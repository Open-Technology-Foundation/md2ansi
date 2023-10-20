% DV2(1) md2ansi - simple terminal markdown translator | Version 0.4.20
% Gary Dean
% Oct 2023

# NAME
**md2ansi - simple terminal markdown translator**
# SYNOPSIS
**`md2ansi [file.md [...]] [< md_input_stream]`**

  `agent`

    Agent file (with '.dv2.agent' filename extension).
    Optional, Positional; must be first argument,
    before any other options.

  `script_file`

    script.dv2 file, via stdin. --

| hdr1 | hdr2 | hdr3 |
| --- | --- | --- |
| AA | BBB | CCCC |
| aaaa | bbb | cc |
| 1 | 2 | 3 |

# EXAMPLES:
```bash
    md2ansi < README.md
    md2ansi < \*.md
    md2ansi file1.md
    md2ansi file1.md file2.md file3.md \< file4.md
```


# REQUIRES
No requirements. Pure Bash.

# REPORTING BUGS
Report bugs and deficiencies on the [DV2 github page](https://github.com/Open-Technology-Foundation/md2ansi)

# COPYRIGHT
Copyright © 2022-2023 [Indonesian Open Technology Foundation](https://yatti.id).  License GPLv3+: GNU GPL version 3 or later [GNU Licences](https://gnu.org/licenses/gpl.html).  This is free software: you are free to change and redistribute it.  There is NO WARRANTY, to the extent permitted by law.

# SEE ALSO
  [YaTTI github](https://github.com/Open-Technology-Foundation/)

