# Supply Chain Integrity

## Dependency Management

### Python (Backend)
- `requirements.txt` with pinned versions (==)
- Regular updates via `pip-audit` + manual review
- No wildcard versions
- Prefer well-maintained packages with > 1000 GitHub stars

### Node.js (Frontend)
- `package-lock.json` committed
- `npm audit` in CI
- No wildcard versions in `package.json`
- Prefer packages with known maintainers

## Build Integrity

### Docker Images
- Base images pinned to specific digest (not just tag)
- Multi-stage builds to minimize attack surface
- No secrets in Docker layers
- Image scanning before deployment (future)

### CI/CD Pipeline
- All CI runs in isolated containers
- No shared state between CI runs
- Artifacts stored in trusted registry
- Deployment requires explicit approval for production

## Provenance (Future Roadmap)

### SLSA Level 1 (Current)
- Build process documented
- Build from version-controlled source
- Automated build process

### SLSA Level 2 (Target)
- Build service generates provenance
- Provenance includes source and build metadata
- Consumer can verify provenance

## Third-Party Service Trust

| Service | Trust Level | Mitigation |
|---------|------------|------------|
| OpenAI API | High | Fallback to Anthropic, usage monitoring |
| Anthropic API | High | Fallback to OpenAI |
| WhatsApp Business API | High | Official Meta partner API |
| PostgreSQL | Self-hosted | Full control, backup strategy |
| Redis | Self-hosted | Full control, not sole data store |
| AWS S3 / MinIO | High | Encryption at rest, access controls |

## Incident Response (Supply Chain)

If a dependency is found vulnerable:
1. Assess impact (is it in our dependency tree? Is it reachable?)
2. If critical: immediate patch or removal
3. If high: patch within 24 hours
4. If medium: patch within 1 week
5. Document in decision log
