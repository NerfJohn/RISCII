# shellcheck shell=bash
# ===========================================================================
#  zhead.sh - shared settings and helpers for zbuild/zclean/zrun/ztag.
#  This file is sourced by the other scripts; don't run it directly.
#
#  Every setting can be overridden from the environment for a single run,
#  e.g.  EXEC_NAME=foo ./zbuild.sh
# ===========================================================================

# ------------------------------ configuration ------------------------------
# Name of the executable (without .exe). Passed to CMake as -DEXEC_NAME=...
EXEC_NAME="asmld"

# Prefix in front of the version in your git tags. May be empty.
# Tags look like  <TAG_PREFIX>vX.Y.Z   e.g.  myapp-v1.2.3
TAG_PREFIX="asmld/"

# Build settings
CMAKE_GENERATOR="MSYS Makefiles"
BUILD_DIR="build"
OUTPUT_DIR="artifact"
VERSION_HEADER="inc/version.h"
# ---------------------------------------------------------------------------

log()  { echo "[${ZSCRIPT:-z}] $*"; }
warn() { echo "[${ZSCRIPT:-z}] WARNING: $*" >&2; }
fail() { echo "[${ZSCRIPT:-z}] ERROR: $*" >&2; exit 1; }

# is_valid_version <string>  -> true if string is vX.X.X (unsigned integers)
is_valid_version() { [[ "$1" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; }

# version_gt <vA> <vB>  -> true if A > B  (both must be valid)
version_gt() {
    local IFS=. a b i
    read -r -a a <<< "${1#v}"
    read -r -a b <<< "${2#v}"
    for i in 0 1 2; do
        (( 10#${a[i]} > 10#${b[i]} )) && return 0
        (( 10#${a[i]} < 10#${b[i]} )) && return 1
    done
    return 1
}

# in_git_repo  -> true if the current directory is inside a git work tree
in_git_repo() { git rev-parse --is-inside-work-tree >/dev/null 2>&1; }

# latest_reachable_tag [commit]
#   Prints the newest (by tag date; ties -> higher version) valid <prefix>vX.Y.Z tag reachable from
#   the commit (default HEAD). Returns 1 if there is none.
latest_reachable_tag() {
    local tag
    while IFS= read -r tag; do
        if is_valid_version "${tag#"$TAG_PREFIX"}"; then
            echo "$tag"; return 0
        fi
    done < <(git tag --merged "${1:-HEAD}" --list "${TAG_PREFIX}v*" --sort=-v:refname --sort=-creatordate 2>/dev/null || true)
    return 1
}

# highest_version
#   Prints the highest vX.Y.Z among ALL valid <prefix> tags (any branch),
#   without the prefix. Returns 1 if there is none.
highest_version() {
    local tag ver best=""
    while IFS= read -r tag; do
        ver="${tag#"$TAG_PREFIX"}"
        is_valid_version "$ver" || continue
        if [[ -z "$best" ]] || version_gt "$ver" "$best"; then best="$ver"; fi
    done < <(git tag --list "${TAG_PREFIX}v*" 2>/dev/null || true)
    [[ -n "$best" ]] && echo "$best"
}

# project_dirty  -> true if there are uncommitted/untracked changes inside the
#   current directory (the project root). Generated paths are ignored.
project_dirty() {
    [[ -n "$(git status --porcelain -- . \
                ":(exclude)$BUILD_DIR" \
                ":(exclude)$OUTPUT_DIR" \
                ":(exclude)$VERSION_HEADER")" ]]
}

# exe_path <dir>  -> prints <dir>/<EXEC_NAME>.exe, or <dir>/<EXEC_NAME>
#   (non-Windows) if that's what exists. Returns 1 if neither exists.
exe_path() {
    local f
    for f in "$1/$EXEC_NAME.exe" "$1/$EXEC_NAME"; do
        [[ -f "$f" ]] && { echo "$f"; return 0; }
    done
    return 1
}
