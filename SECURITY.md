# Security policy

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security reports.

1. Open a **private security advisory** for this repository (GitHub → **Security** → **Advisories** → **Report a vulnerability**), or  
2. Contact the repository maintainers through a private channel you already use for this project.

Include:

- A short description of the issue and affected components (paths or features).
- Steps to reproduce (proof-of-concept) if safe to share.
- Whether you believe the issue is actively exploitable in production.

We will aim to acknowledge receipt within a reasonable timeframe and coordinate remediation and disclosure.

## Secrets

Never commit real API keys, tokens, `DATABASE_URL`, or Moyasar keys. Use Railway variables and GitHub Actions secrets. See `dealix/docs/SECURITY_SECRET_ROTATION_CHECKLIST.md` if a secret may have been exposed.
