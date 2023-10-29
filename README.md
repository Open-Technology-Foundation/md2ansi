# **MD2ANSI** - markdown to ansi translator for Bash terminal

## DESCRIPTION

Print formatted ANSI output to terminal from Markdown file.md or Markdown input stream.

`md2ansi` is 100% core `Bash`.

`md2ansi` converts Markdown streams into a terminal representation using ANSI escape sequences for formatting. It defines various ANSI color codes for different Markdown elements such as code blocks, tables, headers, blockquotes, italics, bold, strikethrough, inline code, and lists.

* Code Blocks: Detects code block markers (lines starting with "\u0060\u0060\u0060") and applies the appropriate formatting to display the code block content.

* Tables: Detects lines starting with "|" to identify table rows. It processes the table rows, determines the maximum width for each column, and formats the table accordingly.

* Horizontal Rules: Detects lines consisting of "---", "===", or "\_\_\_" to create horizontal rules in the output.

* Blockquotes: Lines starting with ">" are treated as blockquotes and indented accordingly.

* Italics and Bold: Markdown for italics and bold with the corresponding ANSI color codes.

* Strikethrough: Markdown for strikethrough with the corresponding ANSI color code.

* Inline Code: Markdown for inline code with the corresponding ANSI color code.

* Lists: The script indents lines starting with "\u002A" or "-" to represent unordered lists.

* Headers: Markdown for headers with the corresponding ANSI color codes.

# h1
## h2
### h3
#### h4
##### h5
###### h6

* General Text Formatting: The `fmt` command is optionally used to wrap and format general text content.

The following markdown codes are processed:

 | function    | ansi      | markdown |
 | -:          | :-        | -        |
 | BLOCKQUOTE  | x1b[35m   | ^>       |
 | BOLD        | x1b[31;1m | **       |
 | CODE_BLOCK  | x1b[90m   | ^```     |
 | H1          | x1b[31;1m | ^#       |
 | H2          | x1b[32;1m | ^##      |
 | H3          | x1b[33;1m | ^###     |
 | H4          | x1b[33m   | ^####    |
 | H5          | x1b[34;1m | ^#####   |
 | H6          | x1b[34m   | ^######  |
 | HR          | x1b[36m   | ---      |
 | CODE        | x1b[97m   | ``       |
 | ITALIC      | x1b[34m   | *        |
 | LIST        | x1b[36m   | ^*       |
 | RESET       | x1b[0m    |          |
 | STRIKE      | x1b[2m    | ~~       |
 | TABLE_BLOCK | x1b[90m   | \\|*       |

For each line of input to `md2ansi`, the following transformations are carried out, in this order:

  | transform | match |
  | :- | - |
  | Code_Block | ^```
  | Tables  | ^[space]|space
  | Horizontal_Rules  | ^--- ^=== ^___
  | Blockquotes  | ^\>
  | Bold | **
  | Italics | *
  | Strikethrough  | ~~
  | Inline_Code  | `(.*?)`
  | List_star | ^[space]*\*space[.*]
  | List_dash | ^[space]*\-space[.*]
  | Headers | ^#[#....]}space(.*)

## SYNOPSIS

**`md2ansi [file.md [...]] [< md_input_stream]`**

`file.md`

Markdown formatted file. Optional.

`md_input_stream`

Markdown formatted input stream via stdin. Required if `file.md` not specified.

## EXAMPLES:

~~~bash
md2ansi < README.md

md2ansi < \*.md

md2ansi file1.md

md2ansi file1.md file2.md file3.md < file4.md

~~~

## REQUIRES

Bash 5.1

## REPORTING BUGS

Report bugs and deficiencies on the [Open Technology github page](https://github.com/Open-Technology-Foundation/md2ansi)

## COPYRIGHT

Copyright © 2022-2023 [Indonesian Open Technology Foundation](https://yatti.id).  License GPLv3+: GNU GPL version 3 or later [GNU Licences](https://gnu.org/licenses/gpl.html).  This is free software: you are free to change and redistribute it.  There is NO WARRANTY, to the extent permitted by law.

## SEE ALSO

[YaTTI github](https://github.com/Open-Technology-Foundation/)

