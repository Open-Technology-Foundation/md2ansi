# MD2ANSI Test File

This file tests both existing and new features for md2ansi.

## Existing Features

### Headers

# H1 Header
## H2 Header
### H3 Header
#### H4 Header
##### H5 Header
###### H6 Header

### Emphasis

**Bold text** and *italic text* and ~~strikethrough~~ and `inline code`.

Combined formatting: **bold and *italic* text** and *italic and **bold** text*.

### Lists (Unordered)

* First level item 1
* First level item 2
  * Second level item 2.1
  * Second level item 2.2
    * Third level item 2.2.1
* First level item 3

### Code Blocks

```python
def hello_world():
    print("Hello, World!")
    
    # Indentation is preserved
    for i in range(5):
        print(f"Count: {i}")
```

### Tables

| Feature | Support | Example |
|:--------|:-------:|--------:|
| Left-aligned | ✓ | `:-----` |
| Center-aligned | ✓ | `:----:` |
| Right-aligned | ✓ | `-----:` |
| **Bold** in tables | ✓ | `**Bold**` |
| *Italic* in tables | ✓ | `*Italic*` |
| `Code` in tables | ✓ | `` `Code` `` |

### Blockquotes

> This is a blockquote.
> It can span multiple lines and will be properly wrapped.
>
> Even with blank lines in between.

### Horizontal Rules

---

## Implemented Features

### Ordered Lists

1. First ordered item
2. Second ordered item
   1. Nested ordered item 2.1
   2. Nested ordered item 2.2
      1. Deep nested item 2.2.1
3. Third ordered item

Mixed lists:

1. First ordered item
   * Unordered sub-item
   * Another unordered sub-item
2. Second ordered item

### Task Lists

- [ ] Uncompleted task
- [x] Completed task
- [ ] Task with **formatted** *text*
  - [ ] Nested task 1
  - [x] Nested task 2

### Links

[Visit GitHub](https://github.com)
[MD2ANSI Repository](https://github.com/Open-Technology-Foundation/md2ansi)

Visit the [project page](https://github.com/Open-Technology-Foundation/md2ansi) for more information.

### Images

![Terminal Screenshot](screenshot.png)
![MD2ANSI Logo](logo.png)

Text with an inline ![image](icon.png) in the middle.

### Enhanced Code Blocks with Syntax Highlighting

#### Python

```python
def hello_world(name="World"):
    """Say hello to someone"""
    # This is a comment
    print(f"Hello, {name}!")
    
    for i in range(5):
        if i % 2 == 0:
            print(f"{i} is even")
        else:
            print(f"{i} is odd")
            
class Example:
    def __init__(self):
        self.value = 42
```

#### JavaScript

```javascript
// Define a function
function calculateTotal(items) {
  const total = items.reduce((sum, item) => sum + item.price, 0);
  return total;
}

// Example class
class ShoppingCart {
  constructor() {
    this.items = [];
  }
  
  addItem(item) {
    this.items.push(item);
    console.log(`Added ${item.name} to cart`);
  }
}

// Use template strings
const name = "User";
console.log(`Hello, ${name}!`);
```

#### Bash

```bash
#!/usr/bin/env bash
# Simple bash script example

declare -i count=0

function process_files() {
  local dir="$1"
  
  # Loop through files
  for file in "$dir"/*.txt; do
    if [[ -f "$file" ]]; then
      echo "Processing $file"
      count+=1
    fi
  done
  
  echo "Processed $count files"
}

# Call the function
process_files "/tmp"
```

### Enhanced Tables with Mixed Formatting

| Feature | Status | Description | Example |
|:--------|:------:|:------------|--------:|
| **Bold text** | ✅ | Support for bold text | `**Bold**` |
| *Italic text* | ✅ | Support for *italic* text | `*Italic*` |
| [Links](https://example.com) | ✅ | Support for hyperlinks | `[text](url)` |
| **Mixed _formatting_** | ✅ | Different styles together | `**Mixed _formatting_**` |
| `code` in **bold** | ✅ | Bold with inline code | `` `code` in **bold** `` |

### Footnotes

Here's a sentence with a footnote reference[^1].

You can also use named footnotes[^note1] and even put
multiple references[^2] in a single paragraph[^note2].

Footnotes can contain formatted text and even [links](https://example.com).

[^1]: This is the first footnote.
[^2]: This is the second footnote with **bold** and *italic* text.
[^note1]: This is a named footnote.
[^note2]: Footnotes can contain [links](https://example.com) and `code` too.

### Better Nested Formatting

- ***Bold and italic text*** using triple asterisks
- **_Bold and italic text_** using bold outside, italic inside
- _**Bold and italic text**_ using italic outside, bold inside
- **Bold text with `inline code`** inside it
- *Italic text with **bold** inside it*
- ~~Strikethrough with [links](https://example.com) inside~~
- **Bold _italic_ mixed with regular** text in the same line

### Complex Mixed Content

> Here's a blockquote with a [link](https://example.com) and some **bold text**.
> 
> 1. It includes an ordered list
> 2. With multiple items
>    * And nested unordered items
>    * With more [links](https://example.org)
> 
> ```python
> # Even code blocks inside blockquotes
> print("Hello from a blockquote!")
> ```

This test file covers all the **essential** features to implement and test[^final].

[^final]: A final footnote at the end of the document.