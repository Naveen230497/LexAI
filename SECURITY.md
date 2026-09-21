# Security Policy

## Supported Versions
Only the latest main branch is currently supported with security updates.

## Reporting a Vulnerability
If you discover a security vulnerability within LexAI, please do not disclose it publicly. Instead, submit an issue to the repository with the `security` label, or contact the repository owner directly.

### Security Features Implemented
* **Prompt Injection Protection:** Magic-byte validation and Regex pattern matching protect the GenAI pipeline.
* **Rate Limiting:** IP-based slowapi limits prevent DDoS and API abuse.
* **Secrets Management:** No secrets are committed; `.env` is rigorously ignored via `.gitignore`.
