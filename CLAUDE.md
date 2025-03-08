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

## Error Handling
- Python: Use try/except with specific exception handling
- Shell: Use proper exit codes and error messages
- Include terminal cleanup (ANSI reset) in error paths
- Handle SIGINT signals gracefully

## Recent Improvements (v0.9.5)
- Fixed syntax highlighting issues with ANSI escape sequences
- Improved handling of code blocks for all supported languages
- Fixed handling of multiline strings and comments in code blocks
- Improved error handling with specific error messages
- Fixed table alignment with mismatched column counts
- Removed unused imports for better performance
- Fixed issues with undefined variables

## Implementation Principles
- K.I.S.S. (Keep It Simple, Stupid)
- Focus on terminal compatibility and performance
- Python 3.8+ for Python implementation
- Bash 5+ for Bash implementation
- Maintain backward compatibility with existing features

## Files to Ignore
- .gudang/, .symlink, tmp/, temp/, .temp/

#fin