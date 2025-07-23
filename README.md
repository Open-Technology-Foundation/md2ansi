# MD2ANSI

A Python-based Markdown to ANSI terminal formatter that renders markdown files with color and style directly in your terminal.

![Version](https://img.shields.io/badge/version-0.9.5-blue.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)

## Features

- **Headers** (H1-H6) with distinct color gradients from yellow to purple
- **Lists:**
  - Unordered lists with proper nesting and indentation
  - Ordered lists with automatic numbering
  - Task lists with checkboxes ([ ] and [x])
  - Nested list support with proper indentation
- **Code Blocks:**
  - Fenced with ``` or ~~~ with language detection
  - Syntax highlighting for Python, JavaScript, and Bash
  - Support for language aliases (py, js, sh, shell)
  - Handles multiline strings and comments correctly
  - ANSI escape sequence sanitization for clean display
- **Tables:**
  - Pipe-delimited with alignment support (left, center, right)
  - Enhanced formatting with mixed styling in cells
  - Handles tables with mismatched column counts gracefully
- **Blockquotes** with dark background highlighting
- **Horizontal Rules** with full-width terminal rendering
- **Inline Formatting:**
  - **Bold** text rendering
  - *Italic* text rendering
  - ~~Strikethrough~~ text rendering
  - `Inline code` with distinct styling
  - [Links](https://example.com) with underlined styling
  - ![Image](url) with alt text placeholder
  - [^1] Footnote references with automatic collection
  - Nested formatting support (***bold italic***, etc.)
- **Smart Features:**
  - Terminal width auto-detection with fallbacks
  - ANSI-aware text wrapping that preserves formatting
  - File size validation (10MB limit for security)
  - Graceful signal handling (Ctrl+C)
- **Security:**
  - Input sanitization to prevent ANSI injection
  - File size limits to prevent DoS attacks
  - Safe handling of special characters in filenames

## Installation

### Method 1: Automatic Installation (Recommended)

Use the provided installation script for system-wide installation:

```bash
# Download and run the installation script
curl -sL https://raw.githubusercontent.com/Open-Technology-Foundation/md2ansi/main/md2ansi-install.sh | bash

# Or if you've already cloned the repository
cd md2ansi
./md2ansi-install.sh

# To uninstall
./md2ansi-install.sh --uninstall
```

The installation script will:
- Check prerequisites (git, bash)
- Clone the repository to `/usr/local/share/md2ansi`
- Set executable permissions on all scripts
- Create symbolic links in `/usr/local/bin` for `md2ansi` and `md` commands
- Install bash completion support (if available)

### Method 2: Manual Installation

Clone the repository and make the scripts executable:

```bash
git clone https://github.com/Open-Technology-Foundation/md2ansi
cd md2ansi
chmod +x md2ansi.py md2ansi md display_ansi_palette md-link-extract

# Create symbolic links (optional but recommended):
sudo ln -s $(pwd)/md2ansi /usr/local/bin/md2ansi
sudo ln -s $(pwd)/md /usr/local/bin/md

# Install bash completion (optional):
sudo cp bash-completion/md2ansi /etc/bash_completion.d/
```

### Method 3: Local Usage (No Installation)

Simply clone and run directly:

```bash
git clone https://github.com/Open-Technology-Foundation/md2ansi
cd md2ansi
./md2ansi README.md
```

## Usage

### Basic Usage

```bash
# View a single markdown file
md2ansi README.md

# View with pager for long files (recommended)
md README.md

# Process multiple files
md2ansi *.md
md2ansi docs/*.md

# Process from stdin
cat README.md | md2ansi
echo "# Hello World" | md2ansi

# Process from URL
curl -s https://raw.githubusercontent.com/user/repo/main/README.md | md2ansi
```

### Advanced Usage

```bash
# Force specific terminal width
md2ansi --width 100 README.md

# Disable specific features
md2ansi --no-syntax-highlight code-heavy.md
md2ansi --no-tables --no-footnotes simple.md

# Plain text mode (all formatting disabled)
md2ansi --plain README.md

# View help and version
md2ansi --help
md2ansi --version
```

### Integration Examples

```bash
# Git diff with markdown formatting
git show HEAD:README.md | md2ansi

# View markdown documentation in man-page style
md2ansi API.md | less -R

# Create a markdown viewer function
mdview() { md2ansi "$1" | less -R; }

# Compare two markdown files side by side
diff -y <(md2ansi --plain old.md) <(md2ansi --plain new.md)

# Search through formatted markdown
md2ansi docs/*.md | grep -i "installation"
```

### Utility Scripts

```bash
# Display ANSI color palette
./display_ansi_palette

# Extract all links from a markdown file
./md-link-extract README.md

# Install/uninstall system-wide
./md2ansi-install.sh --help
```

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Show help message and exit |
| `--version` | `-V` | Show version information and exit |
| `--debug` | `-D` | Enable debug mode (reserved for future use) |
| `--width WIDTH` | | Force specific terminal width (default: auto-detect) |
| `--no-footnotes` | | Disable footnotes processing |
| `--no-syntax-highlight` | | Disable syntax highlighting in code blocks |
| `--no-tables` | | Disable tables formatting |
| `--no-task-lists` | | Disable task lists (checkboxes) formatting |
| `--no-images` | | Disable image placeholders |
| `--no-links` | | Disable links formatting |
| `--plain` | | Plain text mode (disables all formatting) |

## Formatting Examples

### Headers

Headers are rendered with a distinct color gradient:

```markdown
# H1 Header (Bright Yellow)
## H2 Header (Orange)
### H3 Header (Green)
#### H4 Header (Blue)
##### H5 Header (Purple)
###### H6 Header (Dark Gray)
```

### Lists

All list types are supported with proper nesting:

```markdown
* Unordered list item
  * Nested item
    * Deep nested item
  * Another nested item

1. Ordered list item
2. Second item
   1. Nested ordered item
   2. Another nested item

- [ ] Unchecked task
- [x] Checked task
  - [ ] Nested task
```

### Tables

Tables support alignment and inline formatting:

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| Text | **Bold** | *Italic* |
| `Code` | ~~Strike~~ | [Link](url) |
| Plain | ***Bold Italic*** | Mixed |
```

Tables with mismatched columns are handled gracefully:

```markdown
| Col1 | Col2 | Col3 |
|------|------|
| Data spans | remaining columns |
```

### Code Blocks

Syntax highlighting for multiple languages:

````markdown
```python
def fibonacci(n: int) -> int:
    """Calculate fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

```javascript
const greet = (name = 'World') => {
    console.log(`Hello, ${name}!`);
    return Promise.resolve(name);
};
```

```bash
#!/bin/bash
set -euo pipefail

echo "Setting up environment..."
for file in *.md; do
    md2ansi "$file" > "${file%.md}.txt"
done
```
````

### Blockquotes

Blockquotes with nested formatting:

```markdown
> **Important:** This is a blockquote with *emphasis* and `code`.
> 
> It can span multiple lines and include:
> - Lists
> - [Links](https://example.com)
> - Even code blocks:
>
> ```python
> print("Hello from a blockquote!")
> ```
```

### Inline Formatting

Complex nested formatting is supported:

```markdown
You can **bold**, *italicize*, ~~strike~~, and `code` text.

Combine them: ***bold italic***, **`bold code`**, *`italic code`*.

Links can be [**bold**](url) or [*italic*](url) or [`code`](url).

Footnotes[^1] are collected and displayed at the end[^note].

[^1]: This is the first footnote.
[^note]: This is a named footnote.
```

## Technical Details

### Architecture

MD2ANSI is designed as a single-file Python script with zero external dependencies:

- **Parser**: Line-by-line regex-based parsing for efficiency
- **Renderer**: ANSI escape sequence generation with careful formatting
- **Features**: Modular feature flags for customization
- **Security**: Input validation and sanitization throughout

### ANSI Color Scheme

| Element | Color | ANSI Code |
|---------|-------|-----------|
| H1 | Bright Yellow | `\x1b[38;5;226m` |
| H2 | Orange | `\x1b[38;5;214m` |
| H3 | Green | `\x1b[38;5;118m` |
| H4 | Blue | `\x1b[38;5;21m` |
| H5 | Purple | `\x1b[38;5;93m` |
| H6 | Dark Gray | `\x1b[38;5;239m` |
| Code | Gray | `\x1b[90m` |
| Lists | Cyan | `\x1b[36m` |
| Links | Cyan-Blue | `\x1b[38;5;45m` |
| Text | Light Gray | `\x1b[38;5;7m` |

### Terminal Compatibility

MD2ANSI works with any terminal that supports:
- 256-color ANSI sequences
- UTF-8 encoding
- Basic ANSI formatting (bold, italic, underline)

Tested on:
- Linux: GNOME Terminal, Konsole, xterm, Alacritty
- macOS: Terminal.app, iTerm2
- Windows: Windows Terminal, Git Bash, WSL

### Performance

- **Memory efficient**: Processes files line-by-line
- **Fast startup**: No external dependencies to load
- **File size limit**: 10MB for safety (configurable in source)
- **Streaming capable**: Works with pipes and stdin

## Included Scripts

| Script | Purpose |
|--------|---------|
| `md2ansi` | Main converter script (Python) |
| `md2ansi.py` | Symlink to md2ansi for compatibility |
| `md` | Wrapper that pipes through `less -R` |
| `display_ansi_palette` | Shows all 256 ANSI colors |
| `md-link-extract` | Extracts links from markdown files |
| `md2ansi-install.sh` | System-wide installation script |

## Bash Completion

Tab completion is available for both `md2ansi` and `md` commands:

```bash
# Complete .md files only
md2ansi RE<Tab>  # Completes to README.md
md <Tab>          # Shows all .md files

# Complete options
md2ansi --<Tab>   # Shows all available options

# Install completion manually if needed
source bash-completion/md2ansi
```

## Requirements

- **Python**: 3.8 or higher
- **Terminal**: ANSI color support (most modern terminals)
- **Optional**: `less` command for the `md` wrapper script
- **Optional**: `bash-completion` package for tab completion
- **No Python packages required** - uses only standard library

## Security Considerations

MD2ANSI includes several security features:

1. **File size limits**: Files larger than 10MB are rejected
2. **Input sanitization**: ANSI escape sequences in input are removed
3. **Safe file handling**: Proper error messages for invalid files
4. **Command injection prevention**: All grep commands use `--` separator
5. **Signal handling**: Graceful exit on Ctrl+C with terminal reset

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the coding style (2-space indentation, type hints)
4. Add tests for new features
5. Update documentation as needed
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

See [CLAUDE.md](CLAUDE.md) for development guidelines.

## License

Copyright © 2022-2025 [Indonesian Open Technology Foundation](https://yatti.id)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

See [LICENSE](LICENSE) file for details.

## Bug Reports

Please report any issues on the [GitHub repository](https://github.com/Open-Technology-Foundation/md2ansi/issues).

When reporting bugs, please include:
- Your Python version (`python3 --version`)
- Your terminal emulator and OS
- The markdown file causing issues (if possible)
- The exact command you ran
- Any error messages

## Acknowledgments

- Inspired by various markdown terminal viewers
- ANSI color reference from [Wikipedia](https://en.wikipedia.org/wiki/ANSI_escape_code)
- Markdown specification from [CommonMark](https://commonmark.org/)

---

*This README.md file serves as both documentation and a test case for MD2ANSI. Try rendering it with the tool to see all formatting features in action!*

```bash
# Test this README with md2ansi
./md2ansi README.md

# Or use the pager for easier reading
./md README.md
```