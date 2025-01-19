# MD2ANSI

A Python-based Markdown to ANSI terminal formatter that renders markdown files with color and style directly in your terminal.

## Features

- **Headers** (H1-H6) with distinct colors
- **Lists** (unordered)
- **Code Blocks** (fenced with ``` or ~~~)
- **Tables** (pipe-delimited with alignment support)
- **Blockquotes**
- **Horizontal Rules**
- **Inline Formatting:**
  - Bold (**text**)
  - Italic (*text*)
  - Strikethrough (~~text~~)
  - Inline code (`code`)

## Installation

Clone the repository and make the script executable:

```bash
git clone https://github.com/Open-Technology-Foundation/md2ansi
cd md2ansi
chmod +x md2ansi.py
```

Create a symbolic link (optional):
```bash
ln -s md2ansi.py md2ansi
```

## Usage

```bash
# Process a single markdown file
./md2ansi README.md

# Process multiple files
./md2ansi file1.md file2.md

# Process markdown from stdin
cat README.md | ./md2ansi

# Force specific terminal width
./md2ansi --width 100 README.md
```

## Examples

### Headers
```markdown
# H1 Header
## H2 Header
### H3 Header
```

### Lists
```markdown
* Item 1
* Item 2
  * Subitem 2.1
```

### Tables
```markdown
| Align Left | Center | Align Right |
|:-----------|:------:|------------:|
| Left       | Center |       Right |
```

### Code Blocks
````markdown
```python
def hello():
    print("Hello, World!")
```
````

## Requirements

- Python 3.6+
- Linux/Unix terminal with ANSI color support

## Technical Details

The script uses ANSI escape sequences to provide colored output:
- Headers use distinct colors (yellow to purple gradient)
- Code blocks and tables use gray
- Lists and horizontal rules use cyan
- Blockquotes use a dark background
- Regular text uses light gray

Terminal width is auto-detected with graceful fallbacks to ensure proper text wrapping.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Copyright © 2022-2025 [Indonesian Open Technology Foundation](https://yatti.id)
Licensed under GPL-3.0. See LICENSE file for details.

## Bug Reports

Please report any issues on the [GitHub repository](https://github.com/Open-Technology-Foundation/md2ansi/issues).
