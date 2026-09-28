# Demo 1 — Code scanning with CodeQL

**Duration:** ~10 minutes
**Goal:** show that GHAS finds real, exploitable flaws with data-flow analysis, not
just pattern matching — and that a fix closes the alert automatically.

---

## Before you present

1. Confirm the **CodeQL Code Scanning** workflow has completed at least once:
   `Actions` → `CodeQL Code Scanning`. The first run takes 3–5 minutes.
2. Open `Security` → `Code scanning` and confirm alerts are listed.
3. Have [`app/vulnerable_app.py`](../app/vulnerable_app.py) and
   [`app/secure_app.py`](../app/secure_app.py) open in adjacent editor tabs.

```powershell
# Trigger a scan manually if you need a fresh run
gh workflow run codeql.yml
gh run watch
```

---

## Step 1 — The alert inventory (2 min)

Go to **Security → Code scanning**.

Talking points:

- Alerts are grouped by **rule**, tagged with **severity** and **security
  severity** (CVSS-like), and mapped to **CWE** identifiers.
- Filter by `severity:critical` to show triage by risk rather than by volume.
- Every alert names the exact file, line, and introducing commit.

Expected findings from this repository:

| Rule | CWE | Where |
| --- | --- | --- |
| `py/sql-injection` | CWE-89 | `lookup_user` |
| `py/command-line-injection` | CWE-78 | `ping_host`, `run_backup` |
| `py/code-injection` | CWE-94 | `calculate` |
| `py/unsafe-deserialization` | CWE-502 | `restore_session`, `load_config` |
| `py/reflective-xss` | CWE-79 | `greet` |
| `py/path-injection` | CWE-22 | `download_file` |
| `py/full-ssrf` | CWE-918 | `fetch_url` |
| `py/url-redirection` | CWE-601 | `unsafe_redirect` |
| `py/weak-sensitive-data-hashing` | CWE-327 | `register`, `hash_password` |
| `py/clear-text-logging-sensitive-data` | CWE-312 | `register` |
| `py/hardcoded-credentials` | CWE-798 | `insecure_helpers.py` |
| `py/insecure-randomness` | CWE-338 | `generate_reset_token` |
| `py/request-without-cert-validation` | CWE-295 | `call_partner_api` |

> Exact rule set varies slightly with the CodeQL version. Treat the table as a
> guide, not a guarantee.

---

## Step 2 — Data flow is the differentiator (3 min)

Open the **`py/sql-injection`** alert and click **Show paths**.

This is the moment that separates CodeQL from a linter or a regex scanner. Walk
the path out loud:

1. **Source** — `request.args.get("username")` is attacker-controlled input.
2. **Propagation** — the value flows into the local `query` string via `+`.
3. **Sink** — `cursor.execute(query)` interprets that string as SQL.

Say the key line: *"CodeQL proved there is an unbroken path from an untrusted
source to a dangerous sink. That is why this is a finding and not a guess — and
it is also why CodeQL does not flood you with false positives on safe code."*

Contrast it immediately with `lookup_user` in
[`app/secure_app.py`](../app/secure_app.py): the value is passed as a bound
parameter, the path is broken, and no alert is raised on that function.

---

## Step 3 — Fix it in a pull request (4 min)

This is the part that lands with engineers: the alert appears **in the PR**,
before the code merges.

```powershell
cd c:\Projects\GHASTest
git switch -c fix/sql-injection

# Apply the parameterised query from secure_app.py to vulnerable_app.py
# (edit lookup_user by hand on screen — the audience should see the change)

git add app/vulnerable_app.py
git commit -m "Fix SQL injection in user lookup"
git push -u origin fix/sql-injection
gh pr create --fill
```

Then show:

- The **CodeQL** check running on the PR.
- The **"Code scanning results"** section: the fixed alert is gone; any alert you
  did *not* fix is still listed as pre-existing.
- On merge, the alert transitions to **Closed** in the Security tab automatically.

To demonstrate the opposite direction, add a new vulnerable line in the PR and
show CodeQL annotating it inline as a review comment.

---

## Step 4 — Governance talking points (1 min)

Cover these quickly to close the segment:

- **Branch protection**: require the CodeQL check to pass before merge, so a
  critical finding blocks the merge outright.
- **Dismissing alerts**: dismissal requires a reason (false positive / used in
  tests / won't fix) and is recorded in the audit log.
- **Default vs advanced setup**: this repo uses advanced setup (a committed
  workflow file) because it allows the `security-extended` query suite,
  custom query packs, and matrix builds. Default setup is one click and no YAML.
- **`security-extended`** is set in
  [`codeql.yml`](../.github/workflows/codeql.yml); the default suite is quieter
  and tuned for precision.

---

## Reset between demos

```powershell
cd c:\Projects\GHASTest
git switch main
git branch -D fix/sql-injection
git push origin --delete fix/sql-injection
```

Re-open a dismissed alert from the Security tab if you dismissed one while
presenting.
