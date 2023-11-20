#!/bin/bash
#shellcheck disable=SC2034
set -e

md2ansi() {
  # try to inherit current global COLUMNS
  declare -Ii COLUMNS
  COLUMNS=${COLUMNS:-$(tput cols 2>/dev/null || echo '78')}
  # Borrow IFS
  declare -I IFS
  # ANSI Colour Palette
  local -- \
    TEXT="\x1b[38;5;7m" \
    CODE_BLOCK="\x1b[90m" \
    TABLE_BLOCK="\x1b[90m" \
    HR="\x1b[36m" \
    BLOCKQUOTE="\x1b[48;5;236m"
  local -a ITALIC=( "\x1b[2m" "\x1b[22m" ) # italics dim on-off
  local -a BOLD=(   "\x1b[1m" "\x1b[22m" ) # bold on-off
  local -a STRIKE=( "\x1b[9m" "\x1b[29m" ) # strikethrough on-off
  local -a CODE=(   "\x1b[2m" "\x1b[22m" ) # dim on-off
  local -- \
    LIST="\x1b[36m" \
    H1="\x1b[38;5;226m" \
    H2="\x1b[38;5;214m" \
    H3="\x1b[38;5;118m" \
    H4="\x1b[38;5;21m"   \
    H5="\x1b[38;5;93m" \
    H6="\x1b[38;5;239m"   \
    RESET="\x1b[0m"
  local -- line=''
  echo -en "$TEXT"
  while IFS= read -r line; do
    # Code Block ^``` ^~~~
    if [[ "${line:0:3}" == '```' || "${line:0:3}" == '~~~' ]]; then
      echo -e "${CODE_BLOCK}~~~${line:3}"
      while IFS= read -r line; do
        [[ "${line:0:3}" == '```' || "${line:0:3}" == '~~~' ]] \
          && break
        echo -e "    ${CODE_BLOCK}${line}"
      done
      echo -e "${CODE_BLOCK}~~~${TEXT}"
      continue
    fi

    # Tables ^[space]|space
    if [[ "$line" =~ ^([[:space:]]*)\|(.*) ]]; then
      table_indent="${#BASH_REMATCH[1]}"
      local -a  _cols=()
      local -ai _max_widths=()
      local -i  _cols_n=0 _i _nextrow=0
      local --  _col _row
      local -A  _table_rows=()
      while [[ $line =~ ^[[:space:]]*\| ]]; do
        line="$(trim -e "$line")"
        # Remove starting and ending '|'
        line="${line:1}"
        ((${#line})) \
          && [[ "${line: -1}" == '|' ]] \
          && _line="${line:0:${#line}-1}"
        # Split the line into columns
        IFS='|' read -ra _cols <<< "${line:1}"
        ((_cols_n)) || _cols_n=${#_cols[@]}
        # Remove leading and trailing spaces from each column
        for _i in "${!_cols[@]}"; do
          _cols[$_i]="$(trim -e "${_cols[$_i]}")"
        done
        # Determine the max width for each column
        for _i in "${!_cols[@]}"; do
          [[ ! -v _max_widths[$_i] ]] && _max_widths[$_i]=0
          ((${#_cols[$_i]} > ${_max_widths[$_i]})) \
            && _max_widths[$_i]=${#_cols[$_i]}
        done
        # Add the column values to table row
        for((_i=0; _i<_cols_n; _i++)); do
          _col="${_cols[$_i]}"
          _table_rows[$_nextrow,$_i]="$_col"
        done
        _nextrow+=1
        IFS= read -r line || break
      done
      unset _col _row
      local -i _col _row=0
      local -- _hdr='|'
      for((_col=0; _col<_cols_n; _col++)); do
        _hdr+="$(printf     " %-${_max_widths[$_col]}s |" "${_table_rows[$_row,$_col]}")"
      done
      local -- _lineoff='|'
      local -a _fmt=()
      _row=1
      for((_col=0; _col<_cols_n; _col++)); do
        _line="${_table_rows[$_row,$_col]}"
        if [[ "$_line" == ':'* ]]; then
          _fmt[$_col]='-'
        elif [[ "$_line" == *':' ]]; then
          _fmt[$_col]=''
        else
          _fmt[$_col]='c'
        fi
        _lineoff+="$(printf " %-${_max_widths[$_col]}s-|" '-' |tr ' ' '-')"
      done
      _lineoff=${_lineoff//\|/\+}
      (
      echo -ne "$TABLE_BLOCK"
      echo "$_lineoff"
      echo "$_hdr"
      echo "$_lineoff"
      for((_row=2; _row<_nextrow; _row++)); do
        echo -n '|'
        for((_col=0; _col<_cols_n; _col++)); do
          if [[ ${_fmt[$_col]} == '-' ]]; then
            printf " %-${_max_widths[$_col]}s |" "${_table_rows[$_row,$_col]}"
          elif [[ ${_fmt[$_col]} == '' ]]; then
            printf " %${_max_widths[$_col]}s |" "${_table_rows[$_row,$_col]}"
          else
            printf ' %s |' "$(center_text ${_max_widths[$_col]} "${_table_rows[$_row,$_col]}")"
          fi
        done
        echo
      done
      echo "$_lineoff"
      echo -e "${RESET}${TEXT}"
      ) | sed "s/^/$(printf '%0.s ' $(seq 1 $table_indent))/"
      unset _cols _max_widths _cols_n _i _col _row _lineoff
      continue
    fi
    table_indent=0

    # Horizontal_Rules ^--- ^=== ^___
    if [[ ${line:0:3} == '---' ||  ${line:0:3} == '==='  ||  ${line:0:3} == '___' ]]; then
      echo -e "\r${HR}$(head -c "$((${COLUMNS:-78} - 1))" < /dev/zero | tr '\0' "${line:0:1}")$RESET"
      continue
    fi

    # Blockquotes ^\>
    if [[ "$line" =~ ^([[:space:]]*)\>(.*) ]]; then
      if((!blockquote_indent)); then
        blockquote_indent="${#BASH_REMATCH[1]}"
      fi
      indent="$(printf '%0.s ' $(seq 1 $blockquote_indent))"
      line="${BASH_REMATCH[2]}"
      ( echo "$line" \
        | fmt --goal=$((COLUMNS-5)) -w $((COLUMNS-5)) ) \
          | sed "s/^/${TEXT}${indent}>${BLOCKQUOTE}/;s/\$/\x1b[K$TEXT/"
      continue
    fi
    blockquote_indent=0

    # Bold **
    line=$(echo "$line" | sed -E "s/\*\*(.*?)\*\*/${BOLD[0]}\1${BOLD[1]}/g")

    # Italics *
    line=$(echo "$line" | sed -E "s/\*(.*?)\*/${ITALIC[0]}\1${ITALIC[1]}/g")

    # Strikethrough ~~
    line=$(echo "$line" | sed -E "s/\~\~(.*?)\~\~/${STRIKE[0]}\1${STRIKE[1]}/g")

    # Inline_Code `(.*?)`
    line=$(transform_line "$line")

    # List ^[space]*\*space[.*]
    line=$(echo "$line" | sed -E "s/^[ ]*\* (.*)/    ${LIST}* \1${TEXT}/")
    # List ^[space]*\-space[.*]
    line=$(echo "$line" | sed -E "s/^[ ]*\- (.*)/    ${LIST}- \1${TEXT}/")
    # If it *is* a list line, print it out, get to next line.
    if [[ "$line" =~ ^[[:space:]]*[*-] ]]; then
      echo -e "$line"
      continue
    fi

    # Headers ^#..#space(.*)
    line=$(echo "$line" | sed -E "s/^###### (.*)/${H6}\1${TEXT}/")
    line=$(echo "$line" | sed -E "s/^##### (.*)/${H5}\1${TEXT}/")
    line=$(echo "$line" | sed -E "s/^#### (.*)/${H4}\1${TEXT}/")
    line=$(echo "$line" | sed -E "s/^### (.*)/${H3}\1${TEXT}/")
    line=$(echo "$line" | sed -E "s/^## (.*)/${H2}\1${TEXT}/")
    line=$(echo "$line" | sed -E "s/^# (.*)/${H1}\1${TEXT}/")

    # get rid of any leading ansi codes before sending
    # through `fmt`
    while [[ $line =~ ^$'\e'\[([0-9\;]*)m(.*) ]]; do
      echo -en "\e[${BASH_REMATCH[1]}m"
      line="${BASH_REMATCH[2]}"
    done
    echo -e "$line"  | fmt --goal=$((COLUMNS-5)) -w ${COLUMNS:-78}
  done
  echo -en "$RESET"
}

transform_line() {
  local -- line="$1" new_line='' segment
  while [[ $line == *"\`"* ]]; do
    segment="${line%%\`*}"
    new_line+="$segment"
    line="${line#*\`}"
    segment="${line%%\`*}"
    new_line+="${CODE[0]}${segment}${CODE[1]}"
    line="${line#*\`}"
  done
  new_line+="$line"
  echo -ne "$new_line"
}

center_text() {
  local -i w=$1; shift
  local -- text
  text=$(trim "$*")
  ((${#text} >= w)) && { echo "${text:0:$w}"; return 0; }
  local -i lpad
  lpad=$(((w - ${#text}) / 2))
  local -i rpad
  rpad=$(((w - ${#text}) - lpad))
  text=$(printf '%s%s%s' "$(printf "%0.s " $(seq 1 $lpad))" \
                  "$text" \
                  "$(printf "%0.s " $(seq 1 $rpad))")
  echo -n "${text:0:$w}"
}
declare -fx center_text

trim() {
  if (($#)); then
    local -- v
    if [[ $1 == '-e' ]]; then
      shift
      v="$(echo -en "$*")"
    else
      v="$*"
    fi
    v="${v#"${v%%[![:blank:]]*}"}"
    echo -n "${v%"${v##*[![:blank:]]}"}"
    return 0
  fi
  if [[ ! -t 0 ]]; then
    local -- REPLY
    while read -r; do
      REPLY="${REPLY#"${REPLY%%[![:blank:]]*}"}"
      echo "${REPLY%"${REPLY##*[![:blank:]]}"}"
    done
  fi
}
declare -fx trim

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then #=====================================
declare -- _ent_0=$(readlink -fn -- "$0") || _ent_0=''
declare -- PRG=${_ent_0##*/}
declare -- PRGDIR=${_ent_0%/*}
declare -- version='0.4.20'
_main() {
  usage() {
  cat <<EOT
Script  : $PRG vs $version
Desc    : Print formatted ANSI output to terminal from Markdown file.md.
Synopsis: $PRG [file.md [...]] [< md_input_stream]
Examples: $PRG < README.md
        : $PRG < *.md
        : $PRG file1.md
        : $PRG file1.md file2.md file3.md <file4.md
EOT
  }
  local -a args=()
  while(($#)); do case "$1" in
    -V|--version) echo "$PRG $version"; return 0 ;;
    -h|--help)    usage; return 0 ;;
    -?|--*)       >&2 echo "$PRG: Invalid option '$1'"; exit 22 ;;
    *)            args+=( "$1" ) ;;
  esac; shift; done
  if ((${#args[@]})); then
    local -- mdfile md=''
    for mdfile in "${args[@]}"; do
      [[ -f "$mdfile" ]] || { >&2 echo "$PRG: File '$mdfile' not found"; exit 1 ; }
      md+=$(cat -s -- "$mdfile"; echo)
    done
    md2ansi <<<"$md"
  fi
  [[ ! -t 0 ]] && md2ansi
}

_main "$@"
fi
#fin
