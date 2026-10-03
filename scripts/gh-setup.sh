#!/usr/bin/env bash
# One-shot GitHub setup: create the repo, enable Pages (GitHub Actions source), set About + topics, push.
# Needs the GitHub CLI: https://cli.github.com   (run `gh auth login` once)
# Usage: ./scripts/gh-setup.sh [repo-name]      Free plans need a PUBLIC repo for Pages.
set -euo pipefail

REPO="${1:-portfolio}"
DESC="${DESC:-Senior Software Engineer: full-stack, backend-first. Distributed payment systems, FinTech and AI. Interactive single-file portfolio, no framework.}"
TOPICS="portfolio,portfolio-website,github-pages,personal-website,vanilla-js,canvas-animation,no-framework"

command -v gh >/dev/null || { echo "Install the GitHub CLI first: https://cli.github.com"; exit 1; }
gh auth status >/dev/null 2>&1 || gh auth login

python3 scripts/privacy_check.py || true
read -r -p "Phone numbers (if any, above) will be public. Continue? [y/N] " ok
[[ "${ok:-n}" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 1; }

if [ ! -d .git ]; then git init -b main; fi
git add -A
git diff --cached --quiet || git commit -m "Initial commit: portfolio"

# 1. create the repo (no push yet), so Pages can be switched on before the first workflow run
gh repo create "$REPO" --public --source=. --remote=origin --description "$DESC"
OWNER="$(gh repo view --json owner -q .owner.login)"
URL="https://${OWNER}.github.io/${REPO}/"

# 2. About panel + topics
gh repo edit "$OWNER/$REPO" --homepage "$URL" --add-topic "$TOPICS"

# 3. Pages source = GitHub Actions
gh api -X POST "repos/${OWNER}/${REPO}/pages" -f build_type=workflow >/dev/null 2>&1 \
  || echo "Could not enable Pages automatically. Do it once: Settings > Pages > Source: GitHub Actions."

# 4. push -> the workflow builds and deploys
git push -u origin main

cat <<MSG

Done. First deploy takes about a minute: https://github.com/${OWNER}/${REPO}/actions
Site:  ${URL}
Last manual step (GitHub has no API for it): upload docs/img/social-preview.png at
  https://github.com/${OWNER}/${REPO}/settings  ->  Social preview
MSG
