#!/usr/bin/env bash
# coralline theme picker — browse every installed theme with a LIVE statusline
# preview and apply the one you like. Pure bash, no dependencies.
#
#   ↑/↓ or j/k   move          u/d   jump half a page
#   enter        apply & quit  q     quit without changing
#
# Preview & apply both work by cloning your real ~/.claude/coralline.conf and
# swapping only its theme `source` line, so VL_LAYOUT / VL_CTX_TOKENS / etc.
# are preserved exactly as you have them.

set -u

# Resolve paths relative to this script's location so the picker works both
# from a cloned repo and from an installed ~/.claude/coralline/ (same layout:
# statusline.sh + themes/ + tools/ are siblings).
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SELF")"
THEMES_DIR="$ROOT/themes"
STATUSLINE="$ROOT/statusline.sh"
# The config we read/apply to is your live one (override with CORALLINE_CONFIG).
CONF="${CORALLINE_CONFIG:-$HOME/.claude/coralline.conf}"
TMP="$(mktemp -t coralline-preview)"
trap 'rm -f "$TMP"; printf "\033[?25h"' EXIT   # restore cursor on exit

# Canned payload — points at the coralline repo so the git segment renders.
PAYLOAD='{"workspace":{"current_dir":"'"$ROOT"'"},"model":{"display_name":"Opus 4.8"},"context_window":{"used_percentage":62,"total_input_tokens":124000,"total_output_tokens":45600,"current_usage":{"cache_read_input_tokens":1200000,"cache_creation_input_tokens":8000}},"cost":{"total_cost_usd":1.23},"cost_usd":1.23}'

# ── Collect themes: top-level + best-themes/, as "label<TAB>path" ──────────────
PATHS=(); LABELS=()
add() { LABELS+=("$1"); PATHS+=("$2"); }
for f in "$THEMES_DIR"/*.conf; do
  [ -e "$f" ] || continue
  add "$(basename "$f" .conf)" "$f"
done
for f in "$THEMES_DIR"/best-themes/*.conf; do
  [ -e "$f" ] || continue
  add "best-themes/$(basename "$f" .conf)" "$f"
done
N=${#PATHS[@]}
if [ "$N" -eq 0 ]; then echo "No themes found in $THEMES_DIR"; exit 1; fi

# Write a config that sources $1 but keeps every non-theme line from $CONF.
# (If $CONF is missing, just source the theme.)
clone_conf() {
  local theme="$1" out="$2" replaced=0 line
  : > "$out"
  if [ -f "$CONF" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
      case "$line" in
        .\ *themes/*.conf|source\ *themes/*.conf)
          printf '. %s\n' "$theme" >> "$out"; replaced=1 ;;
        *) printf '%s\n' "$line" >> "$out" ;;
      esac
    done < "$CONF"
  fi
  [ "$replaced" -eq 1 ] || printf '. %s\n' "$theme" >> "$out"
}

render() {  # render theme path $1 to stdout
  clone_conf "$1" "$TMP"
  printf '%s' "$PAYLOAD" | CORALLINE_CONFIG="$TMP" bash "$STATUSLINE" 2>/dev/null
}

cur=0; win=12   # names shown around the cursor
draw() {
  printf '\033[H\033[J'                       # home + clear
  printf '\033[1m  coralline theme picker\033[0m  —  %d/%d themes\n' "$((cur+1))" "$N"
  printf '\033[2m  ↑/↓ j/k move · u/d page · enter apply · q quit\033[0m\n\n'
  printf '  \033[2mpreview:\033[0m\n  '
  render "${PATHS[$cur]}"
  printf '\n\n'
  local start=$(( cur - win/2 ))
  [ "$start" -lt 0 ] && start=0
  local end=$(( start + win ))
  [ "$end" -gt "$N" ] && { end=$N; start=$(( end - win )); [ "$start" -lt 0 ] && start=0; }
  local i
  for (( i=start; i<end; i++ )); do
    if [ "$i" -eq "$cur" ]; then
      printf '  \033[1;38;5;213m▸ %s\033[0m\n' "${LABELS[$i]}"
    else
      printf '    \033[2m%s\033[0m\n' "${LABELS[$i]}"
    fi
  done
}

apply() {  # write chosen theme into the real config
  clone_conf "$1" "$TMP"
  cp "$TMP" "$CONF"
}

printf '\033[?25l'   # hide cursor
while :; do
  draw
  IFS= read -rsn1 key
  if [ "$key" = $'\033' ]; then        # escape sequence (arrow keys)
    IFS= read -rsn2 -t 1 rest 2>/dev/null
    key="$key$rest"
  fi
  case "$key" in
    $'\033[A'|k) [ "$cur" -gt 0 ] && cur=$((cur-1)) ;;
    $'\033[B'|j) [ "$cur" -lt $((N-1)) ] && cur=$((cur+1)) ;;
    u) cur=$((cur - win/2)); [ "$cur" -lt 0 ] && cur=0 ;;
    d) cur=$((cur + win/2)); [ "$cur" -gt $((N-1)) ] && cur=$((N-1)) ;;
    g) cur=0 ;;
    G) cur=$((N-1)) ;;
    ""|$'\n'|$'\r')                      # enter
      apply "${PATHS[$cur]}"
      printf '\033[H\033[J'
      printf '\033[1m✓ applied:\033[0m %s\n' "${LABELS[$cur]}"
      printf '  written to %s\n' "$CONF"
      printf '  the statusline redraws every second — it is live now.\n'
      exit 0 ;;
    q|Q) printf '\033[H\033[J'; printf 'no change.\n'; exit 0 ;;
  esac
done
