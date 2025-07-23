#!/bin/bash
# md2ansi-install.sh - System-wide installation script for md2ansi
#
# This script installs md2ansi and its associated tools system-wide by:
# 1. Cloning the repository to /usr/local/share/md2ansi
# 2. Setting executable permissions on scripts
# 3. Creating symlinks in /usr/local/bin for easy access
# 4. Installing bash completion support (optional)
# 5. Generating and installing man page (optional)
#
# Usage: ./md2ansi-install.sh [--help|--uninstall]
#        curl -sL https://raw.githubusercontent.com/Open-Technology-Foundation/md2ansi/main/md2ansi-install.sh | bash
#
# Requirements: sudo access, git, bash 5+
# Security: Script uses 'set -euo pipefail' for safe execution

set -euo pipefail

# Display usage information if requested
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
  cat << EOF
md2ansi Installation Script

Usage: $0 [options]

Options:
  -h, --help     Show this help message and exit
  --uninstall    Remove md2ansi installation

This script installs md2ansi system-wide by:
- Cloning the repository to /usr/local/share/md2ansi
- Creating symlinks in /usr/local/bin for 'md2ansi' and 'md' commands
- Setting proper executable permissions
- Installing bash completion (if /etc/bash_completion.d exists)
- Generating and installing man page (if prerequisites are met)

Requirements:
- sudo access for system-wide installation
- git for cloning the repository
- bash 5+ for script compatibility

After installation:
- Run 'md2ansi --help' for usage information
- Run 'man md2ansi' to view the manual page
EOF
  exit 0
fi

# Handle uninstall option
if [[ "${1:-}" == "--uninstall" ]]; then
  echo "Uninstalling md2ansi..."
  
  # Remove symlinks
  sudo rm -f /usr/local/bin/md2ansi /usr/local/bin/md
  
  # Remove bash completion
  sudo rm -f /etc/bash_completion.d/md2ansi
  
  # Remove man pages
  for dir in /usr/local/share/man/man1 /usr/share/man/man1 /usr/man/man1; do
    sudo rm -f "$dir/md2ansi.1" "$dir/md2ansi.1.gz" 2>/dev/null || true
  done
  
  # Remove installation directory
  sudo rm -rf /usr/local/share/md2ansi
  
  # Update man database if available
  if command -v mandb &> /dev/null; then
    sudo mandb -q 2>/dev/null || true
  fi
  
  echo "✓ md2ansi has been uninstalled."
  exit 0
fi

declare -- sharedir=/usr/local/share/md2ansi

if [[ -d "$sharedir" ]]; then
  echo "Directory '$sharedir' already exists."
  echo "This must be deleted first before executing git clone"
  read -r -p "Do you wish to delete this directory? y/n " yn
  [[ $yn == 'y' ]] || exit 1
  sudo rm -rf "$sharedir"
fi

# Check prerequisites
if ! command -v git &> /dev/null; then
  echo "ERROR: git is not installed. Please install git first."
  exit 1
fi

echo "Cloning md2ansi repository..."
if ! sudo git clone -q https://github.com/Open-Technology-Foundation/md2ansi "$sharedir"; then
  echo "ERROR: Failed to clone repository. Please check your internet connection."
  exit 1
fi

cd "$sharedir"
echo "Setting executable permissions..."
sudo chmod +x md2ansi.py md2ansi md display_ansi_palette md-link-extract md2ansi-create-manpage.sh 2>/dev/null || true

echo "Creating symbolic links..."
sudo ln -sf "$sharedir"/md2ansi /usr/local/bin/md2ansi
sudo ln -sf "$sharedir"/md /usr/local/bin/md

# Install bash completion if directory exists
if [[ -d /etc/bash_completion.d/ ]] && [[ -f "$sharedir/bash-completion/md2ansi" ]]; then
  echo "Installing bash completion..."
  sudo cp "$sharedir/bash-completion/md2ansi" /etc/bash_completion.d/
fi

# Generate and install man page
if [[ -f "$sharedir/md2ansi-create-manpage.sh" ]] && [[ -f "$sharedir/README.md" ]]; then
  echo "Generating and installing man page..."
  cd "$sharedir"
  # Make sure the script is executable
  sudo chmod +x md2ansi-create-manpage.sh 2>/dev/null || true
  # Run as sudo since we're in a directory owned by root
  if sudo ./md2ansi-create-manpage.sh --install >/dev/null 2>&1; then
    echo "Man page installed successfully"
  else
    echo "Warning: Could not install man page (this is optional)"
  fi
else
  echo "Warning: Man page generation script or README.md not found (this is optional)"
fi

echo
echo "✓ md2ansi has been successfully installed!"
echo
echo "Available commands:"
echo "  md2ansi [file.md]  - Convert markdown to ANSI-colored output"
echo "  md [file.md]       - View markdown with pager (less)"
echo
echo "Documentation:"
echo "  md2ansi --help                - Show command options"
echo "  man md2ansi                   - View manual page"
echo "  md $sharedir/README.md  - View full documentation"

#fin
