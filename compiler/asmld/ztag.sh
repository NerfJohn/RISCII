#!/usr/bin/env bash
# ===========================================================================
#  ztag.sh - tag a commit with <TAG_PREFIX>vX.Y.Z (same rules as zbuild.sh)
#
#  Usage:
#    ./ztag.sh <version> [options]
#
#  <version>
#    vX.Y.Z               use exactly this version
#    major|minor|patch    bump the highest existing version
#                         (v1.2.3 -> v2.0.0 / v1.3.0 / v1.2.4; v0.0.0 if none)
#
#  Options
#    -c, --commit <ref>   commit to tag (default: HEAD, the latest commit)
#    -m, --message <msg>  tag message (default: "Release <version>")
#    -p, --push           push the new tag to origin
#    -f, --force          allow a version that isn't higher than the highest
#                         existing one
#    -n, --dry-run        show what would happen without creating the tag
#    -h, --help           show this help
#
#  Tags are annotated, so the tag date (used in version.h) is the date the
#  tag was created.
# ===========================================================================
set -euo pipefail
ZSCRIPT=ztag

SELF="$(readlink -f "${BASH_SOURCE[0]}")"
cd "$(dirname "$SELF")" || { echo "cannot enter project root" >&2; exit 1; }
source ./zhead.sh

usage() { sed -n '3,24p' "$SELF" | sed 's/^# \{0,2\}//'; }

VERSION_ARG=""
COMMIT="HEAD"
MESSAGE=""
PUSH=0
FORCE=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        -c|--commit)  [[ $# -ge 2 ]] || fail "$1 needs a value"; COMMIT="$2"; shift 2 ;;
        -m|--message) [[ $# -ge 2 ]] || fail "$1 needs a value"; MESSAGE="$2"; shift 2 ;;
        -p|--push)    PUSH=1; shift ;;
        -f|--force)   FORCE=1; shift ;;
        -n|--dry-run) DRY_RUN=1; shift ;;
        -h|--help)    usage; exit 0 ;;
        -*)           fail "unknown option: $1 (see --help)" ;;
        *)            [[ -z "$VERSION_ARG" ]] || fail "only one version may be given"
                      VERSION_ARG="$1"; shift ;;
    esac
done

in_git_repo || fail "not a git repository"

HIGHEST="$(highest_version || true)"

if [[ -z "$VERSION_ARG" ]]; then
    usage
    echo
    log "Highest existing version: ${HIGHEST:-none}"
    exit 1
fi

# ------------------------------- resolve version ----------------------------
case "$VERSION_ARG" in
    major|minor|patch)
        base="${HIGHEST:-v0.0.0}"
        IFS=. read -r X Y Z <<< "${base#v}"
        X=$((10#$X)); Y=$((10#$Y)); Z=$((10#$Z))
        if [[ -z "$HIGHEST" ]]; then
            NEW="v0.0.0"            # first tag ever
        else
            case "$VERSION_ARG" in
                major) NEW="v$((X + 1)).0.0" ;;
                minor) NEW="v$X.$((Y + 1)).0" ;;
                patch) NEW="v$X.$Y.$((Z + 1))" ;;
            esac
        fi
        ;;
    *)
        is_valid_version "$VERSION_ARG" || fail "\"$VERSION_ARG\" is not of the form vX.X.X (or major/minor/patch)"
        NEW="$VERSION_ARG"
        ;;
esac

TAG="${TAG_PREFIX}${NEW}"

# --------------------------------- checks -----------------------------------
COMMIT_HASH="$(git rev-parse --verify --quiet "${COMMIT}^{commit}")" \
    || fail "\"$COMMIT\" is not a valid commit"

git rev-parse --verify --quiet "refs/tags/$TAG" >/dev/null \
    && fail "tag \"$TAG\" already exists"

if [[ -n "$HIGHEST" && "$FORCE" -eq 0 ]] && ! version_gt "$NEW" "$HIGHEST"; then
    fail "$NEW is not higher than the highest existing version $HIGHEST (use --force to tag anyway)"
fi

# A commit that already has a version tag would make zbuild's choice ambiguous.
EXISTING="$(git tag --points-at "$COMMIT_HASH" --list "${TAG_PREFIX}v*" | tr '\n' ' ')"
[[ -n "$EXISTING" ]] && warn "commit already has tag(s): $EXISTING"

if [[ "$(git rev-parse HEAD)" == "$COMMIT_HASH" ]] && project_dirty; then
    warn "there are uncommitted changes in the project - they are NOT part of this tag"
fi

SHORT="$(git rev-parse --short=7 "$COMMIT_HASH")"
SUBJECT="$(git log -1 --format=%s "$COMMIT_HASH")"
MESSAGE="${MESSAGE:-Release $NEW}"

# --------------------------------- tag --------------------------------------
if [[ "$DRY_RUN" -eq 1 ]]; then
    log "[dry run] would tag $SHORT (\"$SUBJECT\") as $TAG"
    [[ "$PUSH" -eq 1 ]] && log "[dry run] would push $TAG to origin"
    exit 0
fi

git tag -a "$TAG" -m "$MESSAGE" "$COMMIT_HASH"
log "Tagged $SHORT (\"$SUBJECT\") as $TAG"

if [[ "$PUSH" -eq 1 ]]; then
    git push origin "refs/tags/$TAG" || fail "tag created locally, but push failed"
    log "Pushed $TAG to origin"
else
    log "Not pushed. To push:  git push origin $TAG"
fi
