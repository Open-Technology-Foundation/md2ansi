# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
MD2ANSI is a zero-dependency Python tool that converts Markdown to ANSI-colored terminal output. The codebase follows K.I.S.S. principles with all core functionality in a single Python file for easy distribution.

## Architecture
- **md2ansi.py**: Main converter (1170 lines) - handles all parsing, rendering, and CLI
  - Security layer: `safe_regex_sub()`, `safe_regex_match()` - ReDoS protection with timeouts
  - Core parser: `md2ansi()` - main markdown-to-ANSI conversion pipeline
  - Inline formatting: `colorize_line()` - handles bold, italic, links, code
  - Syntax highlighting: `highlight_code()` - language-aware code coloring
  - Table rendering: `build_table_ansi()` - alignment-aware table formatter
  - Debug system: `debug_print()` with `DEBUG_MODE` global flag
- **Wrapper Scripts**:
  - `md`: Bash wrapper that pipes output through `less -R` for pagination
  - `display-ansi-palette`: Shows ANSI 256-color palette
  - `md-link-extract`: Extracts links from markdown files (uses `--` for grep safety)
  - `md2ansi-install.sh`: System-wide installation to `/usr/local/share/md2ansi`
  - `md2ansi-create-manpage.sh`: Generates troff-format man page from README
- **Testing Infrastructure**:
  - `test_md2ansi.py`: 44 unit tests covering all major functions
  - `run_tests.sh`: Test runner with pytest/unittest fallback
  - `test_fixtures/`: Markdown test files including ReDoS patterns
- **Configuration Files**:
  - `.bash_completion`: Tab completion for md2ansi and md commands
  - `md2ansi.manpage`: Generated man page in troff format

## Development Commands

### Running and Testing
```bash
# Run with debug output (to stderr)
./md2ansi -D README.md 2>debug.log

# Run full test suite
./run_tests.sh
./run_tests.sh --verbose
./run_tests.sh --coverage  # requires pytest-cov

# Run specific test class
python3 -m unittest test_md2ansi.TestSafeRegex

# Test ReDoS protection
timeout 2 ./md2ansi test_fixtures/redos_patterns.md

# Generate/update manpage
./md2ansi-create-manpage.sh
./md2ansi-create-manpage.sh --preview
```

### Installation
```bash
# Install system-wide
sudo ./md2ansi-install.sh

# Install bash completion
source .bash_completion

# Install manpage
./md2ansi-create-manpage.sh --install
```

## Code Style Guidelines
- Python:
  - 2-space indentation with shebang `#!/usr/bin/env python3`
  - Imports order: standard lib, third-party, local modules
  - Type hints for function parameters and return values
  - Constants in UPPER_CASE defined at top of files
  - Line length ~80 characters, descriptive variable/function names
  - Use f-strings for string formatting
  - End all scripts with `\n#fin\n`

- Shell/Bash:
  - Always use `set -euo pipefail` for error handling
  - 2-space indentation with shebang `#!/usr/bin/env bash`
  - Declare variables with `declare` statements before use
  - Prefer `[[` over `[` for conditionals
  - Use `-i` flag for integer variables
  - End all scripts with `\n#fin\n`

## Security Considerations
- **Input Validation**: Files and stdin limited to 10MB to prevent DoS
- **Command Injection**: All grep commands use `--` separator
- **ANSI Sanitization**: Existing ANSI sequences removed from input to prevent rendering issues
- **Error Handling**: Specific exceptions caught with clear error messages
- **Signal Handling**: SIGINT handled gracefully with terminal reset

## Error Handling
- Python: Use try/except with specific exception handling
- Shell: Use proper exit codes and error messages
- Include terminal cleanup (ANSI reset) in error paths
- Handle SIGINT signals gracefully
- File size validation before processing (10MB limit)

## Version 0.9.6 Security & Performance Architecture

### ReDoS Protection System
- All regex operations wrapped in `safe_regex_sub()` with 1-second timeout
- Threading-based timeout mechanism prevents catastrophic backtracking
- Input size validation: MAX_REGEX_INPUT_SIZE = 100KB, MAX_FILE_SIZE = 10MB
- Fallback mechanisms when regex operations fail or timeout

### Debug Mode Implementation
- Global `DEBUG_MODE` flag set via `--debug`/`-D` command line
- `debug_print()` outputs timestamped messages to stderr
- Debug points throughout: terminal width detection, regex operations, file processing
- Performance timing information in debug output

### Testing Strategy
- Unit tests use `unittest` framework (zero dependencies)
- Test fixtures include edge cases and malicious patterns
- `run_tests.sh` automatically detects pytest or falls back to unittest
- Security tests verify ReDoS protection with actual attack patterns

## Implementation Principles
- K.I.S.S. (Keep It Simple, Stupid)
- Focus on terminal compatibility and performance
- Python 3.8+ for Python implementation
- Bash 5+ for Bash implementation
- Maintain backward compatibility with existing features
- Zero external dependencies (Python stdlib only)

## Critical Functions Reference

### Security Layer (Lines 58-161)
- `safe_regex_sub(pattern, replacement, text, timeout=1.0)`: Timeout-protected regex substitution
- `safe_regex_match(pattern, text, timeout=1.0)`: Timeout-protected regex matching
- `RegexTimeout`: Exception raised when regex operations exceed timeout

### Core Processing Pipeline (Lines 547-848)
- `md2ansi(lines, term_width, options)`: Main parser, handles all markdown elements
- `process_file(filename, term_width, options)`: Entry point with size validation
- `sanitize_code(code)`: Removes ANSI sequences before syntax highlighting

### Rendering Functions (Lines 399-544)
- `colorize_line(line, options)`: Inline formatting (bold, italic, links, code)
- `highlight_code(code, language)`: Language-aware syntax highlighting
- `build_table_ansi(table_lines, term_width)`: Table rendering with alignment
- `wrap_text(line, width)`: ANSI-aware text wrapping

### Utility Functions (Lines 399-442)
- `get_terminal_width()`: Multi-method detection with bounds checking (20-500)
- `parse_table(lines, start_index)`: Extracts consecutive table lines

## Files to Ignore
- .gudang/, .symlink, tmp/, temp/, .temp/

#fin