# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
MD2ANSI is a zero-dependency Python tool that converts Markdown to ANSI-colored terminal output. The codebase follows K.I.S.S. principles with all core functionality in a single Python file for easy distribution.

## Architecture
- **md2ansi.py**: Main converter (964 lines) - handles all parsing, rendering, and CLI
  - Key functions: `md2ansi()` (main parser), `colorize_line()` (inline formatting), `highlight_code()` (syntax highlighting), `build_table_ansi()` (table rendering)
  - Uses regex-based parsing with careful ANSI escape sequence handling
  - Implements streaming line-by-line processing for memory efficiency
- **Wrapper Scripts**:
  - `md`: Bash wrapper that pipes output through `less -R` for pagination
  - `display_ansi_palette`: Shows ANSI 256-color palette (includes `trim()` function)
  - `md-link-extract`: Extracts links from markdown files (uses `--` for grep safety)
  - `md2ansi-install.sh`: System-wide installation to `/usr/local/share/md2ansi`
- **Bash Completion**: `.bash_completion` provides tab completion for .md files only

## Project Commands
- Run md2ansi: `./md2ansi [file.md]` or `cat file.md | ./md2ansi`
- View markdown in terminal: `./md file.md` (pipes through less pager)
- Display color palette: `./display_ansi_palette`
- View help: `./md2ansi -h` or `./md2ansi --help`
- Check version: `./md2ansi -V` or `./md2ansi --version`
- Force specific width: `./md2ansi --width 100 README.md`
- Disable features: `./md2ansi --no-footnotes --no-tables README.md`
- Plain text mode: `./md2ansi --plain README.md`
- Debug mode: `./md2ansi -D` or `./md2ansi --debug`

## Testing Commands
- Manual testing: `./md2ansi test_features.md`
- Feature verification: `./md2ansi test_features.md | less -R`
- Test specific feature: `./md2ansi test_features.md | grep -A10 "### Headers"`
- Test bash completion: `source ./.bash_completion && complete -p md2ansi`

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

## Recent Improvements (v0.9.5)
- Fixed syntax highlighting issues with ANSI escape sequences
- Improved handling of code blocks for all supported languages
- Fixed handling of multiline strings and comments in code blocks
- Improved error handling with specific error messages
- Fixed table alignment with mismatched column counts
- Removed unused imports for better performance
- Fixed issues with undefined variables
- Added input size validation for security
- Fixed undefined `trim()` function in display_ansi_palette
- Added `--` to grep commands to prevent command injection

## Implementation Principles
- K.I.S.S. (Keep It Simple, Stupid)
- Focus on terminal compatibility and performance
- Python 3.8+ for Python implementation
- Bash 5+ for Bash implementation
- Maintain backward compatibility with existing features
- Zero external dependencies (Python stdlib only)

## Critical Functions Reference
- `sanitize_code()`: Removes ANSI sequences from code blocks before highlighting
- `get_terminal_width()`: Multi-method terminal width detection with 80-char fallback
- `wrap_text()`: ANSI-aware text wrapping that preserves formatting
- `parse_table()`: Extracts consecutive table lines from markdown
- `process_file()`: Entry point for file/stdin processing with size validation

## Files to Ignore
- .gudang/, .symlink, tmp/, temp/, .temp/

#fin