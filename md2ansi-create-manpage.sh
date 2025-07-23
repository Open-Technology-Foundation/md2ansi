#!/bin/bash
# md2ansi-create-manpage.sh - Generate and install man page for md2ansi
#
# This script creates a man page from README.md and installs it system-wide
# The man page is created in troff format for compatibility with the man system
#
# Usage: ./md2ansi-create-manpage.sh [--install|--uninstall]

set -euo pipefail

# Configuration
declare -r SCRIPT_NAME="md2ansi"
declare -r MAN_SECTION="1"  # User commands section
declare -r MAN_FILE="${SCRIPT_NAME}.${MAN_SECTION}"
declare -r README_FILE="README.md"
declare -r OUTPUT_FILE="md2ansi.manpage"
declare -r TEMP_FILE="/tmp/${SCRIPT_NAME}.${MAN_SECTION}.tmp"

# Man page installation directories (in order of preference)
declare -a MAN_DIRS=(
  "/usr/local/share/man/man${MAN_SECTION}"
  "/usr/share/man/man${MAN_SECTION}"
  "/usr/man/man${MAN_SECTION}"
)

# Display usage
usage() {
  cat << EOF
md2ansi Man Page Generator

Usage: $0 [options]

Options:
  -h, --help       Show this help message
  --install        Generate and install the man page (requires sudo)
  --uninstall      Remove installed man page (requires sudo)
  --preview        Preview the generated man page
  --no-install     Only generate, don't install (default)

This script generates a man page from README.md in troff format.
The generated file is saved as ${OUTPUT_FILE}.

After installation, you can view the man page with:
  man md2ansi
EOF
}

# Check if README exists
check_readme() {
  if [[ ! -f "$README_FILE" ]]; then
    echo "ERROR: $README_FILE not found in current directory"
    exit 1
  fi
}

# Generate man page header
generate_header() {
  local date=$(date +"%B %Y")
  cat << EOF
.\" Man page for md2ansi
.\" Generated from README.md by md2ansi-create-manpage.sh
.TH MD2ANSI ${MAN_SECTION} "${date}" "md2ansi 0.9.5" "User Commands"
.SH NAME
md2ansi \- Convert Markdown to ANSI-colored text in the terminal
.SH SYNOPSIS
.B md2ansi
[\fIFILE\fR...]
[\fIOPTIONS\fR]
.br
.B md
[\fIFILE\fR]
.br
\fIcommand\fR |
.B md2ansi
.SH DESCRIPTION
.B md2ansi
is a Python-based Markdown to ANSI terminal formatter that renders markdown files
with color and style directly in your terminal. It supports headers, lists, tables,
code blocks with syntax highlighting, and more.
.PP
The tool requires no external Python dependencies and works with any terminal
that supports 256-color ANSI sequences.
EOF
}

# Extract and format command line options
generate_options() {
  cat << 'EOF'
.SH OPTIONS
.TP
.BR \-h ", " \-\-help
Show help message and exit
.TP
.BR \-V ", " \-\-version
Show version information and exit
.TP
.BR \-D ", " \-\-debug
Enable debug mode (reserved for future use)
.TP
.BI \-\-width " WIDTH"
Force specific terminal width (default: auto-detect)
.TP
.B \-\-no\-footnotes
Disable footnotes processing
.TP
.B \-\-no\-syntax\-highlight
Disable syntax highlighting in code blocks
.TP
.B \-\-no\-tables
Disable tables formatting
.TP
.B \-\-no\-task\-lists
Disable task lists (checkboxes) formatting
.TP
.B \-\-no\-images
Disable image placeholders
.TP
.B \-\-no\-links
Disable links formatting
.TP
.B \-\-plain
Use plain text mode (disables all formatting features)
EOF
}

# Generate examples section
generate_examples() {
  cat << 'EOF'
.SH EXAMPLES
View a single markdown file:
.PP
.RS 4
md2ansi README.md
.RE
.PP
View with pager for long files:
.PP
.RS 4
md README.md
.RE
.PP
Process multiple files:
.PP
.RS 4
md2ansi *.md
.RE
.PP
Process from stdin:
.PP
.RS 4
cat README.md | md2ansi
.br
curl -s https://example.com/README.md | md2ansi
.RE
.PP
Force specific terminal width:
.PP
.RS 4
md2ansi --width 100 README.md
.RE
.PP
Disable specific features:
.PP
.RS 4
md2ansi --no-syntax-highlight --no-tables README.md
.RE
.PP
Plain text mode:
.PP
.RS 4
md2ansi --plain README.md
.RE
EOF
}

# Generate features section
generate_features() {
  cat << 'EOF'
.SH FEATURES
.SS Headers
H1-H6 headers with distinct color gradients from yellow to purple
.SS Lists
.IP \(bu 2
Unordered lists with proper nesting and indentation
.IP \(bu 2
Ordered lists with automatic numbering
.IP \(bu 2
Task lists with checkboxes ([ ] and [x])
.SS Code Blocks
.IP \(bu 2
Fenced with \fB```\fR or \fB~~~\fR with language detection
.IP \(bu 2
Syntax highlighting for Python, JavaScript, and Bash
.IP \(bu 2
Support for language aliases (py, js, sh, shell)
.IP \(bu 2
ANSI escape sequence sanitization
.SS Tables
.IP \(bu 2
Pipe-delimited with alignment support
.IP \(bu 2
Enhanced formatting with mixed styling in cells
.IP \(bu 2
Handles mismatched column counts gracefully
.SS Inline Formatting
.IP \(bu 2
\fBBold\fR text rendering
.IP \(bu 2
\fIItalic\fR text rendering
.IP \(bu 2
Strikethrough text rendering
.IP \(bu 2
Inline code with distinct styling
.IP \(bu 2
Links with underlined styling
.IP \(bu 2
Image alt text placeholders
.IP \(bu 2
Footnote references with automatic collection
EOF
}

# Generate security section
generate_security() {
  cat << 'EOF'
.SH SECURITY
md2ansi includes several security features:
.IP \(bu 2
Files larger than 10MB are rejected for safety
.IP \(bu 2
ANSI escape sequences in input are sanitized
.IP \(bu 2
Safe handling of special characters in filenames
.IP \(bu 2
Command injection prevention in utility scripts
.IP \(bu 2
Graceful signal handling with terminal reset
EOF
}

# Generate files and environment sections
generate_files() {
  cat << 'EOF'
.SH FILES
.TP
.I /usr/local/share/md2ansi/
Installation directory containing all md2ansi scripts
.TP
.I /usr/local/bin/md2ansi
Symbolic link to the main converter script
.TP
.I /usr/local/bin/md
Symbolic link to the pager wrapper script
.TP
.I /etc/bash_completion.d/md2ansi
Bash completion configuration (if installed)
.SH ENVIRONMENT
.TP
.B COLUMNS
If set, used as fallback for terminal width detection
.TP
.B LESS
Used by the \fBmd\fR wrapper script (set to '-FXRS')
EOF
}

# Generate footer sections
generate_footer() {
  cat << 'EOF'
.SH EXIT STATUS
.TP
.B 0
Successful execution
.TP
.B 1
General error (file not found, invalid options, etc.)
.TP
.B 130
Interrupted by user (Ctrl+C)
.SH SEE ALSO
.BR less (1),
.BR python3 (1),
.BR markdown (1)
.PP
Project homepage: https://github.com/Open-Technology-Foundation/md2ansi
.SH AUTHORS
Indonesian Open Technology Foundation (https://yatti.id)
.SH COPYRIGHT
Copyright © 2022-2025 Indonesian Open Technology Foundation
.PP
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
.SH BUGS
Report bugs at: https://github.com/Open-Technology-Foundation/md2ansi/issues
EOF
}

# Generate complete man page
generate_manpage() {
  echo "Generating man page from $README_FILE..."
  
  {
    generate_header
    echo
    generate_options
    echo
    generate_examples
    echo
    generate_features
    echo
    generate_security
    echo
    generate_files
    echo
    generate_footer
  } > "$OUTPUT_FILE"
  
  echo "Man page generated: $OUTPUT_FILE"
}

# Find suitable man directory
find_man_dir() {
  for dir in "${MAN_DIRS[@]}"; do
    if [[ -d "$(dirname "$dir")" ]]; then
      echo "$dir"
      return 0
    fi
  done
  return 1
}

# Install man page
install_manpage() {
  local man_dir
  
  if ! man_dir=$(find_man_dir); then
    echo "ERROR: No suitable man directory found"
    echo "Tried: ${MAN_DIRS[*]}"
    exit 1
  fi
  
  echo "Installing man page to $man_dir..."
  
  # Create directory if it doesn't exist
  if [[ ! -d "$man_dir" ]]; then
    echo "Creating directory: $man_dir"
    sudo mkdir -p "$man_dir"
  fi
  
  # Copy man page
  sudo cp "$OUTPUT_FILE" "$man_dir/$MAN_FILE"
  
  # Compress with gzip if gzip is available
  if command -v gzip &> /dev/null; then
    echo "Compressing man page..."
    sudo gzip -f "$man_dir/$MAN_FILE"
    echo "Installed: $man_dir/$MAN_FILE.gz"
  else
    echo "Installed: $man_dir/$MAN_FILE"
  fi
  
  # Update man database if mandb is available
  if command -v mandb &> /dev/null; then
    echo "Updating man database..."
    sudo mandb -q
  fi
  
  echo
  echo "✓ Man page installed successfully!"
  echo "You can now use: man md2ansi"
}

# Uninstall man page
uninstall_manpage() {
  local removed=0
  
  echo "Uninstalling md2ansi man page..."
  
  for dir in "${MAN_DIRS[@]}"; do
    for file in "$dir/$MAN_FILE" "$dir/$MAN_FILE.gz"; do
      if [[ -f "$file" ]]; then
        echo "Removing: $file"
        sudo rm -f "$file"
        removed=1
      fi
    done
  done
  
  if [[ $removed -eq 0 ]]; then
    echo "No man page found to remove"
  else
    # Update man database if mandb is available
    if command -v mandb &> /dev/null; then
      echo "Updating man database..."
      sudo mandb -q
    fi
    echo "✓ Man page uninstalled successfully!"
  fi
}

# Preview man page
preview_manpage() {
  if [[ ! -f "$OUTPUT_FILE" ]]; then
    echo "ERROR: $OUTPUT_FILE not found. Run without --preview first."
    exit 1
  fi
  
  echo "Previewing man page (press 'q' to quit)..."
  echo
  
  # Create temporary file for preview
  cp "$OUTPUT_FILE" "$TEMP_FILE"
  
  # Use man to preview
  man "$TEMP_FILE"
  
  # Clean up
  rm -f "$TEMP_FILE"
}

# Main execution
main() {
  local install=0
  local preview=0
  
  # Parse command line arguments
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help)
        usage
        exit 0
        ;;
      --install)
        install=1
        shift
        ;;
      --uninstall)
        uninstall_manpage
        exit 0
        ;;
      --preview)
        preview=1
        shift
        ;;
      --no-install)
        install=0
        shift
        ;;
      *)
        echo "ERROR: Unknown option: $1"
        echo "Run '$0 --help' for usage information"
        exit 1
        ;;
    esac
  done
  
  # Check for README
  check_readme
  
  # Generate man page
  generate_manpage
  
  # Preview if requested
  if [[ $preview -eq 1 ]]; then
    preview_manpage
  fi
  
  # Install if requested
  if [[ $install -eq 1 ]]; then
    install_manpage
  else
    echo
    echo "To install the man page system-wide, run:"
    echo "  $0 --install"
    echo
    echo "To preview the man page, run:"
    echo "  $0 --preview"
  fi
}

# Run main function
main "$@"

#fin