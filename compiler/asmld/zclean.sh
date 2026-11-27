#!/usr/bin/env bash
# ===========================================================================
#  zclean.sh - remove build artifacts produced by zbuild.sh
#
#  Usage:
#    ./zclean.sh          remove build dir, generated version header, and the
#                         executable in output/ (output/ itself is removed
#                         only if nothing else is left in it)
#    ./zclean.sh --all    also remove the whole output/ folder
# ===========================================================================
set -euo pipefail
ZSCRIPT=zclean

SELF="$(readlink -f "${BASH_SOURCE[0]}")"
cd "$(dirname "$SELF")" || { echo "cannot enter project root" >&2; exit 1; }
source ./zhead.sh

ALL=0
for arg in "$@"; do
    case "$arg" in
        -a|--all)  ALL=1 ;;
        -h|--help) sed -n '3,9p' "$SELF" | sed 's/^# \{0,2\}//'; exit 0 ;;
        *)         fail "unknown option: $arg" ;;
    esac
done

# Guard against a misconfigured folder name wiping something important.
for d in "$BUILD_DIR" "$OUTPUT_DIR"; do
    case "$d" in ""|"."|".."|"/"|"~") fail "refusing to clean suspicious folder \"$d\"" ;; esac
done

remove() {
    if [[ -e "$1" ]]; then rm -rf -- "$1"; log "removed $1"; fi
}

remove "$BUILD_DIR"
remove "$VERSION_HEADER"

if [[ "$ALL" -eq 1 ]]; then
    remove "$OUTPUT_DIR"
else
    remove "$OUTPUT_DIR/$EXEC_NAME.exe"
    remove "$OUTPUT_DIR/$EXEC_NAME"
    if [[ -d "$OUTPUT_DIR" ]] && rmdir "$OUTPUT_DIR" 2>/dev/null; then
        log "removed empty $OUTPUT_DIR"
    fi
fi

# Remove the header's folder too if the generated header was all it held.
rmdir "$(dirname "$VERSION_HEADER")" 2>/dev/null || true

log "Clean."
