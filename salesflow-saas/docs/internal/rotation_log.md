# Secret Rotation Log

> **Rule**: Every secret found in git history must be rotated and logged here.  
> **Owner**: CTO / Security Lead  
> **Review**: Monthly

---

## Rotation Template

```
| Date       | Secret Type | Location Found | Old ID/Prefix | New Location | Rotated By | Verified |
|------------|------------|----------------|---------------|--------------|-----------|----------|
| YYYY-MM-DD | API Key    | git history    | sk_xxxx...   | AWS SM       | @user     | ✓        |
```

---

## Active Rotations

### 2026-04-17 — Initial full-history scan

**Tool**: gitleaks v8.20.1
**Scope**: 146 commits scanned
**Findings**: 1

| File | Line | Rule | Verdict | Action |
|------|------|------|---------|--------|
| `personal-brand-engine/tests/test_llm_client.py` | 14 | generic-api-key | **FALSE POSITIVE** — model name `llama-3.1-70b-versatile` | Added to `.gitleaksignore` |

### Conclusion
**No real secrets detected in git history.** Repository is clean for extraction to new org.

## Future Rotations

| Date | Secret Type | Location Found | Rotated By | Verified |
|------|-------------|----------------|-----------|----------|
| TBD  | — | — | — | — |

---

## Scan Commands

```bash
# Install tools
pip install gitleaks detect-secrets

# Full history scan
gitleaks detect --source . --log-opts="--all" --report-path /tmp/secret_scan.json

# Current staged files only
gitleaks protect --staged

# Alternative: trufflehog
pipx install trufflehog3
trufflehog3 . --format json --output /tmp/trufflehog_report.json
```

---

## Mandatory Actions After Scan

For every finding:
1. Rotate the credential in the source system (AWS, Stripe, OpenAI, etc.)
2. Update environment variables in production
3. Revoke the leaked credential
4. Add entry to this log
5. Add path/pattern to `.gitleaksignore` ONLY if it's a known false positive

---

## Secrets Management Hierarchy

| Environment | Manager |
|-------------|---------|
| Local dev | `.env` file (gitignored) + Doppler |
| Staging | Doppler or AWS Secrets Manager |
| Production | AWS Secrets Manager (me-south-1) |

## Escape Hatches (forbidden)

- ❌ Secrets in `.env.example`
- ❌ Secrets in docker-compose.yml (use Secrets reference)
- ❌ Secrets in code comments
- ❌ Secrets in test fixtures (use generated values)
- ❌ Secrets in Slack, email, or tickets
