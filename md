#!/usr/bin/env bash
set -euo pipefail
export LESS='-FXRS'
"$(dirname -- "$(readlink -en -- "$0")")"/md2ansi "$@" | less
#fin
