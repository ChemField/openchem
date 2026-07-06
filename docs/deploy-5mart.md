# Reproducible 5mart sync

The canonical files live in this repo; `www.5mart.ml/Slag/` is a deploy target.
Two commands replace ad-hoc copy steps — no manual drift.

## Canonical set
`tools/deploy-manifest.json` is the single source of truth: repo path → public
path on `/Slag/`. Add a file there to include it in both sync and verify.

## Deploy
```bash
export CHEMFIELD_5MART_SSH="user@5martm.ssh.transip.me"   # never committed
tools/sync-5mart.sh --dry-run   # preview
tools/sync-5mart.sh             # rsync --checksum to /Slag/
```
SSH target comes only from `$CHEMFIELD_5MART_SSH` (or an ssh config alias);
no host or secret is stored in git.

## Verify (no credentials)
```bash
tools/verify-5mart.sh
```
- **Static files** (dataset + alias pointers + node manifest): sha256 of the repo
  copy must equal the live copy, byte-for-byte. Any mismatch → exit 1.
- **`origintrail-gateway.php`**: verified by route liveness
  (`?route=status` → 200), and marked *optional*: the gateway proxies to the
  laptop OriginTrail bridge over an SSH tunnel, so a 5xx means the tunnel is
  down, not that the deploy drifted.

Run `verify-5mart.sh` after every `sync-5mart.sh`, and any time you want to
confirm the public site still matches the repo. Pairs with `tools/validate.py`
(dataset integrity) — validate before you sync, verify after.
