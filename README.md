# GHASTest — GitHub Advanced Security demo

A self-contained demo repository for showing **GHAS code scanning (CodeQL)** and
**secret scanning with push protection**.

> ⚠️ **The code in [`app/`](./app) is intentionally vulnerable.** It exists only to
> generate security alerts. Never deploy it, and never copy from it.

## What is enabled on this repository

| Feature | Status |
| --- | --- |
| GitHub Advanced Security | Enabled |
| Code scanning (CodeQL, advanced setup) | [`.github/workflows/codeql.yml`](./.github/workflows/codeql.yml) |
| Secret scanning | Enabled |
| Secret scanning push protection | Enabled |
| Dependabot alerts | Driven by the outdated pins in [`requirements.txt`](./requirements.txt) |

## Repository layout

```
app/
  vulnerable_app.py     Flask routes with SQLi, command injection, XSS, SSRF, eval, pickle
  insecure_helpers.py   Weak crypto, disabled TLS verification, insecure randomness
  secure_app.py         The remediated version of every flaw above — the "after" slide
.github/
  workflows/codeql.yml  CodeQL analysis on push, PR, and a weekly schedule
  dependabot.yml        Weekly pip and github-actions update checks
docs/
  CODE-SCANNING-DEMO.md     Step-by-step CodeQL walkthrough
  SECRET-SCANNING-DEMO.md   Step-by-step push protection walkthrough
scripts/
  Start-PushProtectionDemo.ps1  Drives the live push-protection block
```

## Running the demo

Two independent tracks — run either or both:

1. **[Code scanning walkthrough](./docs/CODE-SCANNING-DEMO.md)** — roughly 10 minutes.
   Show the alert list, drill into a data-flow path, then fix a vulnerability in a PR
   and watch the check turn green.

2. **[Secret scanning walkthrough](./docs/SECRET-SCANNING-DEMO.md)** — roughly 5 minutes.
   Attempt to push a credential and watch GitHub reject it before it ever reaches
   the remote.

### Suggested 15-minute running order

| Time | Segment |
| --- | --- |
| 0:00 | Show the **Security** tab: alerts already waiting from the initial push |
| 0:02 | Open a SQL injection alert, walk the source → sink data-flow path |
| 0:06 | Open a PR that applies the fix; CodeQL re-runs and the alert closes |
| 0:09 | Switch to secret scanning — attempt the blocked push live |
| 0:13 | Show the bypass dialog and the audit trail it creates |

## Security note about this repo

No real credential is stored anywhere in this repository, by design. The push
protection demo asks you to supply a throwaway test token **at demo time**; it is
written to a git-ignored scratch path and deleted afterwards. The only
credential-shaped strings committed here are the obvious placeholders in
[`insecure_helpers.py`](./app/insecure_helpers.py), which exist so CodeQL's
`py/hardcoded-credentials` query has something to flag.
