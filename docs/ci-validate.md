# Enabling dataset validation in CI

The validator (`tools/validate.py`) runs locally today:

```bash
python3 tools/validate.py   # exit 0 = pass, 1 = drift
```

To gate every PR on it, add `.github/workflows/validate.yml` (requires a token
with `workflow` scope — an owner step, the agent token cannot push workflows):

```yaml
name: validate-dataset
on: [pull_request, push]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: python3 tools/validate.py
```

Then set branch protection on `main` to require the `validate` check.
