# Code Block Tests

## Python Code

```python
def hello_world():
    """A simple hello world function."""
    print("Hello, World!")
    return True

# Call the function
if __name__ == "__main__":
    hello_world()
```

## JavaScript Code

```javascript
function factorial(n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

console.log(factorial(5)); // Output: 120
```

## Bash Code

```bash
#!/bin/bash
# A simple bash script

echo "Starting script..."

for i in {1..5}; do
    echo "Iteration $i"
done

echo "Script complete!"
```

## Code without Language

```
This is a code block without syntax highlighting.
It should still be formatted as code.
```

## Inline Code Examples

Use the `print()` function in Python.

The `console.log()` method in JavaScript.

Run `ls -la` to list files.