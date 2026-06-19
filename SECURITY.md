# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in EleitorAI, please report it
privately to the maintainer. Do **not** open a public GitHub issue.

**Contact:** open a GitHub Security Advisory at
<https://github.com/simoesleandro/eleitorai/security/advisories/new>

Include:
- Description of the vulnerability
- Reproduction steps
- Impact assessment
- Suggested fix (if any)

We aim to acknowledge reports within 72 hours and provide a fix timeline
within 7 days for critical issues.

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| main    | ✅ Active          |
| < 1.0   | ❌ Not maintained  |

Only the `main` branch receives security updates. Pin your deployment to
a specific commit SHA for reproducibility.

## Secrets Management

EleitorAI requires several third-party credentials to function. This section
defines how they should be handled.

### Required secrets

| Secret | Rotation | Owner | Compromise response |
|--------|----------|-------|---------------------|
| `GEMINI_API_KEY` | 90 days | AI lead | Revoke + regenerate at aistudio.google.com |
| `TELEGRAM_BOT_TOKEN` | 180 days | Ops | `/revoke` via @BotFather |
| `TELEGRAM_API_ID` / `TELEGRAM_API_HASH` | 365 days | Ops | "Delete app" at my.telegram.org |
| `ADMIN_PASS` | 90 days | Ops | Update `usuarios.password_hash` in DB |
| `SECRET_KEY` | 90 days | Ops | Rotate + invalidate all Flask sessions |
| `LANGFUSE_*` | 180 days | AI lead | Rotate at cloud.langfuse.com |

### Storage rules

- ✅ Store secrets in `.env` (local dev) or platform secret manager (prod)
- ✅ Use `.env.ci` only for fake CI values (this file is tracked)
- ✅ Use `.env.example` as a template with empty values (tracked)
- ❌ Never commit real `.env` to git (blocked by `scripts/check_no_env.py`)
- ❌ Never paste secrets in GitHub issues, PRs, or chat (use the redaction
  patterns in `core/logging_redactor.py` if you must)
- ❌ Never log full request/response bodies from LLM providers

### Incident: what to do if a secret leaks

1. **Revoke** the secret at the provider (see table above)
2. **Rotate** to a new secret
3. **Audit** git history: `git log -p --all -S "<secret-substring>"`
4. **Force-push** rewritten history if the secret was in commits (only if
   repo is private; for public repos, accept the leak and rely on rotation)
5. **Notify** the team via private channel
6. **Document** in this repo's incident log (or offline equivalent)

## Built-in Protections

EleitorAI ships with several layers of defense:

| Layer | Where | What it does |
|-------|-------|-------------|
| Log redaction | `core/logging_redactor.py` | Scrubs secrets from all log output via `setLogRecordFactory` |
| Pre-commit hook | `scripts/check_no_env.py` | Blocks `.env` files from being committed |
| Secret scanning | `.gitleaks.toml` | Detects known-secret patterns in git diffs |
| Dependabot | `.github/dependabot.yml` | Auto-PRs for security patches in dependencies |
| Meta-test | `tests/core/test_no_log_leaks.py` | Fails CI if any test logs secret values |
| Gitignore | `.gitignore` (line 4) | Excludes `.env` from version control |

## Dependency Security

- All runtime deps pinned in `requirements.txt`
- Dependabot opens weekly PRs for outdated/vulnerable packages
- CI runs `pip-audit` (planned) on every push
- Lock file: not currently used (consider `pip-tools` or `uv` for production)

## Deployment Hardening (Fly.io)

When deploying to Fly.io:
- Use `fly secrets set` to inject credentials (never bake into image)
- Enable `internal_port` only via `fly.toml`
- Set `min_machines_running = 0` for cost, but expect cold starts
- Restrict region to GRU (Brazil) for LGPD compliance
- Enable HTTPS only; Fly provides this automatically

## Data Protection (LGPD)

EleitorAI processes publicly available content from Telegram, YouTube, and
Instagram. No personal data beyond what is publicly posted is collected.

- Collected data: post text, timestamp, author handle, source URL
- Retention: indefinite in SQLite (configurable via cron job — not yet implemented)
- Right to deletion: not implemented (no individual profile tracking)
- DPIA: TODO before production deployment in Brazil

## Audit Log

| Date | Action | By |
|------|--------|-----|
| 2026-06-19 | Initial policy drafted | maintainer |
| 2026-06-19 | Log redaction added (`core/logging_redactor.py`) | maintainer |
| 2026-06-19 | Pre-commit hook added (`scripts/check_no_env.py`) | maintainer |
| 2026-06-19 | gitleaks config added (`.gitleaks.toml`) | maintainer |
| 2026-06-19 | Dependabot enabled (`.github/dependabot.yml`) | maintainer |
