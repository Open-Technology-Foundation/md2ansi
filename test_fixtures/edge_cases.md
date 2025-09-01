# Edge Cases

## Empty Lines



Multiple empty lines above.

## Special Characters

< > & " ' ` | \ / ! @ # $ % ^ * ( ) [ ] { } = + - _ ~ : ; , . ?

## Unicode

Émojis: 😀 🎉 🚀

Chinese: 你好世界

Arabic: مرحبا بالعالم

## Nested Formatting

**Bold with *italic* inside**

*Italic with **bold** inside*

***All bold and italic with `code` inside***

## Task Lists

- [ ] Unchecked task
- [x] Checked task
- [ ] Task with **bold** text
- [x] Task with [link](url)

## Mixed Content

> Blockquote with **bold** and *italic* and `code`
> - List item in blockquote
> - Another item

## Very Long Line

This is a very long line that should be wrapped when displayed in the terminal because it exceeds the typical terminal width of 80 or 100 characters and needs to be broken into multiple lines for proper display.

## Malformed Markdown

**Unclosed bold

*Unclosed italic

[Unclosed link](

![Unclosed image](

## ANSI Escape Sequences in Content

This text contains \x1b[31mred\x1b[0m ANSI codes that should be sanitized.

Code block with ANSI:
```
\x1b[38;5;196mColored text\x1b[0m
```