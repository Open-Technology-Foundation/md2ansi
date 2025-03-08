#!/bin/bash
set -euo pipefail

(($#)) || {
  >&2 echo "usage: md file.md"
  >&2 echo "Pipes an mdfile through less"
  exit 1
}

md2ansi "$1" |less

#fin
