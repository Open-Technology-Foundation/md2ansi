#!/bin/bash
set -euo pipefail
export LESS='-FXRS'
md2ansi "$@" | less
#fin
