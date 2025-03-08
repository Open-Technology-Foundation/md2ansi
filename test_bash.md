```bash
# Process a single markdown file
md2ansi README.md

# Process multiple files
md2ansi file1.md file2.md

# Process markdown from stdin and pipe to less
cat README.md | md2ansi | less
```
