# MD2ANSI

A Python-based Markdown to ANSI terminal formatter that renders markdown files with color and style directly in your terminal.

![Version](https://img.shields.io/badge/version-0.9.5-blue.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)

## Features

- **Headers** (H1-H6) with distinct color gradients
- **Lists:**
  - Unordered lists with proper nesting and indentation
  - Ordered lists with nesting support
  - Task lists with checkboxes ([ ] and [x])
- **Code Blocks:**
  - Fenced with ``` or ~~~ with language detection
  - Syntax highlighting for Python, JavaScript, and Bash
  - Support for language aliases (py, js, sh)
  - Handles multiline strings and comments in code blocks
  - Improved ANSI escape sequence handling for clean display
- **Tables:**
  - Pipe-delimited with alignment support
  - Enhanced formatting with mixed styling in cells
  - Handles tables with mismatched column counts
- **Blockquotes** with background highlighting
- **Horizontal Rules** with full-width rendering
- **Inline Formatting:**
  - **Bold** text rendering
  - *Italic* text rendering
  - ~~Strikethrough~~ text rendering
  - `Inline code` with distinct styling
  - [Links](https://example.com) with underlined styling
  - ![Image](url) with alt text placeholder
  - [^1] Footnote references and rendering
  - Better nested formatting (***bold italic***, etc.)
- **Smart text wrapping** that preserves formatting
- **Terminal width detection** with customization options
- **Improved error handling** with specific error messages

## Installation

### Method 1: Automatic Installation (Recommended)

Use the provided installation script for system-wide installation:

```bash
# Download and run the installation script
curl -sL https://raw.githubusercontent.com/Open-Technology-Foundation/md2ansi/main/md2ansi-install.sh | bash

# Or if you've already cloned the repository
cd md2ansi
./md2ansi-install.sh
```

The installation script will:
- Create a directory at `/usr/local/share/md2ansi`
- Clone the repository into that directory
- Set proper permissions
- Create symbolic links in `/usr/local/bin` for `md2ansi` and `md` commands

### Method 2: Manual Installation

Clone the repository and make the scripts executable:

```bash
git clone https://github.com/Open-Technology-Foundation/md2ansi
cd md2ansi
chmod +x md2ansi.py md2ansi md
# Create symbolic links (optional):
sudo ln -s $(pwd)/md2ansi /usr/local/bin/md2ansi
sudo ln -s $(pwd)/md /usr/local/bin/md
```

## Usage

```bash
# Process a single markdown file
md2ansi README.md

# View markdown file with pager (uses the 'md' wrapper script)
md README.md

# Process multiple files
md2ansi file1.md file2.md

# Process markdown from stdin and pipe to less
cat README.md | md2ansi | less -R

# Force specific terminal width
md2ansi --width 100 README.md

# Disable specific features
md2ansi --no-syntax-highlight README.md
md2ansi --no-footnotes --no-tables README.md

# Plain text mode (disable all formatting)
md2ansi --plain README.md

# Debug mode (shows parsing information)
md2ansi --debug README.md
```

### Command Line Options

* `-h`, `--help`: Show help message and exit
* `-V`, `--version`: Show version information and exit
* `-D`, `--debug`: Enable debug mode (shows parsing information)
* `--width WIDTH`: Force specific terminal width (default: auto-detect)
* `--no-footnotes`: Disable footnotes processing
* `--no-syntax-highlight`: Disable syntax highlighting in code blocks
* `--no-tables`: Disable tables formatting
* `--no-task-lists`: Disable task lists (checkboxes) formatting
* `--no-images`: Disable image placeholders
* `--no-links`: Disable links formatting
* `--plain`: Use plain text mode (disables all formatting features)

## Formatting Examples

### Headers

Headers are rendered with a color gradient from yellow to purple:

```markdown
# H1 Header (Yellow)
## H2 Header (Orange)
### H3 Header (Green)
#### H4 Header (Blue)
##### H5 Header (Purple)
###### H6 Header (Dark Gray)
```

### Lists

Nested lists are properly indented and formatted:

```markdown
* Main item 1
* Main item 2
  * Subitem 2.1
  * Subitem 2.2
    * Sub-subitem 2.2.1
* Main item 3
```

### Tables

Tables support alignment and inline formatting:

| Feature | Support | Example |
|:--------|:-------:|--------:|
| Left-aligned | ✓ | `:-----` |
| Center-aligned | ✓ | `:----:` |
| Right-aligned | ✓ | `-----:` |
| **Bold** in tables | ✓ | `**Bold**` |
| *Italic* in tables | ✓ | `*Italic*` |
| `Code` in tables | ✓ | `` `Code` `` |

### Code Blocks

Code blocks preserve indentation and support language specification:

````markdown
```python
def hello_world():
    print("Hello, World!")

    # Indentation is preserved
    for i in range(5):
        print(f"Count: {i}")
```
````

### Blockquotes

Blockquotes are rendered with a dark background:

```markdown
> This is a blockquote.
> It can span multiple lines and will be properly wrapped.
>
> Even with blank lines in between.
```

### Horizontal Rules

Horizontal rules span the full width of the terminal:

```markdown
---
```

### Inline Formatting

Inline formatting can be combined in various ways:

```markdown
**Bold text** and *italic text* and ~~strikethrough~~ and `inline code`.

You can also **combine *different* ~~styles~~ `together`**.
```

## Technical Details

### ANSI Formatting

MD2ANSI uses ANSI escape sequences to provide colored output in the terminal:

- Headers use a distinct color gradient (yellow → orange → green → blue → purple)
- Code blocks use gray with proper indentation
- Tables use gray borders with content formatting
- Lists use cyan bullets with proper indentation
- Blockquotes use a dark background
- Horizontal rules use cyan dashes
- Regular text uses light gray

Terminal width is auto-detected with graceful fallbacks to ensure proper text wrapping. The script handles ANSI escape sequences correctly when calculating line lengths, ensuring that formatting is preserved when wrapping text.

### Included Scripts

The repository includes several utility scripts:

- `md2ansi`: The main Python script for converting Markdown to ANSI-colored terminal output
- `md`: A wrapper script that pipes markdown files through md2ansi and the `less` pager with proper options
- `md2ansi-install.sh`: Installation script for system-wide deployment
- `display_ansi_palette`: A utility script to display the ANSI color palette in your terminal

## Performance Test

Here's a complex example that demonstrates MD2ANSI's capabilities:

| Formatting | Simple | **Bold** | *Italic* | ~~Strikethrough~~ | `Code` | **`Combined`** |
|:-----------|:-------|:---------|:---------|:------------------|:-------|:---------------|
| Support    | ✓      | ✓        | ✓        | ✓                 | ✓      | ✓              |
| Rendering  | Plain  | Bold     | Italic   | Strikethrough     | Mono   | Bold+Mono      |
| Colors     | Gray   | Gray     | Gray     | Gray              | Gray   | Gray           |

> **Note:** MD2ANSI handles complex nested formatting while maintaining proper alignment in tables.
>
> This is particularly useful for technical documentation with code examples:
>
> ```python
> def format_text(text, style="bold"):
>     if style == "bold":
>         return f"**{text}**"
>     elif style == "italic":
>         return f"*{text}*"
>     else:
>         return text
> ```

## Requirements

- Python 3.8+
- Linux/Unix terminal with ANSI color support
- For viewing files with the `md` script: `less` pager with `-R` flag support
- No external Python dependencies required

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Copyright © 2022-2025 [Indonesian Open Technology Foundation](https://yatti.id)
Licensed under GPL-3.0. See LICENSE file for details.

## Bug Reports

Please report any issues on the [GitHub repository](https://github.com/Open-Technology-Foundation/md2ansi/issues).

---

*This README.md file serves as both documentation and a test case for MD2ANSI. Try rendering it with the tool to see all formatting features in action!*
