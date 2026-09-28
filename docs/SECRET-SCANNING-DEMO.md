# Demo 2 — Secret scanning and push protection

**Duration:** ~5 minutes
**Goal:** show GitHub rejecting a credential **at `git push` time**, before it
ever reaches the remote — and then show the detection path for secrets that
predate the control.

---

## Why no secret is committed in this repository

This repo deliberately contains **no real credential**. Committing one — even a
"demo" one — puts a live secret into git history, where it survives force-pushes,
forks, clones, and cached views.

The live block is also a better demo than a committed secret: the audience sees
the control working in real time rather than reading an alert after the fact.

So you supply a **throwaway token at demo time**. The helper script writes it to
a working-tree file, lets push protection reject it, and then cleans up.

---

## Preparing a safe test token (do this once, before the demo)

Pick one of these:

### Option A — a zero-scope GitHub PAT (most reliable)

1. <https://github.com/settings/personal-access-tokens> → **Generate new token**
   → *fine-grained*.
2. Resource owner: your own account. Repository access: **Public repositories
   (read-only)**. Permissions: **none**.
3. Expiration: 7 days.
4. Copy the token.

A token with no permissions grants no access, but it still matches GitHub's
`github_pat_` provider pattern, so push protection reliably blocks it. **Revoke
it after the demo.**

### Option B — a documented example key (no token creation needed)

AWS's own documentation example key:

```
AKIAIOSFODNN7EXAMPLE
```

This matches the *Amazon AWS Access Key ID* pattern. It is not a real key, so
there is nothing to revoke — but because it is a well-known example string,
detection is slightly less certain than Option A.

> **Never use a token that has real access, even briefly.** If push protection
> is bypassed or disabled, the secret lands in history.

---

## Step 1 — Establish the problem (1 min)

Before running anything, frame it:

> *"The average secret leak isn't malicious. Someone hardcodes a key to get
> unblocked at 6pm, pushes, and forgets. By the time anyone notices, it's in the
> history of forty clones. Secret scanning solves this in two places: detection
> for what's already there, and prevention at the moment of push."*

Show `get_api_key()` in [`app/secure_app.py`](../app/secure_app.py) as the
pattern you actually want — read the value from the environment.

---

## Step 2 — Attempt the blocked push (2 min)

```powershell
cd c:\Projects\GHASTest
.\scripts\Start-PushProtectionDemo.ps1
```

The script creates a branch, asks you to paste the test token, writes it into a
config file, commits, and pushes. The push **fails**:

```
remote: error: GH013: Repository rule violations found for refs/heads/secret-scanning-demo.
remote:
remote: - GITHUB PUSH PROTECTION
remote:   —————————————————————————————————————————
remote:     Resolve the following violations before pushing again
remote:
remote:     - Push cannot contain secrets
remote:
remote:      —— GitHub Personal Access Token ——————————————————————
remote:       locations:
remote:         - commit: <sha>
remote:           path: app/config_demo.py:12
```

Points to make while the message is on screen:

- **Nothing reached the remote.** The commit is rejected; the secret never
  enters server-side history.
- GitHub names the **provider**, the **commit**, and the **file and line**.
- This runs on GitHub's side, so it cannot be skipped by a developer who
  forgot to install a pre-commit hook or who uses `--no-verify`.

---

## Step 3 — The bypass path and its audit trail (1 min)

Open the `unblock-secret` URL from the push output. Show the dialog:

- *It's used in tests*
- *It's a false positive*
- *I'll fix it later*

Talking points:

- Bypass is **deliberate, logged, and attributable** — an organisation can
  restrict who is allowed to do it, and security teams are alerted when it
  happens.
- Choosing "I'll fix it later" allows the push **and** immediately opens a
  secret scanning alert, so nothing silently disappears.

**For the demo, do not bypass.** Remediate instead — it models the right
behaviour:

```powershell
.\scripts\Start-PushProtectionDemo.ps1 -Remediate
```

This removes the secret, rewrites the offending commit so the value is absent
from history, and pushes successfully. Show the green push as the payoff.

---

## Step 4 — Detection for secrets already in history (1 min)

Push protection stops new leaks. Secret scanning finds the old ones.

Show **Security → Secret scanning** and cover:

- Scans the **entire git history**, all branches, on every push — plus issues,
  PR bodies, and comments.
- **Partner patterns**: 200+ providers. On detection GitHub notifies the
  *provider* (AWS, Stripe, Slack…), who can revoke the key automatically —
  often within seconds, before the attacker uses it.
- **Validity checks** (currently disabled on this repo): GitHub asks the
  provider whether the leaked credential is still live, so you can triage
  "active" ahead of "already rotated".
- **Push protection** and **AI detection** for generic, unstructured secrets
  that do not match a known provider format.

### Optional: turn on the extra detectors live

```powershell
gh api -X PATCH repos/skomma_microsoft/GHASTest `
  -f 'security_and_analysis[secret_scanning_validity_checks][status]=enabled' `
  -f 'security_and_analysis[secret_scanning_non_provider_patterns][status]=enabled'
```

Non-provider patterns catch generic things like connection strings and private
keys. Enabling it live is a good way to show the toggle-level control.

---

## Step 5 — The lesson that matters most (30 sec)

> *"A blocked push costs a developer thirty seconds. A leaked key costs an
> incident response. And note what remediation required: rewriting history.
> That is exactly why prevention at push time beats detection after the fact —
> once a secret is pushed, you must assume it is compromised and rotate it,
> no matter how fast you delete the commit."*

---

## Cleanup (always run this)

```powershell
.\scripts\Start-PushProtectionDemo.ps1 -Cleanup
```

Then **revoke the test token** at
<https://github.com/settings/personal-access-tokens> if you used Option A.
