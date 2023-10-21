# NAME

**md2ansi - simple terminal markdown translator**

# SYNOPSIS

**`md2ansi [file.md [...]] [< md_input_stream]`**

`file.md`

Markdown formatted file. Optional.

`md_input_stream`

Markdown formatted input stream via stdin. Required if `file.md` not specified.

# EXAMPLES:

```bash
md2ansi < README.md

md2ansi < \*.md

md2ansi file1.md

md2ansi file1.md file2.md file3.md \< file4.md

```

# REQUIRES

Bash 5.1

# REPORTING BUGS

Report bugs and deficiencies on the [Open Technology github page](https://github.com/Open-Technology-Foundation/md2ansi)

# COPYRIGHT

Copyright © 2022-2023 [Indonesian Open Technology Foundation](https://yatti.id).  License GPLv3+: GNU GPL version 3 or later [GNU Licences](https://gnu.org/licenses/gpl.html).  This is free software: you are free to change and redistribute it.  There is NO WARRANTY, to the extent permitted by law.

# SEE ALSO

[YaTTI github](https://github.com/Open-Technology-Foundation/)

