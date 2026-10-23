#!/usr/bin/env bash
# Read-only worktree cleanup audit. Classifies every git worktree by size, age,
# merge state, uncommitted work, remote state and PR state, and suggests a
# bucket. Never deletes anything; deletion stays a gated step in the worktree
# skill.
#
# Usage: worktree-audit.sh [-b|--base <ref>] [repo-path]
#   repo-path defaults to the current repo.
#   -b sets the ref the MERGED column checks against (e.g. origin/integration).
#   Without it the base is <remote>/HEAD, then <remote>/main, then
#   <remote>/master. <remote> defaults to origin; set GIT_REMOTE for another.
#   <remote>/HEAD is the remote's default branch, not necessarily the branch PRs
#   merge into; pass -b when they differ.
#
# Buckets: safe (merged, clean) | hold-open-pr | hold-wip | review (unmerged and
# no merged PR: a question, not a chore).
set -u

base=""
while [ $# -gt 0 ]; do
	case "$1" in
	-b|--base) [ $# -ge 2 ] || { echo "error: $1 needs a ref" >&2; exit 2; }; base="$2"; shift 2 ;;
	-h|--help) sed -n '2,/^set -u/p' "$0" | sed '$d; s/^# \{0,1\}//'; exit 0 ;;
	-*) echo "error: unknown option: $1" >&2; exit 2 ;;
	*) break ;;
	esac
done

repo="${1:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -z "$repo" ] && { echo "not in a git repo; pass a repo path" >&2; exit 1; }
cd "$repo" || exit 1
git rev-parse --git-dir >/dev/null 2>&1 || { echo "error: not a git repo: $repo" >&2; exit 1; }

remote="${GIT_REMOTE:-origin}"

# Main worktree is the first entry; everything else is a candidate.
main_wt=$(git worktree list --porcelain | awk '/^worktree /{print $2; exit}')

if [ -z "$base" ]; then
	for cand in "$(git symbolic-ref --short "refs/remotes/$remote/HEAD" 2>/dev/null)" "$remote/main" "$remote/master"; do
		[ -n "$cand" ] && git rev-parse --verify --quiet "$cand^{commit}" >/dev/null && { base="$cand"; break; }
	done
	[ -z "$base" ] && { echo "error: no base ref ($remote/HEAD, $remote/main, $remote/master all missing); pass -b <ref>" >&2; exit 1; }
	echo "warn: no -b given; MERGED checks against $base" >&2
fi

# The base drives the merge check. The fetch is best-effort (stale is fine for
# a first pass) and runs before the check, since -b may name a branch not
# fetched yet. The explicit refspec creates it even in a single-branch clone.
case "$base" in
"$remote"/*) git fetch "$remote" "+refs/heads/${base#"$remote"/}:refs/remotes/$base" --quiet 2>/dev/null \
	|| echo "warn: could not fetch $base; merged column may be stale" >&2 ;;
esac
git rev-parse --verify --quiet "$base^{commit}" >/dev/null 2>&1 || { echo "error: base ref not found: $base" >&2; exit 1; }

# PR state by branch, fetched once as [{number, state, head}] with a lowercase
# state. Empty when gh cannot read this repo's PRs.
prs=$(mktemp)
if command -v gh >/dev/null 2>&1 \
	&& raw=$(gh pr list --author "@me" --state all --limit 1000 \
		--json number,state,headRefName 2>/dev/null); then
	printf '%s' "$raw" | jq '[.[] | {number, state: (.state | ascii_downcase), head: .headRefName}]' > "$prs" 2>/dev/null
fi
[ -s "$prs" ] || echo "[]" > "$prs"

echo "# base: $base"
printf "SIZE\tAGE\tMERGED\tDIRTY\tREMOTE\tPR\tBUCKET\tWORKTREE\n"

git worktree list --porcelain | awk '/^worktree /{print $2}' | while read -r wt; do
	[ "$wt" = "$main_wt" ] && continue

	size=$(du -sh "$wt" 2>/dev/null | awk '{print $1}')
	head=$(git -C "$wt" rev-parse HEAD 2>/dev/null)
	head_ts=$(git -C "$wt" log -1 --format='%ct' HEAD 2>/dev/null || echo 0)
	age=$([ "$head_ts" -gt 0 ] 2>/dev/null && echo "$(( ($(date +%s) - head_ts) / 86400 ))d" || echo "?")

	# Squash-merged branches are not ancestors of the base, so PR state is the
	# real signal; merge-base only catches fast-forward/rebase merges.
	git merge-base --is-ancestor "$head" "$base" 2>/dev/null && merged=YES || merged=no

	# Distinguish real WIP (tracked edits) from disposable untracked scratch.
	porcelain=$(git -C "$wt" status --porcelain 2>/dev/null)
	if [ -z "$porcelain" ]; then dirty=clean
	elif printf '%s\n' "$porcelain" | grep -qv '^??'; then
		dirty="wip:$(printf '%s\n' "$porcelain" | grep -cv '^??')"
	else dirty="scratch:$(printf '%s\n' "$porcelain" | grep -c '^??')"; fi

	branch=$(git -C "$wt" symbolic-ref --quiet --short HEAD 2>/dev/null || echo "")
	if [ -z "$branch" ]; then remote_state=detached
	elif git -C "$wt" show-ref --verify --quiet "refs/remotes/$remote/$branch"; then
		[ "$(git -C "$wt" rev-parse "$remote/$branch" 2>/dev/null)" = "$head" ] \
			&& remote_state=pushed \
			|| remote_state="ahead$(git -C "$wt" rev-list --count "$remote/$branch..HEAD" 2>/dev/null)"
	else remote_state=no-remote; fi

	pr=$([ -n "$branch" ] && jq -r --arg b "$branch" \
		'.[] | select(.head==$b) | "#\(.number)/\(.state)"' "$prs" 2>/dev/null | head -1)
	[ -z "$pr" ] && pr="-"

	case "$dirty" in
		wip:*) bucket=hold-wip ;;
		*)
			case "$pr" in
				*/open|*/draft) bucket=hold-open-pr ;;
				*/merged) bucket=safe ;;
				*) if [ "$merged" = YES ]; then bucket=safe; else bucket=review; fi ;;
			esac ;;
	esac

	printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
		"$size" "$age" "$merged" "$dirty" "$remote_state" "$pr" "$bucket" "$wt"
done | sort -t$'\t' -k1,1 -rh

rm -f "$prs"
