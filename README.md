# MD2ANSI

A powerful Python-based Markdown to ANSI terminal formatter that renders markdown files with color and style directly in your terminal.

![Version](https://img.shields.io/badge/version-0.9.0-blue.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)

## Features

- **Headers** (H1-H6) with distinct color gradients
- **Lists** (unordered) with proper nesting and indentation
- **Code Blocks** (fenced with ``` or ~~~) with language detection
- **Tables** (pipe-delimited with alignment support)
- **Blockquotes** with background highlighting
- **Horizontal Rules** with full-width rendering
- **Inline Formatting:**
  - **Bold** text rendering
  - *Italic* text rendering
  - ~~Strikethrough~~ text rendering
  - `Inline code` with distinct styling
- **Smart text wrapping** that preserves formatting
- **Terminal width detection** with customization options

## Installation

Clone the repository and make the script executable:

```bash
git clone https://github.com/Open-Technology-Foundation/md2ansi
cd md2ansi
chmod +x md2ansi.py
# Create a symbolic link (optional):
sudo ln -s $(pwd)/md2ansi.py /usr/local/bin/md2ansi
```

## Usage

```bash
# Process a single markdown file
md2ansi README.md

# Process multiple files
md2ansi file1.md file2.md

# Process markdown from stdin and pipe to less
cat README.md | md2ansi | less

# Force specific terminal width
md2ansi --width 100 README.md
```

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

MD2ANSI uses ANSI escape sequences to provide colored output in the terminal:

- Headers use a distinct color gradient (yellow → orange → green → blue → purple)
- Code blocks use gray with proper indentation
- Tables use gray borders with content formatting
- Lists use cyan bullets with proper indentation
- Blockquotes use a dark background
- Horizontal rules use cyan dashes
- Regular text uses light gray

Terminal width is auto-detected with graceful fallbacks to ensure proper text wrapping. The script handles ANSI escape sequences correctly when calculating line lengths, ensuring that formatting is preserved when wrapping text.

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
