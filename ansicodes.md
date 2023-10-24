
# ANSI colours for Fun and Profit

     > ANSI escape codes can be used to modify text colour and style in a Bash terminal.
>
> These codes are prefixed with `\x1b[` and suffixed with `m`.
>

### Foreground (Text) Colour Codes

    | Description | ANSI Code |
|-------------|-----------|
| Black       | `30`      |
| Red         | `31`      |
| Green       | `32`      |
| Yellow      | `33`      |
| Blue        | `34`      |
| Magenta     | `35`      |
| Cyan        | `36`      |
| White       | `37`      |


### Background Colour Codes

| Description | ANSI Code |
|-------------|-----------|
| Black       | `40`      |
| Red         | `41`      |
| Green       | `42`      |
| Yellow      | `43`      |
| Blue        | `44`      |
| Magenta     | `45`      |
| Cyan        | `46`      |
| White       | `47`      |


### Text Style Codes

| Description     | ANSI Code |
|-----------------|-----------|
| Reset All       | `0`       |
| Bold            | `1`       |
| Dim             | `2`       |
| Italic          | `3`       |
| Underlined      | `4`       |
| Blink (Slow)    | `5`       |
| Blink (Rapid)   | `6`       |
| Reverse         | `7`       |
| Hidden          | `8`       |
| Strike-through  | `9`       |


### Resetting Text Style Codes

| Description     | ANSI Code |
|-----------------|-----------|
| Reset Bold      | `22`      |
| Reset Dim       | `22`      |
| Reset Italic    | `23`      |
| Reset Underline | `24`      |
| Reset Blink     | `25`      |
| Reset Reverse   | `27`      |
| Reset Hidden    | `28`      |
| Reset Strikethrough | `29`     |


### Usage Examples

- To set the text colour to red: `\\\\x1b[31m`
- To set the background colour to blue: `\\\\x1b[44m`
- To make text bold: `\\\\x1b[1m`
- To reset all attributes to default: `\\\\x1b[0m`

You can combine multiple codes by separating them with semicolons. For example, to set the text to red and bold, you can use `\\\\x1b[31;1m`.

