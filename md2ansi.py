#!/usr/bin/env python3
"""
md2ansi: Convert Markdown to ANSI-colored text in the terminal with basic
         support for headings, lists, blockquotes, fenced code blocks, inline
         formatting, horizontal rules, and simple pipe-delimited tables.

Usage:
  md2ansi [file1.md [file2.md ...]] [options]
  cat README.md | md2ansi

Examples:
  md2ansi file1.md file2.md
  cat README.md | md2ansi
"""

import sys
import re
import shutil
import argparse
import signal

# --------------------------------------------------------------------
# ANSI escape sequences
# 2-space indentation in code
ANSI_RESET = "\x1b[0m"
ANSI_BOLD = "\x1b[1m"
ANSI_DIM = "\x1b[2m"
ANSI_STRIKE = "\x1b[9m"

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

# --------------------------------------------------------------------
def sigint_handler(signum, frame):
  """Handle Ctrl-C gracefully."""
  print("\nInterrupted by user.")
  sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

# --------------------------------------------------------------------
def get_terminal_width():
  """
  Get terminal width using multiple methods with fallbacks.
  Returns a reasonable default (80) if all methods fail.
  """
  try:
    # Method 1: Using stty
    import subprocess
    result = subprocess.run(['stty', 'size'],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    if result.returncode == 0:
      rows, columns = map(int, result.stdout.decode().split())
      if columns > 0:
        return columns

    # Method 2: Using shutil (but only if we're connected to a real terminal)
    import os
    if os.isatty(1):  # 1 is stdout
      size = shutil.get_terminal_size()
      if size.columns > 0:
        return size.columns

    # Method 3: Environment variable
    if 'COLUMNS' in os.environ:
      try:
        columns = int(os.environ['COLUMNS'])
        if columns > 0:
          return columns
      except ValueError:
        pass

  except Exception:
    pass

  # Fallback to standard 80 columns
  return 80

# --------------------------------------------------------------------
def colorize_line(line):
  """
  Apply inline transformations:
    - Bold (**) -> ANSI_BOLD
    - Italic (*) -> ANSI_DIM (as an example)
    - Strikethrough (~~)
    - Inline code (`code`)
  """
  # Bold: **text**
  line = re.sub(r"\*\*(.+?)\*\*", rf"{ANSI_BOLD}\1{ANSI_RESET}{COLOR_TEXT}", line)
  # Italics: *text*
  line = re.sub(r"\*(.+?)\*", rf"{ANSI_DIM}\1{ANSI_RESET}{COLOR_TEXT}", line)
  # Strikethrough: ~~text~~
  line = re.sub(r"~~(.+?)~~", rf"{ANSI_STRIKE}\1{ANSI_RESET}{COLOR_TEXT}", line)

  # Inline code: `code`
  def replace_code(match):
    inside = match.group(1)
    return f"{ANSI_DIM}{inside}{ANSI_RESET}{COLOR_TEXT}"

  line = re.sub(r"`([^`]+)`", replace_code, line)

  return line

# --------------------------------------------------------------------
def wrap_text(line, width=80):
  """
  Basic wrap by splitting on spaces. Expand or remove if desired.
  """
  words = line.split()
  if not words:
    return [""]
  lines = []
  current = words[0]
  for w in words[1:]:
    if len(current) + len(w) + 1 <= width:
      current += " " + w
    else:
      lines.append(current)
      current = w
  lines.append(current)
  return lines

# --------------------------------------------------------------------
def parse_table(lines, start_index):
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

def build_table_ansi(table_lines, term_width=80):
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
  if len(rows) > 1 and re.match(r"^-{3,}", rows[1][0]):
    # This is presumably the alignment row
    has_alignment_row = True
    for cell in rows[1]:
      cell = cell.lower()
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
  col_widths = [0] * num_cols
  for r in data_rows:
    for i, cell in enumerate(r):
      col_widths[i] = max(col_widths[i], len(cell))

  # Fallback alignment if needed
  while len(alignment) < num_cols:
    alignment.append('left')

  # Build horizontal divider
  horizontal = "+"
  for w in col_widths:
    horizontal += "-" * (w + 2) + "+"

  # Produce lines
  rendered_lines = []
  rendered_lines.append(COLOR_TABLE + horizontal + ANSI_RESET)
  for row_i, row in enumerate(data_rows):
    line_builder = "|"
    for col_i, cell in enumerate(row):
      cell_text = cell
      # align cell
      w = col_widths[col_i]
      if alignment[col_i] == 'right':
        cell_text = cell_text.rjust(w)
      elif alignment[col_i] == 'center':
        left_spaces = (w - len(cell_text)) // 2
        right_spaces = w - len(cell_text) - left_spaces
        cell_text = (" " * left_spaces) + cell_text + (" " * right_spaces)
      else:
        # left
        cell_text = cell_text.ljust(w)
      line_builder += f" {cell_text} |"

    rendered_lines.append(COLOR_TABLE + line_builder + ANSI_RESET)
    if row_i == 0:  # after header, insert horizontal again
      rendered_lines.append(COLOR_TABLE + horizontal + ANSI_RESET)
  rendered_lines.append(COLOR_TABLE + horizontal + ANSI_RESET)

  return rendered_lines

# --------------------------------------------------------------------
def md2ansi(lines, term_width=80):
  """
  Convert Markdown lines to ANSI-colored lines, yielding lines to print.
  We detect blocks (tables, code blocks) and process them accordingly.
  """
  in_code_block = False
  code_fence = None
  i = 0
  while i < len(lines):
    original_line = lines[i]
    line = original_line.rstrip("\n")

    # Detect fenced code blocks
    if re.match(r"^(```|~~~)", line):
      if in_code_block:
        # closing fence
        in_code_block = False
        yield f"{COLOR_CODEBLOCK}{code_fence}{ANSI_RESET}{COLOR_TEXT}"
        i += 1
        continue
      else:
        # opening fence
        in_code_block = True
        code_fence = line[:3]
        yield f"{COLOR_CODEBLOCK}{code_fence}{ANSI_RESET}{COLOR_TEXT}"
        i += 1
        continue

    if in_code_block:
      yield f"{COLOR_CODEBLOCK}{line}{ANSI_RESET}"
      i += 1
      continue

    # Detect if this is the start of a table
    if re.match(r"^\s*\|", line):
      table_block, next_i = parse_table(lines, i)
      # Build the table
      table_ansi = build_table_ansi(table_block, term_width=term_width)
      for row_str in table_ansi:
        yield row_str
      i = next_i
      continue

    # Horizontal rules: --- / === / ___
    if re.match(r"^(\-{3,}|={3,}|_{3,})\s*$", line):
      yield COLOR_HR + ("─" * (term_width - 1)) + ANSI_RESET
      i += 1
      continue

    # Blockquotes: lines starting with >
    if re.match(r"^\s*>", line):
      content = re.sub(r"^\s*> ?", "", line)
      content_wrapped = wrap_text(content, term_width - 4)
      for wrapped_segment in content_wrapped:
        yield (f"{COLOR_TEXT}  > {COLOR_BLOCKQUOTE}"
               f"{wrapped_segment}{ANSI_RESET}{COLOR_TEXT}")
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
      yield f"{color}{text}{ANSI_RESET}{COLOR_TEXT}"
      i += 1
      continue

    # Unordered lists: lines starting with '-' or '*'
    if re.match(r"^\s*[\-\*]\s+", line):
      item_content = re.sub(r"^\s*[\-\*]\s+", "", line)
      item_content = colorize_line(item_content)
      segments = wrap_text(item_content, term_width - 4)
      yield f"  {COLOR_LIST}* {COLOR_TEXT}{segments[0]}"
      for seg in segments[1:]:
        yield f"    {seg}"
      i += 1
      continue

    # Otherwise, normal text. Apply inline expansions and wrap.
    line_colored = colorize_line(line)
    for seg in wrap_text(line_colored, term_width):
      yield seg

    i += 1

# --------------------------------------------------------------------
def main():
  parser = argparse.ArgumentParser(
    description="Convert Markdown to ANSI-colored text in the terminal."
  )
  parser.add_argument(
    "files", nargs="*", default=[],
    help="Markdown files to process; reads from stdin if none are provided."
  )
  parser.add_argument(
    "--width", type=int,
    help="Force specific terminal width (default: auto-detect)"
  )
  args = parser.parse_args()

  # Use specified width or auto-detect
  term_width = args.width if args.width else get_terminal_width()

  if args.files:
    all_lines = []
    for fname in args.files:
      try:
        with open(fname, "r", encoding="utf-8") as f:
          all_lines.extend(f.readlines())
      except FileNotFoundError:
        sys.stderr.write(f"ERROR: '{fname}' not found.\n")
        sys.exit(1)
    for line in md2ansi(all_lines, term_width=term_width):
      print(line)
  else:
    # Read from stdin
    data = sys.stdin.read()
    all_lines = data.splitlines()
    for line in md2ansi(all_lines, term_width=term_width):
      print(line)

# --------------------------------------------------------------------
if __name__ == "__main__":
  main()
