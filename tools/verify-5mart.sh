#!/usr/bin/env bash
# Verify the live 5mart deployment against the repo. No credentials needed —
# public HTTPS + local sha256.
#   static files        -> byte-identity (sha256 repo vs live)
#   server-executed php  -> route-liveness (HTTP 200); marked optional because
#                           the gateway proxies to the laptop bridge over an SSH
#                           tunnel, so a 5xx means "tunnel down", not "out of sync".
# Exit 1 on drift of a required file; optional route failures only warn.
set -euo pipefail
cd "$(dirname "$0")/.."
MAN=tools/deploy-manifest.json
BASE=$(python3 -c "import json;print(json.load(open('$MAN'))['publicBase'])")
fail=0; warn=0; n=0
while IFS=$'\t' read -r repo remote mode route optional; do
  n=$((n+1))
  if [ "$mode" = "route" ]; then
    code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/$route") || code=000
    if [ "$code" = 200 ]; then echo "ok    $remote (route -> 200)"
    elif [ "$optional" = "1" ]; then echo "warn  $remote (route -> $code; tunnel down, deploy unaffected)"; warn=$((warn+1))
    else echo "FAIL  $remote (route -> $code)"; fail=1; fi
  else
    want=$(shasum -a256 "$repo" | cut -d' ' -f1)
    got=$(curl -fsS "$BASE/$remote" | shasum -a256 | cut -d' ' -f1) || { echo "MISSING live: $remote"; fail=1; continue; }
    if [ "$want" = "$got" ]; then echo "ok    $remote"; else echo "DRIFT $remote  repo=$want live=$got"; fail=1; fi
  fi
done < <(python3 -c "import json
for f in json.load(open('$MAN'))['files']:
    print('\t'.join([f['repo'],f['remote'],f.get('verify','hash'),f.get('route',''),'1' if f.get('optional') else '0']))")
echo "---"
if [ "$fail" = 0 ]; then echo "verify-5mart: OK ($n entries; $warn optional warning(s))"; else echo "verify-5mart: DRIFT DETECTED"; fi
exit $fail
