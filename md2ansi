#!/bin/bash
#shellcheck disable=SC2034
set -e
declare -- _ent_0=$(readlink -fn -- "$0") || _ent_0=''
declare -- PRG=${_ent_0##*/}
declare -- PRGDIR=${_ent_0%/*}
declare -- version='0.4.20'

md2ansi() {
  # Borrow IFS
  local -I IFS
  # ANSI Colour Palette
  local -- \
    CODE_BLOCK='\x1b[90m' \
    TABLE_BLOCK='\x1b[90m' \
    HORIZONTAL_RULE='\x1b[36m' \
    BLOCKQUOTE='\x1b[35m'
  local -a ITALICS=(        '\x1b[2m' '\x1b[22m' ) # dim on-off
  local -a BOLD=(           '\x1b[1m' '\x1b[22m' ) # bold on-off
  local -a STRIKETHROUGH=(  '\x1b[9m' '\x1b[29m' ) # strikethrough on-off
  local -a INLINE_CODE=(    '\x1b[2m' '\x1b[22m' ) # dim on-off
  local -- \
    LIST='\x1b[36m' \
    H1='\x1b[31;1m' \
    H2='\x1b[32;1m' \
    H3='\x1b[33;1m' \
    H4='\x1b[33m' \
    H5='\x1b[34;1m' \
    H6='\x1b[34m' \
    RESET='\x1b[0m'
  local -- line=''
  while IFS= read -r line; do
    # Code Block ^``` ^~~~
    if [[ "${line:0:3}" == '```' || "${line:0:3}" == '~~~' ]]; then
      echo -e "${CODE_BLOCK}~~~${line:3}"
      while IFS= read -r line; do
        [[ "${line:0:3}" == '```' || "${line:0:3}" == '~~~' ]] \
          && break
        echo -e "    ${CODE_BLOCK}${line}"
      done
      echo -e "${CODE_BLOCK}~~~${RESET}"
      continue
    fi

    # Tables ^[space]|space
    if [[ $line =~ ^[[:space:]]*\| ]]; then
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
          && _line="${line:0:${#_line}-1}"
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
      echo -e "$RESET"
      unset _cols _max_widths _cols_n _i _col _row _lineoff
      continue
    fi

    # Horizontal_Rules ^--- ^=== ^___
    if [[ ${line:0:3} == '---' ||  ${line:0:3} == '==='  ||  ${line:0:3} == '___' ]]; then
      echo -e "\r$(head -c "$((${COLUMNS:-78} - 1))" < /dev/zero | tr '\0' "${line:0:1}")"
      continue
    fi

    # Blockquotes ^\>
    if [[ "$line" =~ ^\> ]]; then
      echo "$line" | sed -E "s/^> (.*)/  ${BLOCKQUOTE}> \1${RESET}/"
      continue
    fi

    # Bold **
    line=$(echo "$line" | sed -E "s/\*\*(.*?)\*\*/${BOLD[0]}\1${BOLD[1]}/g")

    # Italics *
    line=$(echo "$line" | sed -E "s/\*(.*?)\*/${ITALICS[0]}\1${ITALICS[1]}/g")

    # Strikethrough ~~
    line=$(echo "$line" | sed -E "s/\~\~(.*?)\~\~/${STRIKETHROUGH[0]}\1${STRIKETHROUGH[1]}/g")

    # Inline_Code `(.*?)`
    #line=$(echo "$line" | sed -E "s/\`(.*?)\`/${INLINE_CODE[0]}\1${INLINE_CODE[1]}/g")
    line=$(transform_line "$line")

    # List ^[space]*\*space[.*]
    line=$(echo "$line" | sed -E "s/^[ ]*\* (.*)/    ${LIST}* \1${RESET}/")
    # List ^[space]*\-space[.*]
    line=$(echo "$line" | sed -E "s/^[ ]*\- (.*)/    ${LIST}- \1${RESET}/")
    # If it *is* a list line, print it out, get to next line.
    if [[ "$line" =~ ^[[:space:]]*[*-] ]]; then
      echo -e "$line"
      continue
    fi

    # Headers ^#..#space(.*)
    line=$(echo "$line" | sed -E "s/^###### (.*)/${H6}\1${RESET}/")
    line=$(echo "$line" | sed -E "s/^##### (.*)/${H5}\1${RESET}/")
    line=$(echo "$line" | sed -E "s/^#### (.*)/${H4}\1${RESET}/")
    line=$(echo "$line" | sed -E "s/^### (.*)/${H3}\1${RESET}/")
    line=$(echo "$line" | sed -E "s/^## (.*)/${H2}\1${RESET}/")
    line=$(echo "$line" | sed -E "s/^# (.*)/${H1}\1${RESET}/")

    echo -e "$line"  | fmt -w ${COLUMNS:-78}
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
    new_line+="${INLINE_CODE[0]}${segment}${INLINE_CODE[1]}"
    line="${line#*\`}"
  done
  new_line+="$line"
  echo -ne "$new_line"
}
# Example usage
#INLINE_CODE=('\x1b[97m' '\x1b[0m')
#line="This is `inline code` and this is another `inline code`."
#transformed_line=$(transform_line "$line")
#echo -e "$transformed_line"

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

# In script.sh
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
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
