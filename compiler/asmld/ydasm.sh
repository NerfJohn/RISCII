#!/usr/bin/env bash
# ===========================================================================
#  ydasm.sh - shortcut to a (multi-file) Python script
#
#  Usage:
#    ./ydasm.sh [args...]     every argument is passed on to the Python script
#
#  File paths among the arguments are made absolute (relative to the folder
#  you ran ydasm.sh from), so they still point at the right file whatever
#  folder Python runs in. On Windows (Git Bash / MSYS2) they are also
#  converted to Windows form (C:/...) so a native python.exe understands them.
#
#  An argument counts as a path if it exists, or if it contains a "/" and
#  its parent folder exists (so output files that don't exist yet work too).
#  Arguments starting with "-" are passed through untouched; for options with
#  a path (e.g. --out=dir/x.txt), the part after "=" is converted.
#
#  Each setting below can be overridden from the environment for one run,
#  e.g.  YDASM_RUN_DIR=script ./ydasm.sh input.bin
# ===========================================================================
set -euo pipefail

# ------------------------------ configuration ------------------------------
# Entry point of the Python script. Either:
#   - a .py file              e.g.  tools/dasm/main.py
#   - a folder with a __main__.py inside (run as  python <folder>)
# A relative path is relative to the folder this shell script lives in.
YDASM_SCRIPT="../../tools/dasm/src/main.py"

# Python command. Leave empty to auto-detect (python3, python, then py -3).
# Can include arguments, e.g.  "py -3.12"  or  "/c/Python312/python.exe"
YDASM_PYTHON="${YDASM_PYTHON:-}"

# Working folder Python runs in:
#   (empty, default)  the folder you ran ydasm.sh from
#   script            the Python script's own folder (use this if it loads
#                     data files relative to the current folder)
#   any other path    relative to this shell script's folder, or absolute
YDASM_RUN_DIR="${YDASM_RUN_DIR:-}"
# ---------------------------------------------------------------------------

fail() { echo "[ydasm] ERROR: $*" >&2; exit 1; }

# Resolve through symlinks, so a link to this file on your PATH works too.
HERE="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

HAVE_CYGPATH=0
command -v cygpath >/dev/null 2>&1 && HAVE_CYGPATH=1

# to_abs <path>  -> absolute path (Windows form when cygpath is available)
to_abs() {
    local p
    p="$(realpath -m -- "$1")"
    if [[ "$HAVE_CYGPATH" -eq 1 ]]; then p="$(cygpath -m -- "$p")"; fi
    echo "$p"
}

# looks_like_path <arg>
looks_like_path() {
    [[ -e "$1" ]] && return 0
    [[ "$1" == */* && -d "$(dirname -- "$1")" ]]
}

# ------------------------------ locate script -------------------------------
SCRIPT="$YDASM_SCRIPT"
[[ "$SCRIPT" = /* ]] || SCRIPT="$HERE/$SCRIPT"
SCRIPT="$(realpath -m -- "$SCRIPT")"

if [[ -d "$SCRIPT" ]]; then
    [[ -f "$SCRIPT/__main__.py" ]] || fail "folder \"$SCRIPT\" has no __main__.py"
    SCRIPT_DIR="$SCRIPT"
elif [[ -f "$SCRIPT" ]]; then
    SCRIPT_DIR="$(dirname "$SCRIPT")"
else
    fail "Python script not found: $SCRIPT (set YDASM_SCRIPT in ydasm.sh)"
fi

# ------------------------------ locate python -------------------------------
if [[ -n "$YDASM_PYTHON" ]]; then
    read -r -a PY_CMD <<< "$YDASM_PYTHON"
    command -v "${PY_CMD[0]}" >/dev/null 2>&1 \
        || fail "Python command \"${PY_CMD[0]}\" not found (check YDASM_PYTHON in ydasm.sh)"
else
    PY_CMD=()
    # Actually run each candidate: on Windows "python3" may be a Store stub.
    for cand in "python3" "python" "py -3"; do
        read -r -a try <<< "$cand"
        if command -v "${try[0]}" >/dev/null 2>&1 \
           && "${try[@]}" -c 'import sys; sys.exit(sys.version_info[0] != 3)' >/dev/null 2>&1; then
            PY_CMD=("${try[@]}"); break
        fi
    done
    [[ ${#PY_CMD[@]} -gt 0 ]] || fail "no Python 3 found (set YDASM_PYTHON in ydasm.sh)"
fi

# ------------------------------ convert args --------------------------------
ARGS=()
for arg in "$@"; do
    if [[ "$arg" == -* ]]; then
        # --opt=path  -> convert the value part only
        if [[ "$arg" == --*=* ]]; then
            opt="${arg%%=*}"; val="${arg#*=}"
            if [[ -n "$val" ]] && looks_like_path "$val"; then
                arg="$opt=$(to_abs "$val")"
            fi
        fi
    elif looks_like_path "$arg"; then
        arg="$(to_abs "$arg")"
    fi
    ARGS+=("$arg")
done

# ------------------------------ run -----------------------------------------
case "$YDASM_RUN_DIR" in
    "")      ;;
    script)  cd "$SCRIPT_DIR" ;;
    /*)      cd "$YDASM_RUN_DIR" || fail "cannot enter \"$YDASM_RUN_DIR\"" ;;
    *)       cd "$HERE/$YDASM_RUN_DIR" || fail "cannot enter \"$HERE/$YDASM_RUN_DIR\"" ;;
esac

SCRIPT_ARG="$SCRIPT"
[[ "$HAVE_CYGPATH" -eq 1 ]] && SCRIPT_ARG="$(cygpath -m -- "$SCRIPT")"

# exec hands over the process, so the script's exit code is ydasm's exit code.
exec "${PY_CMD[@]}" "$SCRIPT_ARG" ${ARGS[@]+"${ARGS[@]}"}