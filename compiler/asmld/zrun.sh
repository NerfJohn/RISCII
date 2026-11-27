#!/usr/bin/env bash
# ===========================================================================
#  zrun.sh - run the executable built by zbuild.sh
#
#  Usage:
#    ./zrun.sh [args...]      every argument is passed on to the executable
#
#  File paths among the arguments are made absolute (relative to the folder
#  you ran zrun.sh from), so they still point at the right file whatever
#  folder the program runs in. On Windows (Git Bash / MSYS2) they are also
#  converted to Windows form (C:/...) so a native .exe understands them.
#
#  An argument counts as a path if it exists, or if it contains a "/" and
#  its parent folder exists (so output files that don't exist yet work too).
#  Arguments starting with "-" are passed through untouched; for options with
#  a path (e.g. --out=dir/x.txt), the part after "=" is converted.
#
#  RUN_DIR sets the working folder the program runs in:
#    (empty, default)  the folder you ran zrun.sh from
#    output            the output folder (handy if the exe loads files
#                      that sit next to it); any other folder works too,
#                      relative to the project root.
#  e.g.  RUN_DIR=output ./zrun.sh data/input.txt
# ===========================================================================
set -euo pipefail
ZSCRIPT=zrun

# Don't cd: relative paths must be resolved from the caller's folder.
ROOT="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
source "$ROOT/zhead.sh"

RUN_DIR="${RUN_DIR:-}"

EXE="$(exe_path "$ROOT/$OUTPUT_DIR")" \
    || fail "$OUTPUT_DIR/$EXEC_NAME(.exe) not found - run ./zbuild.sh first"

HAVE_CYGPATH=0
command -v cygpath >/dev/null 2>&1 && HAVE_CYGPATH=1

# looks_like_path <arg>
looks_like_path() {
    [[ -e "$1" ]] && return 0
    [[ "$1" == */* && -d "$(dirname -- "$1")" ]]
}

# to_abs <path>  -> absolute path (Windows form when cygpath is available)
to_abs() {
    local p
    p="$(realpath -m -- "$1")"
    if [[ "$HAVE_CYGPATH" -eq 1 ]]; then p="$(cygpath -m -- "$p")"; fi
    echo "$p"
}

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

if [[ -n "$RUN_DIR" ]]; then
    [[ "$RUN_DIR" = /* ]] || RUN_DIR="$ROOT/$RUN_DIR"
    cd "$RUN_DIR" || fail "cannot enter RUN_DIR \"$RUN_DIR\""
fi

# exec hands over the process, so the program's exit code is zrun's exit code.
exec "$EXE" ${ARGS[@]+"${ARGS[@]}"}
