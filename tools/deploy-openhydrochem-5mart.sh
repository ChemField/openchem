#!/usr/bin/env bash
# Publish the full OpenHydroChem static site to www.5mart.ml/openhydrochem/.
# Mirrors the same convention as sync-5mart.sh: the SSH target comes ONLY from
# $CHEMFIELD_5MART_SSH (or an ssh config alias) — never hard-coded, never a secret in git.
# Usage: CHEMFIELD_5MART_SSH=user@host [REMOTE_DIR=/openhydrochem] tools/deploy-openhydrochem-5mart.sh [--dry-run]
set -euo pipefail
cd "$(dirname "$0")/.."
: "${CHEMFIELD_5MART_SSH:?set CHEMFIELD_5MART_SSH=user@host (SSH target for 5mart)}"
REMOTE_DIR="${REMOTE_DIR:-/openhydrochem}"
DRY=""; [ "${1:-}" = "--dry-run" ] && DRY="--dry-run"

# The static site = the repo tree minus dev/CI/server-only dirs. Everything the
# browser needs (index.html, the labs + 3D chem-web under molgang/, root games,
# data/) ships; git/tooling/tests/docs and the PHP relay do not.
rsync -avz $DRY --checksum --delete \
  --exclude '.git' --exclude '.github' --exclude 'tools' --exclude 'tests' \
  --exclude 'docs' --exclude '5mart' --exclude '*.md' --exclude '.gitignore' \
  --exclude 'CHANGELOG.md' --exclude 'LICENSE' \
  ./ "$CHEMFIELD_5MART_SSH:$REMOTE_DIR/"

echo "✓ OpenHydroChem → $CHEMFIELD_5MART_SSH:$REMOTE_DIR/  (https://www.5mart.ml/openhydrochem/)"
echo "  Verify: open https://www.5mart.ml/openhydrochem/#knowledge-graph (3D chem-web) and /#play (The Bench)."
