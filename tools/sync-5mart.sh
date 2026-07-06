#!/usr/bin/env bash
# Push the canonical file set to 5mart /Slag/ reproducibly.
# SSH target comes from $CHEMFIELD_5MART_SSH (e.g. "5martml@5martm.ssh.transip.me")
# or an ssh config alias — never hard-coded, never a secret in git.
# Usage: CHEMFIELD_5MART_SSH=user@host [REMOTE_DIR=/path] tools/sync-5mart.sh [--dry-run]
set -euo pipefail
cd "$(dirname "$0")/.."
MAN=tools/deploy-manifest.json
: "${CHEMFIELD_5MART_SSH:?set CHEMFIELD_5MART_SSH=user@host (SSH target for 5mart)}"
REMOTE_DIR="${REMOTE_DIR:-$(python3 -c "import json;print(json.load(open('$MAN'))['remoteBase'])")}"
DRY=""; [ "${1:-}" = "--dry-run" ] && DRY="--dry-run"
# stage into a temp tree mirroring the remote layout, then one rsync
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
while IFS=$'\t' read -r repo remote; do install -D "$repo" "$STAGE/$remote"; done \
  < <(python3 -c "import json;[print(f['repo']+chr(9)+f['remote']) for f in json.load(open('$MAN'))['files']]")
echo "Syncing $(ls "$STAGE" | wc -l | tr -d ' ') files -> $CHEMFIELD_5MART_SSH:$REMOTE_DIR/  $DRY"
rsync -avz $DRY --checksum "$STAGE/" "$CHEMFIELD_5MART_SSH:$REMOTE_DIR/"
echo "Now run: tools/verify-5mart.sh"
