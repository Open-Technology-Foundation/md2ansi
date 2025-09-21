#!/usr/bin/env python3
"""
md2ansi: Convert Markdown to ANSI-colored text in the terminal

A zero-dependency Markdown to ANSI formatter that renders markdown files with
color and style directly in your terminal. Supports headers, lists, tables,
code blocks with syntax highlighting, and more.

Usage:
  md2ansi [file1.md [file2.md ...]] [options]
  cat README.md | md2ansi
  curl -s https://example.com/README.md | md2ansi

Examples:
  md2ansi README.md                    # View a single file
  md2ansi *.md                         # View multiple files
  cat doc.md | md2ansi                 # Process from stdin
  md2ansi --width 100 README.md        # Force specific width
  md2ansi --no-tables doc.md           # Disable table formatting
  md2ansi --plain README.md            # Plain text mode

Security:
  - Files larger than 10MB are rejected for safety
  - Input from stdin is also limited to 10MB
  - ANSI escape sequences in input are sanitized

Version: 0.9.6
License: GPL-3.0
"""

import sys
import re
import shutil
import argparse
import signal
import threading
import time
import multiprocessing
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Callable, Any

# Global debug mode flag
DEBUG_MODE = False

# Maximum sizes for regex operations to prevent ReDoS
MAX_REGEX_INPUT_SIZE = 100000  # 100KB limit for regex input
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB for files

# --------------------------------------------------------------------
# Debug functionality
def debug_print(message: str, level: str = "INFO") -> None:
  """Print debug messages when debug mode is active."""
  if DEBUG_MODE:
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [{level}] {message}", file=sys.stderr)

# --------------------------------------------------------------------
# Safe regex execution with timeout protection
class RegexTimeout(Exception):
  """Exception raised when regex operation times out."""
  pass

def _regex_sub_worker(pattern: str, replacement: str, text: str, flags: int, queue: multiprocessing.Queue):
  """Worker function for regex substitution in subprocess."""
  import re  # Import here since this runs in a separate process
  try:
    # Only use string replacement, not callable replacement in subprocess
    result = re.sub(pattern, replacement, text, flags=flags)
    queue.put(('success', result))
  except Exception as e:
    queue.put(('error', str(e)))

def safe_regex_sub(
  pattern: str,
  replacement: Any,
  text: str,
  flags: int = 0,
  timeout: float = 1.0,
  max_size: int = MAX_REGEX_INPUT_SIZE
) -> str:
  """
  Safely execute regex substitution with timeout and size limits.

  Args:
    pattern: Regex pattern to match
    replacement: Replacement string or function
    text: Text to search in
    flags: Regex flags
    timeout: Maximum time in seconds for regex operation
    max_size: Maximum allowed input size

  Returns:
    Modified text after substitution

  Raises:
    ValueError: If input is too large
    RegexTimeout: If operation takes too long
  """
  # Check input size to prevent excessive memory usage
  if len(text) > max_size:
    debug_print(f"Input too large for regex: {len(text)} > {max_size}", "WARNING")
    raise ValueError(f"Input too large for regex operation: {len(text)} bytes exceeds {max_size} bytes limit")

  debug_print(f"Safe regex sub: pattern length={len(pattern)}, text length={len(text)}", "DEBUG")

  # For simple patterns, execute directly
  if len(pattern) < 50 and not any(c in pattern for c in ['*', '+', '{', '?']):
    try:
      return re.sub(pattern, replacement, text, flags=flags)
    except Exception as e:
      debug_print(f"Regex failed: {e}", "ERROR")
      raise

  # For complex patterns that might cause ReDoS, use subprocess with timeout
  # This provides true process isolation and termination capability
  try:
    # If replacement is callable, we can't use subprocess easily
    # Fall back to direct execution with risk warning
    if callable(replacement):
      debug_print("Warning: Callable replacement cannot use subprocess protection", "WARNING")
      return re.sub(pattern, replacement, text, flags=flags)

    # Use multiprocessing for true timeout capability
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(
      target=_regex_sub_worker,
      args=(pattern, replacement, text, flags, queue)
    )
    process.start()
    process.join(timeout)

    if process.is_alive():
      debug_print(f"Regex timeout after {timeout}s for pattern: {pattern[:50]}...", "WARNING")
      process.terminate()
      process.join(0.5)  # Give it time to terminate
      if process.is_alive():
        process.kill()  # Force kill if needed
        process.join()
      raise RegexTimeout(f"Regex operation timed out after {timeout} seconds")

    # Check if we got a result
    if not queue.empty():
      status, data = queue.get_nowait()
      if status == 'success':
        return data
      else:
        raise RuntimeError(f"Regex error: {data}")
    else:
      # Process ended without putting result
      raise RuntimeError("Regex process ended without result")

  except RegexTimeout:
    raise
  except Exception as e:
    debug_print(f"Regex subprocess failed, falling back: {e}", "WARNING")
    # Fall back to direct execution as last resort
    try:
      return re.sub(pattern, replacement, text, flags=flags)
    except Exception as e2:
      debug_print(f"Regex fallback also failed: {e2}", "ERROR")
      raise

def _regex_match_worker(pattern: str, text: str, flags: int, queue: multiprocessing.Queue):
  """Worker function for regex matching in subprocess."""
  import re  # Import here since this runs in a separate process
  try:
    match = re.match(pattern, text, flags=flags)
    # Can't pickle Match objects, so extract the needed info
    if match:
      queue.put(('success', {'found': True, 'group': match.group(0), 'groups': match.groups()}))
    else:
      queue.put(('success', {'found': False}))
  except Exception as e:
    queue.put(('error', str(e)))

def safe_regex_match(
  pattern: str,
  text: str,
  flags: int = 0,
  timeout: float = 1.0
) -> Optional[re.Match]:
  """Safely execute regex match with timeout protection."""
  if len(text) > MAX_REGEX_INPUT_SIZE:
    debug_print(f"Input too large for regex match: {len(text)}", "WARNING")
    return None

  # For simple patterns, execute directly
  if len(pattern) < 50 and not any(c in pattern for c in ['*', '+', '{', '?']):
    try:
      return re.match(pattern, text, flags=flags)
    except Exception as e:
      debug_print(f"Regex match failed: {e}", "ERROR")
      return None

  # Use multiprocessing for complex patterns
  try:
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(
      target=_regex_match_worker,
      args=(pattern, text, flags, queue)
    )
    process.start()
    process.join(timeout)

    if process.is_alive():
      debug_print(f"Regex match timeout for pattern: {pattern[:50]}...", "WARNING")
      process.terminate()
      process.join(0.5)
      if process.is_alive():
        process.kill()
        process.join()
      return None

    # Get result from queue
    if not queue.empty():
      status, data = queue.get_nowait()
      if status == 'success':
        if data['found']:
          # Create a simple match-like object for compatibility
          # Note: This won't have all Match methods but has the basic ones
          class SimpleMatch:
            def __init__(self, group0, groups):
              self._group0 = group0
              self._groups = groups
            def group(self, n=0):
              return self._group0 if n == 0 else (self._groups[n-1] if n <= len(self._groups) else None)
            def groups(self):
              return self._groups
          return SimpleMatch(data['group'], data.get('groups', ()))
        else:
          return None
      else:
        debug_print(f"Regex match error: {data}", "ERROR")
        return None
    else:
      return None

  except Exception as e:
    debug_print(f"Regex match subprocess failed, falling back: {e}", "WARNING")
    # Fall back to direct execution
    try:
      return re.match(pattern, text, flags=flags)
    except:
      return None

# --------------------------------------------------------------------
# ANSI escape sequences
# 2-space indentation in code
ANSI_RESET = "\x1b[0m"
ANSI_BOLD = "\x1b[1m"
ANSI_DIM = "\x1b[2m"
ANSI_ITALIC = "\x1b[3m"  # Added italic style
ANSI_STRIKE = "\x1b[9m"
ANSI_UNDERLINE = "\x1b[4m"  # Underline for links

COLOR_H1 = "\x1b[38;5;226m"
COLOR_H2 = "\x1b[38;5;214m"
COLOR_H3 = "\x1b[38;5;118m"
COLOR_H4 = "\x1b[38;5;21m"
COLOR_H5 = "\x1b[38;5;93m"
COLOR_H6 = "\x1b[38;5;239m"
COLOR_TEXT = "\x1b[38;5;7m"
COLOR_BLOCKQUOTE = "\x1b[48;5;236m"
COLOR_CODEBLOCK = "\x1b[90m"
COLOR_LIST = "\x1b[36m"
COLOR_HR = "\x1b[36m"
COLOR_TABLE = "\x1b[90m"
COLOR_LINK = "\x1b[38;5;45m"  # Cyan-blue color for links

# Syntax highlighting colors for code blocks
COLOR_KEYWORD = "\x1b[38;5;204m"  # Pink for keywords
COLOR_STRING = "\x1b[38;5;114m"   # Green for strings
COLOR_NUMBER = "\x1b[38;5;220m"   # Yellow for numbers
COLOR_COMMENT = "\x1b[38;5;245m"  # Gray for comments
COLOR_FUNCTION = "\x1b[38;5;81m"  # Blue for function names
COLOR_CLASS = "\x1b[38;5;214m"    # Orange for class names
COLOR_BUILTIN = "\x1b[38;5;147m"  # Purple for built-in functions

# Simple syntax highlighting rules for common languages
SYNTAX_RULES = {
  "python": {
    "keywords": [
      "and", "as", "assert", "async", "await", "break", "class", "continue", 
      "def", "del", "elif", "else", "except", "False", "finally", "for", 
      "from", "global", "if", "import", "in", "is", "lambda", "None", 
      "nonlocal", "not", "or", "pass", "raise", "return", "True", "try", 
      "while", "with", "yield"
    ],
    "builtins": [
      "abs", "all", "any", "bin", "bool", "bytearray", "bytes", "callable",
      "chr", "classmethod", "compile", "complex", "delattr", "dict", "dir",
      "divmod", "enumerate", "eval", "exec", "filter", "float", "format",
      "frozenset", "getattr", "globals", "hasattr", "hash", "help", "hex",
      "id", "input", "int", "isinstance", "issubclass", "iter", "len", "list",
      "locals", "map", "max", "min", "next", "object", "oct", "open", "ord",
      "pow", "print", "property", "range", "repr", "reversed", "round", "set",
      "setattr", "slice", "sorted", "staticmethod", "str", "sum", "super",
      "tuple", "type", "vars", "zip"
    ],
    "string_patterns": [r'"""(?:.|\n)*?"""', r"'''(?:.|\n)*?'''", r'"[^"\n]*"', r"'[^'\n]*'"],
    "comment_patterns": [r"#.*$"],
    "number_patterns": [r"\b\d+\b", r"\b\d+\.\d+\b"],
    "function_patterns": [r"def\s+(\w+)\s*\("],
    "class_patterns": [r"class\s+(\w+)\s*[\(:]"]
  },
  "javascript": {
    "keywords": [
      "break", "case", "catch", "class", "const", "continue", "debugger", 
      "default", "delete", "do", "else", "export", "extends", "false", 
      "finally", "for", "function", "if", "import", "in", "instanceof", 
      "new", "null", "return", "super", "switch", "this", "throw", "true", 
      "try", "typeof", "var", "void", "while", "with", "yield", "let", "static", 
      "await", "async"
    ],
    "builtins": [
      "Array", "Boolean", "Date", "Error", "Function", "JSON", "Math",
      "Number", "Object", "RegExp", "String", "console", "document",
      "window", "fetch", "setTimeout", "setInterval", "Promise"
    ],
    "string_patterns": [r'"[^"\n]*"', r"'[^'\n]*'", r"`(?:.|\n)*?`"],
    "comment_patterns": [r"//.*$", r"/\*(?:.|\n)*?\*/"],
    "number_patterns": [r"\b\d+\b", r"\b\d+\.\d+\b"],
    "function_patterns": [r"function\s+(\w+)\s*\(", r"(\w+)\s*=\s*function\s*\(", r"(\w+)\s*:\s*function\s*\("],
    "class_patterns": [r"class\s+(\w+)\s*[\{:]"]
  },
  "bash": {
    "keywords": [
      "if", "then", "else", "elif", "fi", "case", "esac", "for", "while", 
      "until", "do", "done", "in", "function", "time", "select", "break", 
      "continue", "return", "declare", "readonly", "local", "export", "set", 
      "unset", "shift", "exit", "trap"
    ],
    "builtins": [
      "echo", "printf", "read", "cd", "pwd", "pushd", "popd", "mkdir", "rmdir",
      "rm", "cp", "mv", "ln", "ls", "cat", "grep", "sed", "awk", "find", "test",
      "source", "eval", "exec", "ulimit", "umask", "wait", "kill", "sleep"
    ],
    "string_patterns": [r'"[^"\n]*"', r"'[^'\n]*'"],
    "comment_patterns": [r"(^|\s)#.*$"],
    "number_patterns": [r"\b\d+\b"],
    "function_patterns": [r"(\w+)\s*\(\)\s*\{", r"function\s+(\w+)\s*\{"],
    "class_patterns": []
  }
}

# Pre-compile regex patterns for syntax highlighting (performance optimization)
COMPILED_SYNTAX_RULES = {}
for lang, rules in SYNTAX_RULES.items():
  COMPILED_SYNTAX_RULES[lang] = {
    'keywords': [re.compile(r'\b' + re.escape(kw) + r'\b') for kw in rules['keywords']],
    'builtins': [re.compile(r'\b' + re.escape(bi) + r'\b') for bi in rules['builtins']],
    'string_patterns': [re.compile(pattern, re.MULTILINE) for pattern in rules['string_patterns']],
    'comment_patterns': [re.compile(pattern, re.MULTILINE) for pattern in rules['comment_patterns']],
    'number_patterns': [re.compile(pattern) for pattern in rules['number_patterns']],
    'function_patterns': [re.compile(pattern, re.MULTILINE) for pattern in rules['function_patterns']],
    'class_patterns': [re.compile(pattern, re.MULTILINE) for pattern in rules.get('class_patterns', [])]
  }

# Pre-compile ANSI stripping pattern for performance
ANSI_STRIP_PATTERN = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')

# --------------------------------------------------------------------
def sigint_handler(signum, frame):
  """Handle Ctrl-C gracefully."""
  print(f"{ANSI_RESET}\nInterrupted by user.")
  sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

# --------------------------------------------------------------------
def sanitize_code(code: str) -> str:
  """
  Remove or escape ANSI patterns and other problematic sequences.
  """
  debug_print(f"Sanitizing code, length: {len(code)}", "DEBUG")
  
  # Remove any existing ANSI escape sequences
  try:
    code = safe_regex_sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', code)
  except (RegexTimeout, ValueError) as e:
    debug_print(f"Failed to sanitize ANSI sequences: {e}", "WARNING")
    # Fallback to simple replacement
    code = code.replace('\x1b[', 'ESC[')
  
  # Fix common problematic ANSI-like patterns in code
  code = code.replace("\\x1b", "ESC_SEQ")
  
  # Special handling for patterns that look like ANSI color codes
  try:
    code = safe_regex_sub(r'\[([0-9]{1,2}(;[0-9]{1,2})*m)', r'[ANSI_CODE\1', code)
    code = safe_regex_sub(r'\[38;5;[0-9]+m', r'[COLOR_CODE]', code)
  except (RegexTimeout, ValueError) as e:
    debug_print(f"Failed to sanitize color codes: {e}", "WARNING")
  
  return code

def highlight_code(code: str, language: str) -> str:
  """
  Apply syntax highlighting to code based on language rules.
  Returns the code with ANSI escape sequences for syntax highlighting.
  """
  # Default to plain text if language not supported
  language = language.lower().strip()
  
  # Common language aliases
  lang_map = {
    "js": "javascript",
    "py": "python",
    "sh": "bash",
    "shell": "bash",
  }
  
  # Map language to supported language if possible
  if language in lang_map:
    language = lang_map[language]
  
  # If language not supported, return plain code
  if language not in COMPILED_SYNTAX_RULES:
    return code

  # Sanitize the code to prevent issues with ANSI sequences
  code = sanitize_code(code)

  # Use pre-compiled patterns for better performance
  compiled_rules = COMPILED_SYNTAX_RULES[language]
  highlighted_code = code

  # Process comments first (they have highest priority)
  for pattern in compiled_rules["comment_patterns"]:
    highlighted_code = pattern.sub(
      lambda m: f"{COLOR_COMMENT}{m.group(0)}{COLOR_CODEBLOCK}",
      highlighted_code
    )

  # Then strings (second highest priority)
  for pattern in compiled_rules["string_patterns"]:
    highlighted_code = pattern.sub(
      lambda m: f"{COLOR_STRING}{m.group(0)}{COLOR_CODEBLOCK}",
      highlighted_code
    )

  # Then numbers
  for pattern in compiled_rules["number_patterns"]:
    highlighted_code = pattern.sub(
      lambda m: f"{COLOR_NUMBER}{m.group(0)}{COLOR_CODEBLOCK}",
      highlighted_code
    )

  # Then functions (match function definitions)
  for pattern in compiled_rules["function_patterns"]:
    try:
      highlighted_code = pattern.sub(
        lambda m: m.group(0).replace(m.group(1), f"{COLOR_FUNCTION}{m.group(1)}{COLOR_CODEBLOCK}"),
        highlighted_code
      )
    except (IndexError, AttributeError) as e:
      # Skip if there's an issue with replacement
      debug_print(f"Function pattern error: {e}", "WARNING")
      pass

  # Then classes (match class definitions)
  for pattern in compiled_rules["class_patterns"]:
    try:
      highlighted_code = pattern.sub(
        lambda m: m.group(0).replace(m.group(1), f"{COLOR_CLASS}{m.group(1)}{COLOR_CODEBLOCK}"),
        highlighted_code
      )
    except (IndexError, AttributeError) as e:
      # Skip if there's an issue with replacement
      debug_print(f"Class pattern error: {e}", "WARNING")
      pass

  # Then keywords (important to do after function patterns)
  for pattern in compiled_rules["keywords"]:
    highlighted_code = pattern.sub(
      lambda m: f"{COLOR_KEYWORD}{m.group(0)}{COLOR_CODEBLOCK}",
      highlighted_code
    )

  # Finally builtins
  for pattern in compiled_rules["builtins"]:
    highlighted_code = pattern.sub(
      lambda m: f"{COLOR_BUILTIN}{m.group(0)}{COLOR_CODEBLOCK}",
      highlighted_code
    )
    
  return highlighted_code

# --------------------------------------------------------------------
def get_terminal_width() -> int:
  """
  Get terminal width using multiple methods with fallbacks.
  Returns a reasonable default (80) if all methods fail.
  """
  debug_print("Getting terminal width", "DEBUG")
  
  try:
    # Method 1: Using shutil (but only if we're connected to a real terminal)
    import os
    if os.isatty(1):  # 1 is stdout
      size = shutil.get_terminal_size()
      if size.columns > 0:
        debug_print(f"Terminal width from shutil: {size.columns}", "DEBUG")
        # Validate reasonable bounds
        return min(max(size.columns, 20), 500)

    # Method 2: Using stty
    import subprocess
    result = subprocess.run(['stty', 'size'],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    if result.returncode == 0:
      rows, columns = map(int, result.stdout.decode().split())
      if columns > 0:
        debug_print(f"Terminal width from stty: {columns}", "DEBUG")
        return min(max(columns, 20), 500)

    # Method 3: Environment variable
    if 'COLUMNS' in os.environ:
      try:
        columns = int(os.environ['COLUMNS'])
        if columns > 0:
          debug_print(f"Terminal width from COLUMNS env: {columns}", "DEBUG")
          return min(max(columns, 20), 500)
      except ValueError:
        pass

  except Exception as e:
    debug_print(f"Error getting terminal width: {e}", "WARNING")

  # Fallback to standard 80 columns
  debug_print("Using default terminal width: 80", "DEBUG")
  return 80

# --------------------------------------------------------------------
def colorize_line(line: str, options: Dict = None) -> str:
  """
  Apply inline transformations:
    - Bold (**) -> ANSI_BOLD
    - Italic (*) -> ANSI_ITALIC
    - Strikethrough (~~)
    - Inline code (`code`)
    - Links: [text](url)
    - Images: ![alt](url)
    - Footnote references: [^id]
  
  Args:
    line: The text line to process
    options: Dictionary of feature flags to enable/disable features
  """
  # Default options if none provided
  if options is None:
    options = {
      "footnotes": True,
      "syntax_highlighting": True,
      "tables": True,
      "task_lists": True,
      "images": True,
      "links": True
    }
  # We need to be careful with the order of replacements to avoid conflicts
  
  # Inline code: `code` (do this first to avoid conflicts with other formatting)
  def replace_code(match):
    inside = match.group(1)
    return f"{COLOR_CODEBLOCK}`{inside}`{ANSI_RESET}{COLOR_TEXT}"

  try:
    line = safe_regex_sub(r"`([^`]+)`", replace_code, line)
  except (RegexTimeout, ValueError):
    debug_print("Failed to process inline code", "WARNING")
  
  # Image links: ![alt](url) - must be processed before regular links
  def replace_image(match):
    alt_text = match.group(1)
    url = match.group(2)
    # Create a placeholder for the image with alt text
    return f"{ANSI_BOLD}[IMG: {alt_text}]{ANSI_RESET}{COLOR_TEXT}"

  if options.get("images", True):
    try:
      line = safe_regex_sub(r"!\[([^\]]+)\]\(([^)]+)\)", replace_image, line)
    except (RegexTimeout, ValueError):
      debug_print("Failed to process image links", "WARNING")
  
  # Links: [text](url) - must be processed before bold and italic to avoid conflicts
  def replace_link(match):
    text = match.group(1)
    url = match.group(2)
    # Process any nested formatting within the link text (for better nested formatting)
    if "**" in text:
      text = safe_regex_sub(r"\*\*(.+?)\*\*", f"{ANSI_BOLD}\\1{ANSI_RESET}{COLOR_LINK}", text)
    if "*" in text and not text.startswith("*") and not text.endswith("*"):
      text = safe_regex_sub(r"(?<!\*)\*([^\*]+)\*(?!\*)", f"{ANSI_ITALIC}\\1{ANSI_RESET}{COLOR_LINK}", text)
    if "~~" in text:
      text = safe_regex_sub(r"~~(.+?)~~", f"{ANSI_STRIKE}\\1{ANSI_RESET}{COLOR_LINK}", text)
    if "`" in text:
      text = safe_regex_sub(r"`([^`]+)`", f"{COLOR_CODEBLOCK}`\\1`{ANSI_RESET}{COLOR_LINK}", text)
    return f"{COLOR_LINK}{ANSI_UNDERLINE}{text}{ANSI_RESET}{COLOR_TEXT}"

  if options.get("links", True):
    try:
      line = safe_regex_sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, line)
    except (RegexTimeout, ValueError):
      debug_print("Failed to process links", "WARNING")
  
  # Better handling of nested formatting
  
  # Combinations of bold+italic: ***text*** or **_text_** or _**text**_
  if "***" in line or "**_" in line or "_**" in line:
    line = re.sub(r"\*\*\*(.+?)\*\*\*", f"{ANSI_BOLD}{ANSI_ITALIC}\\1{ANSI_RESET}{COLOR_TEXT}", line)
    line = re.sub(r"\*\*_(.+?)_\*\*", f"{ANSI_BOLD}{ANSI_ITALIC}\\1{ANSI_RESET}{COLOR_TEXT}", line)
    line = re.sub(r"_\*\*(.+?)\*\*_", f"{ANSI_BOLD}{ANSI_ITALIC}\\1{ANSI_RESET}{COLOR_TEXT}", line)
  
  # Bold: **text**
  if "**" in line:
    line = re.sub(r"\*\*(.+?)\*\*", f"{ANSI_BOLD}\\1{ANSI_RESET}{COLOR_TEXT}", line)
  
  # Italics: *text* (but not if it's part of a list item)
  if "*" in line and not line.startswith("*") and not line.endswith("*"):
    line = re.sub(r"(?<!\*)\*([^\*]+)\*(?!\*)", f"{ANSI_ITALIC}\\1{ANSI_RESET}{COLOR_TEXT}", line)
  
  # Strikethrough: ~~text~~
  if "~~" in line:
    line = re.sub(r"~~(.+?)~~", f"{ANSI_STRIKE}\\1{ANSI_RESET}{COLOR_TEXT}", line)
  
  # Footnote references: [^1], [^note], etc.
  def replace_footnote_ref(match):
    ref = match.group(1)
    # Superscript style for the footnote reference
    return f"{COLOR_TEXT}[{ANSI_BOLD}{ANSI_DIM}^{ref}{ANSI_RESET}{COLOR_TEXT}]"
  
  if options.get("footnotes", True) and "[^" in line:
    line = re.sub(r"\[\^([^\]]+)\]", replace_footnote_ref, line)

  return line

# --------------------------------------------------------------------
def wrap_text(line: str, width: int = 80) -> List[str]:
  """
  Basic wrap by splitting on spaces. Preserves formatting.
  """
  # If line is empty or shorter than width, return as is
  if not line or len(line) <= width:
    return [line]

  words = line.split()
  if not words:
    return [""]

  lines = []
  current = words[0]

  # Pre-calculate visible lengths once for all words (performance optimization)
  visible_words = [(w, ANSI_STRIP_PATTERN.sub('', w)) for w in words]
  current_visible = visible_words[0][1]

  for word, visible_word in visible_words[1:]:
    # Use cached visible lengths
    if len(current_visible) + len(visible_word) + 1 <= width:
      current += " " + word
      current_visible += " " + visible_word
    else:
      lines.append(current)
      current = word
      current_visible = visible_word

  lines.append(current)
  return lines

# --------------------------------------------------------------------
def parse_table(lines: List[str], start_index: int) -> Tuple[List[str], int]:
  """
  Collect consecutive table lines starting at start_index.
  Return (list_of_table_lines, next_index).

  Table lines are recognized if they start with an optional
  whitespace and then a '|' character, e.g.:
    | col1 | col2 | ...
    |------|------| ...
    | data1| data2| ...
  """
  table_lines = []
  i = start_index
  while i < len(lines):
    if re.match(r"^\s*\|", lines[i]):
      table_lines.append(lines[i])
      i += 1
    else:
      break
  return table_lines, i

def build_table_ansi(table_lines: List[str], term_width: int = 80) -> List[str]:
  """
  Given a list of lines representing a Markdown table, parse
  them into cells, then produce an ASCII/ANSI table.
  """
  # Split each line by pipe, ignoring first/last empty columns if present.
  rows = []
  for line in table_lines:
    # Strip trailing newline, remove leading/trailing whitespace, then split
    row_cells = [c.strip() for c in line.strip().strip('|').split('|')]
    rows.append(row_cells)

  # If there's a 'separator row' (usually the 2nd row) that looks like
  # | --- | :---: | etc., gather alignment info. This row won't be printed
  # as data.
  alignment = []
  has_alignment_row = False
  if len(rows) > 1 and all(re.match(r"^:?-+:?$", cell) for cell in rows[1]):
    # This is the alignment row
    has_alignment_row = True
    for cell in rows[1]:
      cell = cell.strip()
      if cell.startswith(':') and cell.endswith(':'):
        alignment.append('center')
      elif cell.endswith(':'):
        alignment.append('right')
      else:
        alignment.append('left')

  # We remove the alignment row from the final data display
  if has_alignment_row:
    data_rows = [rows[0]] + rows[2:]
  else:
    data_rows = rows

  # Determine max column widths
  num_cols = max(len(r) for r in data_rows) if data_rows else 0
  
  # Ensure alignment has an entry for each column, defaulting to 'left'
  # This handles the case where data rows have more columns than the alignment row
  alignment = alignment + ['left'] * (num_cols - len(alignment))
  
  col_widths = [0] * num_cols
  for r in data_rows:
    for i, cell in enumerate(r[:num_cols]):
      col_widths[i] = max(col_widths[i], len(cell))

  # Build horizontal divider
  horizontal = "+"
  for w in col_widths:
    horizontal += "-" * (w + 2) + "+"

  # Produce lines
  rendered_lines = []
  rendered_lines.append(f"{COLOR_TABLE}{horizontal}{ANSI_RESET}")
  
  for row_i, row in enumerate(data_rows):
    line_builder = "|"
    
    # Ensure row has enough cells
    row_padded = row + [""] * (num_cols - len(row))
    
    for col_i, cell in enumerate(row_padded):
      cell_text = cell
      
      # Apply enhanced inline formatting to cell content
      # This ensures proper handling of complex formatting like bold+italic and links
      cell_text = colorize_line(cell_text)
      
      # Get visible length (without ANSI codes)
      visible_text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', cell_text)
      
      # align cell
      w = col_widths[col_i]
      if alignment[col_i] == 'right':
        padding = w - len(visible_text)
        cell_text = " " * padding + cell_text
      elif alignment[col_i] == 'center':
        left_spaces = (w - len(visible_text)) // 2
        right_spaces = w - len(visible_text) - left_spaces
        cell_text = (" " * left_spaces) + cell_text + (" " * right_spaces)
      else:
        # left
        padding = w - len(visible_text)
        cell_text = cell_text + " " * padding
      
      # Ensure we reset formatting at the end of each cell to maintain table structure
      # Add a wrapper that resets to table color at the end
      line_builder += f" {cell_text}{COLOR_TABLE} |"

    rendered_lines.append(f"{COLOR_TABLE}{line_builder}{ANSI_RESET}")
    if row_i == 0 and has_alignment_row:  # after header, insert horizontal again
      rendered_lines.append(f"{COLOR_TABLE}{horizontal}{ANSI_RESET}")
      
  rendered_lines.append(f"{COLOR_TABLE}{horizontal}{ANSI_RESET}")

  return rendered_lines

# --------------------------------------------------------------------
def md2ansi(lines: List[str], term_width: int = 80, options: Dict = None) -> List[str]:
  """
  Convert Markdown lines to ANSI-colored lines, yielding lines to print.
  We detect blocks (tables, code blocks) and process them accordingly.
  
  Args:
    lines: List of markdown text lines
    term_width: Terminal width to wrap text
    options: Dictionary of feature flags to enable/disable features
  """
  # Default options if none provided
  if options is None:
    options = {
      "footnotes": True,
      "syntax_highlighting": True,
      "tables": True,
      "task_lists": True,
      "images": True,
      "links": True
    }
    
  result = []
  in_code_block = False
  code_fence = None
  footnotes = {}  # Format: {id: text}
  footnote_refs = []  # List of footnote ids in order of appearance
  i = 0
  
  while i < len(lines):
    original_line = lines[i]
    line = original_line.rstrip("\n")

    # Detect fenced code blocks
    code_fence_match = re.match(r"^(```|~~~)(.*)$", line)
    if code_fence_match:
      fence = code_fence_match.group(1)
      lang_spec = code_fence_match.group(2).strip()
      
      if in_code_block:
        # closing fence
        in_code_block = False
        code_fence = None  # Reset code fence
        lang = None  # Reset language when exiting block
        result.append(f"{COLOR_CODEBLOCK}{fence}{ANSI_RESET}")
        i += 1
        continue
      else:
        # opening fence
        in_code_block = True
        code_fence = fence
        lang = lang_spec if lang_spec else None  # Store language for the block
        fence_line = f"{COLOR_CODEBLOCK}{fence}"
        if lang:
          fence_line += f" {lang}"
        result.append(f"{fence_line}{ANSI_RESET}")
        i += 1
        continue

    if in_code_block:
      # Store code lines for syntax highlighting
      if lang and options.get("syntax_highlighting", True):
        # First sanitize all ANSI sequences
        clean_line = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', line)
        
        # Special handling based on language
        if lang.lower() in ["bash", "sh", "shell"]:
          # Handle bash comments specially
          if clean_line.strip().startswith("#"):
            # Replace any patterns that look like ANSI codes in comments
            clean_line = re.sub(r'\[([0-9]{1,2}(;[0-9]{1,2})*m)', r'[\1]', clean_line)
            clean_line = re.sub(r'\[38;5;[0-9]+m', r'[color]', clean_line)
            result.append(f"{COLOR_COMMENT}{clean_line}{ANSI_RESET}")
          else:
            # Basic highlighting for bash command lines
            for builtin in SYNTAX_RULES["bash"]["builtins"]:
              pattern = r'\b' + re.escape(builtin) + r'\b'
              clean_line = re.sub(pattern, f"{COLOR_BUILTIN}\\g<0>{COLOR_CODEBLOCK}", clean_line)
            result.append(f"{COLOR_CODEBLOCK}{clean_line}{ANSI_RESET}")
        
        elif lang.lower() in ["python", "py"]:
          # Handle Python comments
          if clean_line.strip().startswith("#"):
            clean_line = re.sub(r'\[([0-9]{1,2}(;[0-9]{1,2})*m)', r'[\1]', clean_line)
            result.append(f"{COLOR_COMMENT}{clean_line}{ANSI_RESET}")
          # Handle Python docstrings
          elif '"""' in clean_line or "'''" in clean_line:
            clean_line = re.sub(r'\[([0-9]{1,2}(;[0-9]{1,2})*m)', r'[\1]', clean_line)
            result.append(f"{COLOR_STRING}{clean_line}{ANSI_RESET}")
          else:
            # Basic highlighting for other Python lines
            for keyword in SYNTAX_RULES["python"]["keywords"]:
              pattern = r'\b' + re.escape(keyword) + r'\b'
              clean_line = re.sub(pattern, f"{COLOR_KEYWORD}\\g<0>{COLOR_CODEBLOCK}", clean_line)
            for builtin in SYNTAX_RULES["python"]["builtins"]:
              pattern = r'\b' + re.escape(builtin) + r'\b'
              clean_line = re.sub(pattern, f"{COLOR_BUILTIN}\\g<0>{COLOR_CODEBLOCK}", clean_line)
            result.append(f"{COLOR_CODEBLOCK}{clean_line}{ANSI_RESET}")
            
        else:
          # For all other languages, just use basic code coloring
          result.append(f"{COLOR_CODEBLOCK}{clean_line}{ANSI_RESET}")
      else:
        # No language specified or syntax highlighting disabled, use default color
        clean_line = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', line)
        result.append(f"{COLOR_CODEBLOCK}{clean_line}{ANSI_RESET}")
      i += 1
      continue

    # Detect if this is the start of a table
    if re.match(r"^\s*\|", line) and options.get("tables", True):
      table_block, next_i = parse_table(lines, i)
      # Build the table
      table_ansi = build_table_ansi(table_block, term_width=term_width)
      result.extend(table_ansi)
      i = next_i
      continue
    elif re.match(r"^\s*\|", line):
      # Tables are disabled but we found what looks like a table
      # Just format as plain text with basic formatting
      line_colored = f"{COLOR_TEXT}{colorize_line(line, options)}"
      segments = wrap_text(line_colored, term_width)
      result.extend(segments)
      i += 1
      continue

    # Horizontal rules: --- / === / ___
    if re.match(r"^(\-{3,}|={3,}|_{3,})\s*$", line):
      result.append(f"{COLOR_HR}{('─' * (term_width - 1))}{ANSI_RESET}")
      i += 1
      continue

    # Blockquotes: lines starting with >
    if re.match(r"^\s*>", line):
      content = re.sub(r"^\s*> ?", "", line)
      content = colorize_line(content, options)
      content_wrapped = wrap_text(content, term_width - 4)
      for wrapped_segment in content_wrapped:
        result.append(f"{COLOR_TEXT}  > {COLOR_BLOCKQUOTE}{wrapped_segment}{ANSI_RESET}")
      i += 1
      continue

    # Headings: #, ##, ...
    heading_match = re.match(r"^(#{1,6})\s+(.*)", line)
    if heading_match:
      hashes = heading_match.group(1)
      text = heading_match.group(2)
      level = len(hashes)
      if level == 1:
        color = COLOR_H1
      elif level == 2:
        color = COLOR_H2
      elif level == 3:
        color = COLOR_H3
      elif level == 4:
        color = COLOR_H4
      elif level == 5:
        color = COLOR_H5
      else:
        color = COLOR_H6
      
      # Apply inline formatting to heading text
      text = colorize_line(text, options)
      result.append(f"{color}{text}{ANSI_RESET}")
      i += 1
      continue

    # Task lists: lines starting with '-' or '*' followed by [ ] or [x]
    task_match = re.match(r"^(\s*)[\-\*]\s+\[([ x])\]\s+(.*)", line)
    if task_match:
      indent = task_match.group(1)
      task_status = task_match.group(2)
      item_content = task_match.group(3)
      
      if options.get("task_lists", True):
        # Process as a task list with checkbox
        item_content = colorize_line(item_content, options)
        
        # Calculate indentation level for nested lists
        indent_level = len(indent) // 2
        bullet_indent = "  " * indent_level
        text_indent = "  " * (indent_level + 1) + "     "  # 5 extra spaces for "[ ] "
        
        # Format checkbox based on status
        if task_status == "x":
          checkbox = f"{COLOR_LIST}[{ANSI_BOLD}x{ANSI_RESET}{COLOR_LIST}]"
        else:
          checkbox = f"{COLOR_LIST}[ ]"
        
        segments = wrap_text(item_content, term_width - len(text_indent) - 2)
        result.append(f"{bullet_indent}{COLOR_LIST}* {checkbox} {COLOR_TEXT}{segments[0]}")
        for seg in segments[1:]:
          result.append(f"{text_indent}{seg}")
      else:
        # Process as a regular list item when task lists are disabled
        # Combine the checkbox and text as part of the list item
        combined_content = f"[{task_status}] {item_content}"
        combined_content = colorize_line(combined_content, options)
        
        # Calculate indentation level for nested lists
        indent_level = len(indent) // 2
        bullet_indent = "  " * indent_level
        text_indent = "  " * (indent_level + 1)
        
        segments = wrap_text(combined_content, term_width - len(text_indent) - 2)
        result.append(f"{bullet_indent}{COLOR_LIST}* {COLOR_TEXT}{segments[0]}")
        for seg in segments[1:]:
          result.append(f"{text_indent}{seg}")
      
      i += 1
      continue
      
    # Unordered lists: lines starting with '-' or '*'
    list_match = re.match(r"^(\s*)[\-\*]\s+(.*)", line)
    if list_match:
      indent = list_match.group(1)
      item_content = list_match.group(2)
      item_content = colorize_line(item_content, options)
      
      # Calculate indentation level for nested lists
      indent_level = len(indent) // 2
      bullet_indent = "  " * indent_level
      text_indent = "  " * (indent_level + 1)
      
      segments = wrap_text(item_content, term_width - len(text_indent) - 2)
      result.append(f"{bullet_indent}{COLOR_LIST}* {COLOR_TEXT}{segments[0]}")
      for seg in segments[1:]:
        result.append(f"{text_indent}{seg}")
      i += 1
      continue
      
    # Ordered lists: lines starting with a number followed by a period
    ordered_list_match = re.match(r"^(\s*)(\d+)\.[ \t]+(.*)", line)
    if ordered_list_match:
      indent = ordered_list_match.group(1)
      number = ordered_list_match.group(2)
      item_content = ordered_list_match.group(3)
      item_content = colorize_line(item_content, options)
      
      # Calculate indentation level for nested lists
      indent_level = len(indent) // 2
      number_indent = "  " * indent_level
      # Add 2 extra spaces for each digit in the number (e.g., "10. " vs "1. ")
      number_width = len(number) + 2  # includes the period and space
      text_indent = "  " * indent_level + " " * number_width
      
      segments = wrap_text(item_content, term_width - len(text_indent) - 2)
      result.append(f"{number_indent}{COLOR_LIST}{number}. {COLOR_TEXT}{segments[0]}")
      for seg in segments[1:]:
        result.append(f"{text_indent}{seg}")
      i += 1
      continue

    # Check for footnote definition: [^1]: Footnote text
    footnote_def_match = re.match(r"^\[\^([^\]]+)\]:\s+(.+)$", line)
    if footnote_def_match and options.get("footnotes", True):
      footnote_id = footnote_def_match.group(1)
      footnote_text = footnote_def_match.group(2)
      
      # Store footnote text for later rendering
      footnotes[footnote_id] = footnote_text
      
      # Add reference if it doesn't exist yet (for definitions without references)
      if footnote_id not in footnote_refs:
        footnote_refs.append(footnote_id)
      
      # Skip this line in the main output
      i += 1
      continue
        
    # Otherwise, normal text. Apply inline expansions and wrap.
    if line.strip():  # Skip empty lines
      # Find footnote references in the line and track them
      refs = re.findall(r"\[\^([^\]]+)\]", line)
      for ref in refs:
        if ref not in footnote_refs:
          footnote_refs.append(ref)
          
      line_colored = f"{COLOR_TEXT}{colorize_line(line, options)}"
      segments = wrap_text(line_colored, term_width)
      result.extend(segments)
    else:
      result.append("")  # Preserve empty lines

    i += 1
    
  # Add footnotes section at the end if footnotes exist
  if footnotes and footnote_refs and options.get("footnotes", True):
    result.append("")  # Add a blank line before footnotes
    result.append(f"{COLOR_H2}Footnotes:{ANSI_RESET}")
    result.append("")
    
    # Render footnotes in order of appearance
    for idx, ref_id in enumerate(footnote_refs):
      if ref_id in footnotes:
        # Format the footnote text with inline formatting
        footnote_text = colorize_line(footnotes[ref_id], options)
        result.append(f"{COLOR_TEXT}[{ANSI_BOLD}{ANSI_DIM}^{ref_id}{ANSI_RESET}{COLOR_TEXT}]: {footnote_text}")
      else:
        # Reference exists but definition doesn't
        result.append(f"{COLOR_TEXT}[{ANSI_BOLD}{ANSI_DIM}^{ref_id}{ANSI_RESET}{COLOR_TEXT}]: Missing footnote definition")

  return result

# --------------------------------------------------------------------
def process_file(filename: Optional[str] = None, term_width: int = 80, options: Dict = None) -> List[str]:
  """
  Process a single file or stdin and return formatted lines.
  
  Args:
    filename: Path to markdown file or None for stdin
    term_width: Terminal width for wrapping
    options: Dictionary of feature flags to enable/disable features
  """
  try:
    if filename:
      try:
        # Check file size before reading
        import os
        file_size = os.path.getsize(filename)
        # Limit to 10MB for safety
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if file_size > max_size:
          return [f"ERROR: File '{filename}' is too large ({file_size:,} bytes). Maximum allowed size is {max_size:,} bytes (10MB)."]
        
        with open(filename, "r", encoding="utf-8") as f:
          content = f.read()
      except FileNotFoundError:
        return [f"ERROR: File '{filename}' not found."]
      except IsADirectoryError:
        return [f"ERROR: '{filename}' is a directory, not a file."]
      except PermissionError:
        return [f"ERROR: Permission denied when trying to read '{filename}'."]
      except UnicodeDecodeError:
        return [f"ERROR: '{filename}' is not a valid UTF-8 text file."]
    else:
      try:
        # Read from stdin with size limit (improved security & accuracy)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        content_bytes = b""

        # Read binary data directly for accurate byte counting
        while True:
          chunk = sys.stdin.buffer.read(8192)  # Read in 8KB chunks as bytes
          if not chunk:
            break
          if len(content_bytes) + len(chunk) > max_size:
            return [f"ERROR: Input from stdin is too large (>{max_size:,} bytes). Maximum allowed size is {max_size:,} bytes (10MB)."]
          content_bytes += chunk

        # Decode once after all data is read, with error handling
        try:
          content = content_bytes.decode('utf-8', errors='replace')
        except UnicodeDecodeError as e:
          debug_print(f"Unicode decode error: {e}", "WARNING")
          content = content_bytes.decode('utf-8', errors='replace')

      except KeyboardInterrupt:
        print(f"{ANSI_RESET}")
        sys.exit(130)  # Standard exit code for SIGINT
      except (IOError, OSError) as e:
        return [f"ERROR: Failed to read from stdin: {str(e)}"]
      except Exception as e:
        return [f"ERROR: Unexpected error reading from stdin: {str(e)}"]
      
    all_lines = content.splitlines()
    
    # Skip shebang line if present on the first line
    if all_lines and all_lines[0].startswith('#!'):
      debug_print(f"Skipping shebang line: {all_lines[0]}", "DEBUG")
      all_lines = all_lines[1:]
    
    return md2ansi(all_lines, term_width=term_width, options=options)
    
  except MemoryError:
    return [f"ERROR: Not enough memory to process {'file' if filename else 'input'}."]
  except Exception as e:
    return [f"ERROR: Unexpected error: {type(e).__name__}: {str(e)}"]

# --------------------------------------------------------------------
def main():
  parser = argparse.ArgumentParser(
    description="Convert Markdown to ANSI-colored text in the terminal.",
    epilog="Security: Files and stdin input are limited to 10MB. "
           "ANSI sequences in input are sanitized. "
           "Visit https://github.com/Open-Technology-Foundation/md2ansi for more info.",
    formatter_class=argparse.RawDescriptionHelpFormatter
  )
  parser.add_argument(
    "files", nargs="*", default=[],
    help="Markdown files to process; reads from stdin if none are provided."
  )
  parser.add_argument(
    "-w", "--width", type=int,
    help="Force specific terminal width (default: auto-detect)"
  )
  parser.add_argument(
    "-V", "--version", action="version", version="0.9.6",
    help="Show version information and exit"
  )
  parser.add_argument(
    "-D", "--debug", action="store_true",
    help="Enable debug mode with detailed execution traces (output to stderr)"
  )
  
  # Feature toggle options
  feature_group = parser.add_argument_group('Feature toggles')
  feature_group.add_argument(
    "--no-footnotes", action="store_true",
    help="Disable footnotes processing"
  )
  feature_group.add_argument(
    "--no-syntax-highlight", action="store_true",
    help="Disable syntax highlighting in code blocks"
  )
  feature_group.add_argument(
    "--no-tables", action="store_true",
    help="Disable tables formatting"
  )
  feature_group.add_argument(
    "--no-task-lists", action="store_true",
    help="Disable task lists (checkboxes) formatting"
  )
  feature_group.add_argument(
    "--no-images", action="store_true",
    help="Disable image placeholders"
  )
  feature_group.add_argument(
    "--no-links", action="store_true",
    help="Disable links formatting"
  )
  feature_group.add_argument(
    "-t", "--plain", action="store_true",
    help="Use plain text mode (disables all formatting features)"
  )
  
  args = parser.parse_args()

  # Enable debug mode if requested
  global DEBUG_MODE
  DEBUG_MODE = args.debug
  
  if DEBUG_MODE:
    debug_print("Debug mode enabled", "INFO")
    debug_print(f"Arguments: {args}", "DEBUG")

  # Use specified width or auto-detect
  term_width = args.width if args.width else get_terminal_width()
  
  # Build options dictionary based on command-line arguments
  options = {
    "footnotes": not (args.no_footnotes or args.plain),
    "syntax_highlighting": not (args.no_syntax_highlight or args.plain),
    "tables": not (args.no_tables or args.plain),
    "task_lists": not (args.no_task_lists or args.plain),
    "images": not (args.no_images or args.plain),
    "links": not (args.no_links or args.plain)
  }
  
  if DEBUG_MODE:
    debug_print(f"Terminal width: {term_width}", "INFO")
    debug_print(f"Options: {options}", "DEBUG")

  # Print initial color reset to ensure terminal is in a clean state
  print(ANSI_RESET, end="")
  
  if args.files:
    for fname in args.files:
      formatted_lines = process_file(fname, term_width, options)
      for line in formatted_lines:
        print(line)
      # Add a newline between files if processing multiple files
      if len(args.files) > 1 and fname != args.files[-1]:
        print()
  else:
    # Read from stdin
    formatted_lines = process_file(None, term_width, options)
    for line in formatted_lines:
      print(line)
      
  # Ensure terminal colors are reset at the end
  print(ANSI_RESET, end="")

# --------------------------------------------------------------------
if __name__ == "__main__":
  main()

#fin
