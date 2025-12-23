# Security Policy

## Supported Versions

We actively maintain and provide security updates for the following versions:

| Version | Supported          | Status |
| ------- | ------------------ | ------ |
| 1.2.x   | :white_check_mark: | Active development |
| 1.1.x   | :white_check_mark: | Security fixes only |
| 1.0.x   | :x:                | No longer supported |
| < 1.0   | :x:                | No longer supported |

**Recommendation**: Always use the latest stable release from the `main` branch.

---

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

### 1. **Do NOT** Open a Public Issue

Security vulnerabilities should **not** be disclosed publicly until a fix is available.

### 2. Report Privately

Please report security vulnerabilities via one of these methods:

- **Preferred**: Use GitHub's [Security Advisories](https://github.com/chriskoch/ngx-renamer/security/advisories/new) feature
- **Alternative**: Email the maintainer directly (see GitHub profile for contact)

### 3. Include Details

When reporting a vulnerability, please include:

- **Description**: Clear description of the vulnerability
- **Impact**: What could an attacker do with this vulnerability?
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Affected Versions**: Which versions are affected?
- **Proof of Concept**: Example code or configuration demonstrating the issue
- **Suggested Fix**: If you have ideas for fixing it (optional)

### 4. Response Timeline

You can expect the following response timeline:

- **Initial Response**: Within 48 hours
- **Confirmation**: Within 1 week
- **Fix Timeline**: Depends on severity
  - **Critical**: Within 7 days
  - **High**: Within 14 days
  - **Medium**: Within 30 days
  - **Low**: Next release cycle

### 5. Disclosure Process

Once a fix is available:

1. We'll create a security advisory on GitHub
2. We'll release a patched version
3. We'll publicly disclose the vulnerability details
4. We'll credit you (unless you prefer to remain anonymous)

---

## Security Considerations

### API Keys and Secrets

**Never commit sensitive information:**

- ❌ **Don't** commit `.env` files
- ❌ **Don't** hardcode API keys in code
- ❌ **Don't** commit credentials in docker-compose.yml
- ✅ **Do** use environment variables
- ✅ **Do** use `.env.example` as a template
- ✅ **Do** add sensitive files to `.gitignore`

**Proper API Key Handling:**

```yaml
# ✅ Good - Use environment variables
webserver:
  environment:
    OPENAI_API_KEY: ${OPENAI_API_KEY}
    PAPERLESS_NGX_API_KEY: ${PAPERLESS_API_KEY}
```

```python
# ❌ Bad - Hardcoded secrets
openai_api_key = "sk-1234567890abcdef"  # NEVER DO THIS
```

### Network Security

**Docker Networking:**

- Internal services use Docker service names (e.g., `http://webserver:8000`)
- External APIs use HTTPS (OpenAI)
- Ollama can use `localhost` or Docker internal networking
- No unnecessary port exposure

**API Communications:**

- OpenAI API: Always HTTPS
- Paperless API: Internal Docker network (no external exposure)
- Ollama API: Can be local HTTP (no internet transit)

### Container Security

**Best Practices Implemented:**

- ✅ Read-only source mounts (`:ro`)
- ✅ Non-root execution (inherits from Paperless NGX)
- ✅ Isolated virtual environment
- ✅ Minimal attack surface
- ✅ No privileged containers

**What We Don't Do:**

- ❌ Run as root
- ❌ Use `--privileged` flag
- ❌ Expose unnecessary ports
- ❌ Install unnecessary packages

### Dependency Security

**Monitoring:**

We actively monitor dependencies for known vulnerabilities:

- Python dependencies in `requirements.txt`
- Development dependencies in `requirements-dev.txt`
- Docker base images

**Update Policy:**

- Security patches: Applied immediately
- Minor updates: Reviewed and tested
- Major updates: Evaluated for breaking changes

**Checking for Vulnerabilities:**

```bash
# Check for known vulnerabilities
pip install pip-audit
pip-audit

# Update dependencies
pip install --upgrade -r requirements.txt
```

### Input Validation

**Document Content:**

- OCR text is sent to LLM providers
- No validation required (LLMs handle arbitrary text)
- Titles are truncated to 127 characters max
- No SQL injection risk (uses Paperless API, not direct DB)

**API Inputs:**

- Paperless API: Authenticated via token
- OpenAI API: Authenticated via API key
- Ollama API: Optional authentication via API key
- All inputs validated by respective APIs

### Structured Outputs

**JSON Parsing Security:**

Starting in v1.2.0, we use structured outputs with JSON schemas:

- ✅ Schema validation prevents injection
- ✅ Auto-truncation prevents overflow
- ✅ Error handling for malformed responses
- ✅ No `eval()` or dynamic code execution

---

## Known Security Limitations

### 1. LLM Provider Trust

**Limitation**: You must trust your LLM provider (OpenAI or Ollama).

- Document content is sent to the LLM for title generation
- OpenAI: Data sent to OpenAI servers (see their [privacy policy](https://openai.com/privacy))
- Ollama: Data stays on your local machine

**Mitigation**: Use local Ollama for sensitive documents.

### 2. API Key Exposure

**Limitation**: API keys must be stored in environment variables or `.env` files.

- If container is compromised, API keys could be exposed
- Environment variables visible to anyone with container access

**Mitigation**:
- Use secrets management (Docker secrets, Kubernetes secrets)
- Rotate API keys regularly
- Use API key restrictions (IP whitelisting, usage limits)

### 3. Paperless NGX API Access

**Limitation**: Requires a Paperless API token with document read/write access.

- If token is compromised, attacker can read/modify all documents
- Token stored in environment variables

**Mitigation**:
- Use dedicated API token for ngx-renamer
- Rotate tokens regularly
- Monitor API access logs in Paperless

---

## Security Best Practices for Users

### Production Deployments

1. **Use HTTPS for external access**
   - Paperless should be behind HTTPS reverse proxy
   - Never expose Paperless directly to the internet

2. **Secure API tokens**
   - Use strong, randomly generated tokens
   - Rotate tokens periodically
   - Don't share tokens across services

3. **Keep software updated**
   - Update to latest ngx-renamer version
   - Keep Paperless NGX updated
   - Update Docker base images

4. **Monitor logs**
   - Check Paperless logs regularly
   - Watch for unusual API activity
   - Set up alerts for errors

5. **Use local Ollama for sensitive data**
   - Keeps document content on-premises
   - No cloud API costs
   - Full data privacy

### Development Environments

1. **Never use production API keys in development**
2. **Don't commit `.env` files**
3. **Use separate Paperless instances for dev/prod**
4. **Review code changes for security implications**

---

## Security Checklist

Before deploying ngx-renamer:

- [ ] API keys stored in environment variables, not hardcoded
- [ ] `.env` file added to `.gitignore` (already done)
- [ ] Paperless behind HTTPS reverse proxy
- [ ] Strong, unique API tokens generated
- [ ] No unnecessary ports exposed
- [ ] Using latest stable version
- [ ] Reviewed [docker-compose.yml](README.md) example
- [ ] Tested with sample documents before production use
- [ ] Logs configured and monitored
- [ ] Backup strategy in place

---

## Vulnerability Disclosure History

No vulnerabilities have been reported or disclosed for ngx-renamer as of version 1.2.2.

This section will be updated if any vulnerabilities are discovered and fixed.

---

## Security Updates

Security updates will be announced via:

- GitHub Security Advisories
- Release notes in CHANGELOG.md
- GitHub Releases page

Subscribe to repository notifications to stay informed.

---

## Resources

- [Paperless NGX Security](https://docs.paperless-ngx.com/configuration/#security)
- [OpenAI Security Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)
- [Docker Security](https://docs.docker.com/engine/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

## Contact

For security concerns, please use:

- **GitHub Security Advisories**: https://github.com/chriskoch/ngx-renamer/security/advisories/new
- **Issues** (for non-security bugs): https://github.com/chriskoch/ngx-renamer/issues

Thank you for helping keep ngx-renamer secure! 🔒

---

**Version**: 1.2.2
**Last Updated**: 2024-12-23
