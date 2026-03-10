#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="${1:-}"
OWNER="${2:-}"         # optional: org or user; if empty, create under authenticated user
PRIVATE="${3:-false}"  # true|false

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "GITHUB_TOKEN is not set" >&2
  exit 1
fi

if [[ -z "$REPO_NAME" ]]; then
  echo "Usage: $0 <repo-name> [owner] [private:true|false]" >&2
  exit 1
fi

AUTH_HEADER="Authorization: token $GITHUB_TOKEN"
ACCEPT_HEADER="Accept: application/vnd.github+json"
API="https://api.github.com"

BOOL=$( [[ "$PRIVATE" == "true" ]] && echo true || echo false )
DATA=$(printf '{"name":"%s","private":%s}' "$REPO_NAME" "$BOOL")
if [[ -n "$OWNER" ]]; then
  curl -sS -X POST -H "$AUTH_HEADER" -H "$ACCEPT_HEADER" "$API/orgs/$OWNER/repos" -d "$DATA" >/dev/null
  REMOTE_URL="https://github.com/$OWNER/$REPO_NAME.git"
else
  USER_LOGIN=$(curl -sS -H "$AUTH_HEADER" -H "$ACCEPT_HEADER" "$API/user" | python -c "import sys,json;print(json.load(sys.stdin)['login'])")
  curl -sS -X POST -H "$AUTH_HEADER" -H "$ACCEPT_HEADER" "$API/user/repos" -d "$DATA" >/dev/null
  REMOTE_URL="https://github.com/$USER_LOGIN/$REPO_NAME.git"
fi

if [[ ! -d ".git" ]]; then
  git init
fi

git add .
git commit -m "Initial commit"
git branch -M main || true

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE_URL"
else
  git remote add origin "$REMOTE_URL"
fi

git push -u origin main
