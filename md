#!/bin/bash
set -euo pipefail

(($#)) || {
  >&2 echo "usage: md file.md"
  >&2 echo "Wrapper script for md2ansi, to pipe a markdown file through less."
  exit 1
}

export LESS='-FXRS'

md2ansi "$@" | less

#fin
