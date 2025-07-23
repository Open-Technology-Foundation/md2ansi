# Bash Completion for md2ansi

This directory contains bash completion support for the `md2ansi` and `md` commands.

## Features

- Completes only `.md` files (directories are excluded for cleaner completion)
- Completes all command-line options including:
  - Short options: `-h`, `-V`, `-D`
  - Long options: `--help`, `--version`, `--debug`, `--width`, `--plain`
  - Feature toggles: `--no-footnotes`, `--no-syntax-highlight`, `--no-tables`, etc.
- Provides value suggestions for `--width` option (80, 100, 120, 140, 160, 180, 200)
- Works for both `md2ansi` and `md` commands
- Handles files with spaces in their names

## Installation

### Automatic Installation (via md2ansi-install.sh)

The bash completion is automatically installed when you use the main installation script:

```bash
# This will install md2ansi AND bash completion
./md2ansi-install.sh

# Or via curl
curl -sL https://raw.githubusercontent.com/Open-Technology-Foundation/md2ansi/main/md2ansi-install.sh | bash
```

The installation script automatically:
- Checks if `/etc/bash_completion.d/` exists
- Copies the completion file if the directory is available
- The completion will be available in new shell sessions

### Manual System-wide Installation

If you need to install just the completion manually:

```bash
# Copy to system bash completion directory
sudo cp bash-completion/md2ansi /etc/bash_completion.d/

# Reload bash completions (or start a new shell)
source /etc/bash_completion
```

### User-specific Installation

For installing completion just for your user:

```bash
# Create user completion directory if it doesn't exist
mkdir -p ~/.local/share/bash-completion/completions

# Copy completion script
cp bash-completion/md2ansi ~/.local/share/bash-completion/completions/

# Add to bashrc if not already present
grep -q 'bash-completion/completions/md2ansi' ~/.bashrc || \
  echo 'source ~/.local/share/bash-completion/completions/md2ansi' >> ~/.bashrc

# Reload bashrc
source ~/.bashrc
```

### Temporary Loading

To test or use temporarily in current shell:

```bash
source /path/to/md2ansi/bash-completion/md2ansi
```

## Usage

After installation, use Tab to complete:

```bash
# Complete markdown files only (not directories)
md2ansi RE<Tab>          # Completes to README.md
md <Tab>                 # Shows all .md files in current directory
md2ansi test<Tab>        # Shows all .md files starting with "test"

# Complete files in subdirectories
md2ansi docs/IN<Tab>     # Completes to docs/INSTALL.md

# Complete options
md2ansi --<Tab>          # Shows all available long options
md2ansi -<Tab>           # Shows all available short options
md2ansi --no-<Tab>       # Shows all --no- options

# Complete width values
md2ansi --width <Tab>    # Shows: 80 100 120 140 160 180 200

# Multiple arguments
md2ansi README.md --<Tab> # Options still complete after filenames
```

## How It Works

The completion script (`md2ansi`) uses bash's `compgen` command to:
1. Filter files to show only those with `.md` extension
2. Provide option completion when the current word starts with `-`
3. Suggest common terminal widths after `--width`
4. Register the same completion function for both `md2ansi` and `md` commands

## Testing

To verify completion is working:

```bash
# Check if completion is registered
complete -p md2ansi
complete -p md

# Test file completion
touch test.md test.txt
md2ansi t<Tab>  # Should only show test.md, not test.txt

# Test option completion
md2ansi --no-<Tab>  # Should show all --no- options
```

## Troubleshooting

If completion doesn't work:

1. **Check bash-completion is installed:**
   ```bash
   # Debian/Ubuntu
   sudo apt-get install bash-completion
   
   # Fedora/RHEL/CentOS
   sudo dnf install bash-completion
   
   # Arch Linux
   sudo pacman -S bash-completion
   
   # macOS (via Homebrew)
   brew install bash-completion
   ```

2. **Verify completion is loaded:**
   ```bash
   # Should show the completion function
   complete -p md2ansi 2>/dev/null || echo "Not loaded"
   ```

3. **Check bash version:**
   ```bash
   # Requires bash 4.0+
   bash --version
   ```

4. **Manually source the completion:**
   ```bash
   source /etc/bash_completion.d/md2ansi
   # or
   source ~/.local/share/bash-completion/completions/md2ansi
   ```

5. **Start a new shell:**
   Sometimes completions only load in new shell sessions.

## Uninstallation

The completion is automatically removed when running:

```bash
./md2ansi-install.sh --uninstall
```

Or manually remove with:

```bash
# System-wide
sudo rm -f /etc/bash_completion.d/md2ansi

# User-specific
rm -f ~/.local/share/bash-completion/completions/md2ansi
# Also remove the source line from ~/.bashrc
```

## Development

To modify the completion behavior, edit the `_md2ansi_complete()` function in the `md2ansi` file. Key variables:
- `$cur`: Current word being completed
- `$prev`: Previous word on the command line
- `$COMPREPLY`: Array of possible completions

The script avoids showing directories to keep the completion list focused on markdown files only.