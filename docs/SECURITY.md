# Security Best Practices - VCC-URN

This document outlines the security measures implemented in the VCC-URN system.

## Security Features Implemented

### 1. Input Validation and Sanitization

All user inputs are validated to prevent injection attacks and DoS:

- **Length Limits**: URNs, manifests, and other inputs have maximum length limits
- **Format Validation**: State codes, domains, object types use strict regex patterns
- **Character Filtering**: Control characters are blocked from inputs
- **Batch Size Limits**: Batch operations are limited to prevent resource exhaustion

Implementation: `vcc_urn/core/validation.py`

### 2. Authentication and Authorization

Multiple authentication modes supported:

- **API Key Authentication**: 
  - Constant-time comparison to prevent timing attacks
  - Role-based access control (RBAC)
  - Support for key-specific roles
  
- **OIDC/JWT Authentication**:
  - RS256 signature verification via JWKS
  - Token expiration validation
  - Audience and issuer validation
  - Role extraction from claims

Implementation: `vcc_urn/core/security.py`

### 3. Security Headers

Security headers are automatically added to all responses:

- **X-Content-Type-Options**: `nosniff` - Prevents MIME type sniffing
- **X-Frame-Options**: `DENY` - Prevents clickjacking
- **X-XSS-Protection**: `1; mode=block` - Enables XSS protection
- **Content-Security-Policy**: Restricts resource loading
- **Referrer-Policy**: `strict-origin-when-cross-origin` - Controls referrer information
- **Permissions-Policy**: Restricts browser features
- **Strict-Transport-Security** (HSTS): Forces HTTPS (when enabled)

Implementation: `vcc_urn/core/security_middleware.py`

### 4. Database Security

- **Connection Pooling**: Prevents resource exhaustion
  - Pool size: 10 connections
  - Max overflow: 20 connections
  - Pool timeout: 30 seconds
  - Connection recycling: 1 hour
  - Pre-ping: Test connections before use

- **Query Timeout**: PostgreSQL queries timeout after 30 seconds
- **Parameterized Queries**: SQLAlchemy ORM prevents SQL injection
- **Transaction Management**: Automatic rollback on errors

Implementation: `vcc_urn/db/session.py`

### 5. Error Handling

- **Information Disclosure Prevention**: Generic error messages for server errors
- **Structured Logging**: Detailed errors logged securely
- **Log Sanitization**: Prevents log injection attacks
- **Proper HTTP Status Codes**: 400 for client errors, 500 for server errors

Implementation: `vcc_urn/api/v1/endpoints.py`, `vcc_urn/core/validation.py`

### 6. Rate Limiting

Rate limiting is applied to prevent abuse:

- Global rate limits via SlowAPI
- Configurable per-endpoint limits
- Based on client IP address

Implementation: `app/main.py`

### 7. CORS Configuration

- **Development**: Wildcard CORS allowed (with warning if auth is enabled)
- **Production**: Explicit origin configuration required
- **Warning System**: Alerts when wildcard CORS is used with authentication

Implementation: `app/main.py`

### 8. Federation Security

- **Circuit Breaker**: Prevents cascading failures (5 failures, 60s timeout)
- **Retry Logic**: Exponential backoff for transient failures
- **Timeout Protection**: 3-second timeout on peer requests
- **mTLS Support**: Mutual TLS for peer-to-peer communication (Phase 2b)
- **Cache Poisoning Prevention**: Validates peer responses

Implementation: `vcc_urn/services/federation.py`

### 9. Dependency Security

All dependencies are checked for known vulnerabilities:

- **python-jose**: Updated to >=3.4.0 (fixes ECDSA vulnerability)
- **Regular Updates**: Dependencies should be updated regularly
- **Advisory Checks**: Run `gh-advisory-database` before adding dependencies

## Security Configuration

### Required for Production

1. **Disable Wildcard CORS**:
   ```bash
   URN_CORS_ORIGINS=https://your-domain.com,https://another-domain.com
   ```

2. **Enable Authentication**:
   ```bash
   # API Key mode
   URN_AUTH_MODE=apikey
   URN_API_KEYS=strong-random-key-1:admin,strong-random-key-2:reader
   
   # OR OIDC mode
   URN_AUTH_MODE=oidc
   URN_OIDC_ISSUER=https://your-issuer.com
   URN_OIDC_AUDIENCE=your-audience
   URN_OIDC_JWKS_URL=https://your-issuer.com/.well-known/jwks.json
   ```

3. **Use PostgreSQL** (not SQLite in production):
   ```bash
   URN_DB_URL=postgresql+psycopg://user:password@localhost:5432/urn
   ```

4. **Enable Structured Logging**:
   ```bash
   URN_LOG_LEVEL=INFO
   URN_LOG_FORMAT=json
   ```

5. **Configure HTTPS** and enable HSTS in deployment (not in application)

### Optional Security Enhancements

1. **Redis Cache** (for distributed deployments):
   ```bash
   URN_REDIS_ENABLED=true
   URN_REDIS_URL=redis://localhost:6379/0
   ```

2. **mTLS for Federation** (Phase 2b):
   ```bash
   URN_MTLS_ENABLED=true
   URN_MTLS_CA_CERT=/path/to/ca.crt
   URN_MTLS_CERT=/path/to/instance.crt
   URN_MTLS_KEY=/path/to/instance.key
   ```

3. **OpenTelemetry Tracing** (for audit trails):
   ```bash
   URN_TRACING_ENABLED=true
   URN_TRACING_ENDPOINT=http://localhost:4317
   ```

## Security Testing

Run security tests:
```bash
pytest tests/test_security.py -v
```

Run all tests:
```bash
pytest tests/ -v
```

## Security Checklist for Deployment

- [ ] Authentication is enabled (`URN_AUTH_MODE` != `none`)
- [ ] CORS origins are explicitly configured (not `*`)
- [ ] Using PostgreSQL (not SQLite)
- [ ] Strong API keys or OIDC configured
- [ ] HTTPS is configured at load balancer/reverse proxy level
- [ ] Database credentials are stored in secrets manager (not environment files)
- [ ] Logging is configured with JSON format for production
- [ ] Rate limiting is enabled
- [ ] Security headers are enabled
- [ ] Dependencies are up-to-date and vulnerability-free
- [ ] Regular backups are configured
- [ ] Monitoring and alerting are set up

## Vulnerability Reporting

If you discover a security vulnerability, please:

1. **DO NOT** create a public GitHub issue
2. Contact the maintainers privately
3. Provide detailed information about the vulnerability
4. Allow time for a fix before public disclosure

## Security Updates

- Review dependencies monthly for vulnerabilities
- Update to latest patch versions regularly
- Subscribe to security advisories for dependencies
- Monitor OWASP Top 10 and adjust as needed

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/20/faq/security.html)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security.html)
