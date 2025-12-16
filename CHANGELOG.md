# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-12-16

### Added

#### Security Features
- **Input Validation & Sanitization** ([#996b697](https://github.com/makr-code/VCC-URN/commit/996b697))
  - Length limits on all URN components (512 chars max)
  - Manifest size limit (100KB max)
  - Batch operation limit (100 URNs max)
  - Regex validation for state codes, domains, and object types
  - Control character filtering to prevent log injection
  - New `vcc_urn/core/validation.py` module with reusable validators

- **Security Headers Middleware** ([#996b697](https://github.com/makr-code/VCC-URN/commit/996b697))
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Content-Security-Policy with dev/prod modes
  - Referrer-Policy: strict-origin-when-cross-origin
  - Permissions-Policy restricting browser features
  - Optional HSTS support for HTTPS deployments

- **Authentication Security** ([#996b697](https://github.com/makr-code/VCC-URN/commit/996b697))
  - Constant-time API key comparison using `secrets.compare_digest()`
  - Prevents timing attacks on authentication

- **Database Security** ([#4b68a67](https://github.com/makr-code/VCC-URN/commit/4b68a67))
  - Connection pooling configuration (10 base, 20 max overflow, 30s timeout)
  - Connection recycling (1 hour)
  - Pre-ping enabled for connection health checks
  - PostgreSQL query timeout (30 seconds, configurable)

- **Documentation** ([#4b68a67](https://github.com/makr-code/VCC-URN/commit/4b68a67), [#edc2c5a](https://github.com/makr-code/VCC-URN/commit/edc2c5a))
  - `docs/SECURITY.md`: Comprehensive security features and guidelines
  - `docs/BEST_PRACTICES.md`: Development and deployment best practices
  - `docs/SECURITY_REVIEW_SUMMARY.md`: Complete security audit report

- **Testing** ([#996b697](https://github.com/makr-code/VCC-URN/commit/996b697))
  - 27 new security tests
  - Input validation tests
  - Security headers tests
  - Constant-time comparison tests
  - Log sanitization tests

#### Configuration
- CORS configuration warnings when wildcard CORS is used with authentication
- Configurable database query timeout constant (`DB_QUERY_TIMEOUT_MS`)
- Development vs. production CSP modes

### Changed

#### Error Handling
- Improved error messages to prevent information disclosure
- Client errors (400) return validation details
- Server errors (500) return generic messages
- Added comprehensive structured logging with sanitization
- Log injection prevention through control character removal

#### Security Improvements
- All user inputs are now validated before processing
- Log values are sanitized to prevent log injection attacks
- Error responses no longer expose internal system details

### Fixed

#### Security Vulnerabilities
- **CVE Fix**: Updated `python-jose` from 3.3.0 to >=3.4.0 (fixes ECDSA algorithm confusion vulnerability)
- SQL injection protection confirmed (SQLAlchemy ORM with parameterized queries)

#### Code Quality
- Extracted control character pattern as module constant
- Made database timeout configurable
- Moved test imports to module level
- Improved CSP configuration with environment-aware modes

### Security

#### Vulnerability Assessment
- **CodeQL Scan**: 0 security alerts
- **Dependency Scan**: 1 vulnerability fixed (python-jose)
- **Security Posture**: GOOD ✅
- **Recommendation**: APPROVED for production deployment

#### Security Testing
- All 42 tests passing (15 original + 27 new security tests)
- Comprehensive security test coverage
- No regressions detected

## [0.1.0] - 2024-11-XX

### Added
- Initial URN resolver implementation
- FastAPI-based REST API
- PostgreSQL and SQLite support
- Federation support for peer-to-peer URN resolution
- Admin API for catalog management
- GraphQL API (optional)
- OIDC and API key authentication
- Prometheus metrics
- Rate limiting
- Alembic database migrations
- Docker and Docker Compose support

[0.2.0]: https://github.com/makr-code/VCC-URN/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/makr-code/VCC-URN/releases/tag/v0.1.0
