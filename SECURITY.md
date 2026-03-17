# Security Policy for HELIOSICA

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of HELIOSICA seriously. If you believe you have found a security vulnerability, please report it to us as described below.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to:

**gitdeeper@gmail.com**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the following information in your report:

- Type of issue (e.g., buffer overflow, SQL injection, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## Preferred Languages

We prefer all communications to be in English.

## Policy

We follow the principle of [Responsible Disclosure](https://en.wikipedia.org/wiki/Responsible_disclosure).

## Security Considerations for Deployment

When deploying HELIOSICA in production, please consider the following security measures:

### 1. Environment Variables
- Never commit `.env` files to version control
- Use strong passwords for database connections
- Rotate API keys regularly
- Use secrets management services in production
- Example `.env` file should be `.env.example` only

### 2. Network Security
- Run services behind a firewall
- Use HTTPS/TLS for all web interfaces
- Restrict database access to localhost when possible
- Use VPN for remote connections
- Implement rate limiting for API endpoints

### 3. Authentication
- Change default passwords immediately
- Use strong password policies
- Enable 2FA for administrative access
- Implement rate limiting for login attempts

### 4. Data Security
- Encrypt sensitive data at rest
- Use secure backup strategies
- Implement data retention policies
- Verify checksums for downloaded datasets
- Use signed commits and tags

### 5. API Security
- Validate all input data
- Sanitize file paths and names
- Limit file upload sizes
- Use API keys with restricted permissions
- Log all access attempts
- Implement rate limiting (100 requests/minute default)

### 6. Alert System Security
- Alert credentials stored in environment variables
- SMS alerts via secure API (Twilio)
- Email alerts via SMTP with TLS
- No sensitive data in alert messages

### 7. Container Security
- Use specific image tags (not 'latest')
- Run containers as non-root user
- Scan images for vulnerabilities
- Use read-only root filesystems
- Limit container capabilities

### 8. Scientific Integrity
- Verify data provenance (NOAA/NASA sources)
- Document all assumptions
- Use version control for all code and data
- Maintain audit trails for predictions
- Validate against historical events (312-event catalogue)

## Security Updates

Security updates will be released as soon as possible after a vulnerability is confirmed. Updates will be announced via:

- GitHub releases
- PyPI package updates
- Project website announcements
- Direct email to registered users (optional)
- Security mailing list

## Responsible Disclosure Timeline

1. **Vulnerability Reported**: Reporter submits details
2. **Acknowledgment**: Within 48 hours, we acknowledge receipt
3. **Investigation**: We investigate and validate the report
4. **Fix Development**: We develop and test a fix
5. **Release**: We release a patched version
6. **Public Disclosure**: After users have time to update

## Critical Infrastructure Note

HELIOSICA provides real-time space weather alerts that may be used for:
- Satellite operator decisions
- Power grid protection
- Aviation radiation monitoring
- Emergency response planning

**False alerts** could cause unnecessary disruptions. **Missed alerts** could lead to infrastructure damage. Therefore:

- All alerts ≥G4 require human verification before broadcast
- GSSI uses ensemble forecasting with confidence intervals
- Multiple data sources are cross-checked (DSCOVR, ACE, SOHO)
- Historical validation ensures 88.4% accuracy

## Acknowledgements

We thank the security researchers and users who report vulnerabilities to us responsibly. Contributors will be acknowledged in release notes (unless they prefer anonymity).

## Contact

- **Email**: gitdeeper@gmail.com
- **PGP Key**: Available on request
- **ORCID**: 0009-0003-8903-0029
- **Emergency**: +1 (614) 264-2074 (for critical infrastructure issues only)

## License

This security policy is part of the HELIOSICA project and is covered under the MIT License.
