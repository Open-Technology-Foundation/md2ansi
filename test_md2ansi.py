#!/usr/bin/env python3
"""
Unit tests for md2ansi.py

This test suite covers the core functionality of the md2ansi markdown-to-ANSI converter.
Tests can be run with pytest (if available) or with Python's built-in unittest module.
"""

import sys
import os
import unittest
import re
from unittest.mock import patch, MagicMock
from io import StringIO

# Add parent directory to path to import md2ansi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the module to test
import md2ansi


class TestSafeRegex(unittest.TestCase):
  """Test the safe regex wrapper functions."""
  
  def test_safe_regex_sub_simple(self):
    """Test safe regex substitution with simple pattern."""
    text = "Hello World"
    result = md2ansi.safe_regex_sub(r"World", "Python", text)
    self.assertEqual(result, "Hello Python")
  
  def test_safe_regex_sub_with_groups(self):
    """Test safe regex substitution with capture groups."""
    text = "The price is $100"
    result = md2ansi.safe_regex_sub(r"\$(\d+)", r"€\1", text)
    self.assertEqual(result, "The price is €100")
  
  def test_safe_regex_sub_size_limit(self):
    """Test that safe regex enforces size limits."""
    large_text = "a" * (md2ansi.MAX_REGEX_INPUT_SIZE + 1)
    with self.assertRaises(ValueError):
      md2ansi.safe_regex_sub(r"a", "b", large_text)
  
  def test_safe_regex_match_simple(self):
    """Test safe regex matching."""
    text = "Hello World"
    result = md2ansi.safe_regex_match(r"^Hello", text)
    self.assertIsNotNone(result)
    self.assertEqual(result.group(0), "Hello")
  
  def test_safe_regex_match_no_match(self):
    """Test safe regex matching with no match."""
    text = "Hello World"
    result = md2ansi.safe_regex_match(r"^Goodbye", text)
    self.assertIsNone(result)


class TestSanitizeCode(unittest.TestCase):
  """Test the sanitize_code function."""
  
  def test_removes_ansi_sequences(self):
    """Test that ANSI escape sequences are removed."""
    input_text = "\x1b[31mRed Text\x1b[0m Normal"
    result = md2ansi.sanitize_code(input_text)
    self.assertNotIn("\x1b[31m", result)
    self.assertNotIn("\x1b[0m", result)
  
  def test_escapes_ansi_patterns(self):
    """Test that ANSI-like patterns are escaped."""
    input_text = "Code with \\x1b sequence"
    result = md2ansi.sanitize_code(input_text)
    self.assertIn("ESC_SEQ", result)
    self.assertNotIn("\\x1b", result)
  
  def test_handles_empty_string(self):
    """Test sanitize_code with empty string."""
    result = md2ansi.sanitize_code("")
    self.assertEqual(result, "")
  
  def test_handles_color_code_patterns(self):
    """Test that patterns looking like ANSI codes are handled."""
    input_text = "Array[38;5;123m looks like color"
    result = md2ansi.sanitize_code(input_text)
    # Should be modified to prevent confusion with real ANSI codes
    self.assertIn("COLOR_CODE", result)


class TestGetTerminalWidth(unittest.TestCase):
  """Test the get_terminal_width function."""
  
  @patch('shutil.get_terminal_size')
  @patch('os.isatty')
  def test_terminal_width_from_shutil(self, mock_isatty, mock_get_size):
    """Test getting terminal width from shutil."""
    mock_isatty.return_value = True
    mock_get_size.return_value = MagicMock(columns=120)
    
    result = md2ansi.get_terminal_width()
    self.assertEqual(result, 120)
  
  @patch('os.isatty')
  def test_terminal_width_fallback(self, mock_isatty):
    """Test fallback to default width."""
    mock_isatty.return_value = False
    
    # Should fallback to 80
    result = md2ansi.get_terminal_width()
    self.assertEqual(result, 80)
  
  @patch('shutil.get_terminal_size')
  @patch('os.isatty')
  def test_terminal_width_bounds(self, mock_isatty, mock_get_size):
    """Test that terminal width is bounded."""
    mock_isatty.return_value = True
    
    # Test lower bound
    mock_get_size.return_value = MagicMock(columns=10)
    result = md2ansi.get_terminal_width()
    self.assertEqual(result, 20)  # Minimum is 20
    
    # Test upper bound
    mock_get_size.return_value = MagicMock(columns=1000)
    result = md2ansi.get_terminal_width()
    self.assertEqual(result, 500)  # Maximum is 500


class TestColorizeLine(unittest.TestCase):
  """Test the colorize_line function."""
  
  def test_bold_formatting(self):
    """Test bold text formatting."""
    line = "This is **bold** text"
    result = md2ansi.colorize_line(line)
    self.assertIn(md2ansi.ANSI_BOLD, result)
    self.assertIn("bold", result)
  
  def test_italic_formatting(self):
    """Test italic text formatting."""
    line = "This is *italic* text"
    result = md2ansi.colorize_line(line)
    self.assertIn(md2ansi.ANSI_ITALIC, result)
    self.assertIn("italic", result)
  
  def test_inline_code_formatting(self):
    """Test inline code formatting."""
    line = "Use `print()` function"
    result = md2ansi.colorize_line(line)
    self.assertIn(md2ansi.COLOR_CODEBLOCK, result)
    self.assertIn("`print()`", result)
  
  def test_strikethrough_formatting(self):
    """Test strikethrough formatting."""
    line = "This is ~~deleted~~ text"
    result = md2ansi.colorize_line(line)
    self.assertIn(md2ansi.ANSI_STRIKE, result)
    self.assertIn("deleted", result)
  
  def test_link_formatting(self):
    """Test link formatting."""
    line = "Visit [Google](https://google.com)"
    result = md2ansi.colorize_line(line)
    self.assertIn(md2ansi.COLOR_LINK, result)
    self.assertIn(md2ansi.ANSI_UNDERLINE, result)
    self.assertIn("Google", result)
  
  def test_image_formatting(self):
    """Test image placeholder formatting."""
    line = "![Alt text](image.png)"
    result = md2ansi.colorize_line(line)
    self.assertIn("[IMG: Alt text]", result)
  
  def test_footnote_reference(self):
    """Test footnote reference formatting."""
    line = "This is a footnote[^1] reference"
    result = md2ansi.colorize_line(line)
    self.assertIn("^1", result)
  
  def test_combined_formatting(self):
    """Test combination of bold and italic."""
    line = "This is ***bold and italic*** text"
    result = md2ansi.colorize_line(line)
    self.assertIn(md2ansi.ANSI_BOLD, result)
    self.assertIn(md2ansi.ANSI_ITALIC, result)


class TestWrapText(unittest.TestCase):
  """Test the wrap_text function."""
  
  def test_wrap_short_line(self):
    """Test that short lines are not wrapped."""
    line = "Short line"
    result = md2ansi.wrap_text(line, width=80)
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0], line)
  
  def test_wrap_long_line(self):
    """Test that long lines are wrapped."""
    line = "This is a very long line that definitely exceeds the width limit and should be wrapped"
    result = md2ansi.wrap_text(line, width=30)
    self.assertGreater(len(result), 1)
    for wrapped_line in result:
      # Check visible length without ANSI codes
      visible = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', wrapped_line)
      self.assertLessEqual(len(visible), 30)
  
  def test_wrap_empty_line(self):
    """Test wrapping empty line."""
    result = md2ansi.wrap_text("", width=80)
    self.assertEqual(result, [""])
  
  def test_wrap_preserves_ansi(self):
    """Test that ANSI codes are preserved during wrapping."""
    line = f"{md2ansi.ANSI_BOLD}Bold text that needs wrapping{md2ansi.ANSI_RESET}"
    result = md2ansi.wrap_text(line, width=10)
    # ANSI codes should still be present
    full_result = "".join(result)
    self.assertIn(md2ansi.ANSI_BOLD, full_result)
    self.assertIn(md2ansi.ANSI_RESET, full_result)


class TestParseTable(unittest.TestCase):
  """Test the parse_table function."""
  
  def test_parse_simple_table(self):
    """Test parsing a simple markdown table."""
    lines = [
      "| Header 1 | Header 2 |",
      "|----------|----------|",
      "| Cell 1   | Cell 2   |",
      "",
      "Not a table line"
    ]
    table_lines, next_index = md2ansi.parse_table(lines, 0)
    self.assertEqual(len(table_lines), 3)
    self.assertEqual(next_index, 3)
  
  def test_parse_no_table(self):
    """Test parsing when no table is present."""
    lines = ["Regular text", "More text"]
    table_lines, next_index = md2ansi.parse_table(lines, 0)
    self.assertEqual(len(table_lines), 0)
    self.assertEqual(next_index, 0)


class TestBuildTableAnsi(unittest.TestCase):
  """Test the build_table_ansi function."""
  
  def test_build_simple_table(self):
    """Test building ANSI table from markdown."""
    table_lines = [
      "| Header 1 | Header 2 |",
      "|----------|----------|",
      "| Cell 1   | Cell 2   |"
    ]
    result = md2ansi.build_table_ansi(table_lines)
    
    # Should have borders and content
    self.assertGreater(len(result), 3)
    # Check for table color
    self.assertTrue(any(md2ansi.COLOR_TABLE in line for line in result))
    # Check for horizontal dividers
    self.assertTrue(any("+" in line for line in result))
  
  def test_table_alignment(self):
    """Test table with alignment specifications."""
    table_lines = [
      "| Left | Center | Right |",
      "|:-----|:------:|------:|",
      "| A    | B      | C     |"
    ]
    result = md2ansi.build_table_ansi(table_lines)
    
    # Should process alignment row correctly
    self.assertGreater(len(result), 3)
    # Alignment row should not appear in output
    combined = "\n".join(result)
    self.assertNotIn(":---", combined)


class TestProcessFile(unittest.TestCase):
  """Test the process_file function."""
  
  @patch('builtins.open')
  @patch('os.path.getsize')
  def test_process_small_file(self, mock_getsize, mock_open):
    """Test processing a small markdown file."""
    mock_getsize.return_value = 100  # 100 bytes
    mock_open.return_value.__enter__.return_value.read.return_value = "# Header\n\nParagraph"
    
    result = md2ansi.process_file("test.md")
    
    # Should process without errors
    self.assertIsInstance(result, list)
    self.assertGreater(len(result), 0)
  
  @patch('os.path.getsize')
  def test_process_large_file(self, mock_getsize):
    """Test that large files are rejected."""
    mock_getsize.return_value = md2ansi.MAX_FILE_SIZE + 1
    
    result = md2ansi.process_file("large.md")
    
    # Should return error message
    self.assertEqual(len(result), 1)
    self.assertIn("too large", result[0])
  
  @patch('sys.stdin')
  def test_process_stdin(self, mock_stdin):
    """Test processing from stdin."""
    mock_stdin.read.return_value = "# Header from stdin"
    
    result = md2ansi.process_file(None)
    
    # Should process stdin content
    self.assertIsInstance(result, list)
    self.assertGreater(len(result), 0)


class TestDebugMode(unittest.TestCase):
  """Test debug mode functionality."""
  
  def test_debug_print_disabled(self):
    """Test that debug_print does nothing when disabled."""
    md2ansi.DEBUG_MODE = False
    
    with patch('sys.stderr') as mock_stderr:
      md2ansi.debug_print("Test message")
      mock_stderr.write.assert_not_called()
  
  def test_debug_print_enabled(self):
    """Test that debug_print outputs when enabled."""
    md2ansi.DEBUG_MODE = True
    
    with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
      md2ansi.debug_print("Test message", "INFO")
      output = mock_stderr.getvalue()
      
      # Should contain timestamp, level, and message
      self.assertIn("INFO", output)
      self.assertIn("Test message", output)
    
    # Reset debug mode
    md2ansi.DEBUG_MODE = False


class TestHighlightCode(unittest.TestCase):
  """Test syntax highlighting functionality."""
  
  def test_python_highlighting(self):
    """Test Python code highlighting."""
    code = "def hello():\n    print('Hello')"
    result = md2ansi.highlight_code(code, "python")
    
    # Should contain syntax colors
    self.assertIn(md2ansi.COLOR_KEYWORD, result)  # for 'def'
    self.assertIn(md2ansi.COLOR_BUILTIN, result)  # for 'print'
  
  def test_javascript_highlighting(self):
    """Test JavaScript code highlighting."""
    code = "function test() { console.log('test'); }"
    result = md2ansi.highlight_code(code, "javascript")
    
    # Should contain syntax colors
    self.assertIn(md2ansi.COLOR_KEYWORD, result)  # for 'function'
  
  def test_unsupported_language(self):
    """Test highlighting with unsupported language."""
    code = "some code here"
    result = md2ansi.highlight_code(code, "unknown_lang")
    
    # Should return unchanged
    self.assertEqual(result, code)
  
  def test_language_alias(self):
    """Test language alias mapping."""
    code = "print('test')"
    
    # 'py' should map to 'python'
    result1 = md2ansi.highlight_code(code, "py")
    result2 = md2ansi.highlight_code(code, "python")
    
    # Both should produce same result
    self.assertEqual(result1, result2)


class TestMd2AnsiMain(unittest.TestCase):
  """Test the main md2ansi function."""
  
  def test_process_headers(self):
    """Test markdown header processing."""
    lines = ["# H1", "## H2", "### H3", "#### H4", "##### H5", "###### H6"]
    result = md2ansi.md2ansi(lines)
    
    # Should have different colors for each header level
    self.assertIn(md2ansi.COLOR_H1, result[0])
    self.assertIn(md2ansi.COLOR_H2, result[1])
    self.assertIn(md2ansi.COLOR_H3, result[2])
  
  def test_process_code_blocks(self):
    """Test code block processing."""
    lines = ["```python", "print('hello')", "```"]
    result = md2ansi.md2ansi(lines)
    
    # Should have code block coloring
    self.assertTrue(any(md2ansi.COLOR_CODEBLOCK in line for line in result))
  
  def test_process_lists(self):
    """Test list processing."""
    lines = ["- Item 1", "- Item 2", "1. Numbered item"]
    result = md2ansi.md2ansi(lines)
    
    # Should have list coloring
    self.assertTrue(any(md2ansi.COLOR_LIST in line for line in result))
  
  def test_process_blockquotes(self):
    """Test blockquote processing."""
    lines = ["> This is a quote"]
    result = md2ansi.md2ansi(lines)
    
    # Should have blockquote coloring
    self.assertTrue(any(md2ansi.COLOR_BLOCKQUOTE in line for line in result))
  
  def test_process_horizontal_rules(self):
    """Test horizontal rule processing."""
    lines = ["---", "===", "___"]
    result = md2ansi.md2ansi(lines)
    
    # Should have horizontal rule coloring
    for line in result:
      self.assertIn(md2ansi.COLOR_HR, line)
  
  def test_process_task_lists(self):
    """Test task list processing."""
    lines = ["- [ ] Unchecked", "- [x] Checked"]
    result = md2ansi.md2ansi(lines)
    
    # Should process checkboxes
    combined = "\n".join(result)
    self.assertIn("[ ]", combined)
    self.assertIn("[x]", combined)
  
  def test_process_footnotes(self):
    """Test footnote processing."""
    lines = [
      "Text with footnote[^1]",
      "",
      "[^1]: Footnote text"
    ]
    result = md2ansi.md2ansi(lines)
    
    # Should have footnote section at end
    combined = "\n".join(result)
    self.assertIn("Footnotes:", combined)


def run_tests():
  """Run all tests and return results."""
  # Create test suite
  loader = unittest.TestLoader()
  suite = loader.loadTestsFromModule(sys.modules[__name__])
  
  # Run tests
  runner = unittest.TextTestRunner(verbosity=2)
  result = runner.run(suite)
  
  # Return 0 if all tests passed, 1 otherwise
  return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
  sys.exit(run_tests())

#fin