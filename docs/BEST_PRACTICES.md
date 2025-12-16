# Best Practices - VCC-URN

This document outlines best practices for developing, deploying, and maintaining the VCC-URN system.

## Code Quality

### 1. Linting and Formatting

Run linters before committing:

```bash
# Format code with Black
black vcc_urn/ app/ tests/

# Lint with Ruff
ruff check vcc_urn/ app/ tests/

# Type checking with mypy
mypy vcc_urn/ app/
```

### 2. Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Run tests before committing:

```bash
pytest tests/ -v
```

### 3. Code Organization

- **Separation of Concerns**: Keep business logic in services, data access in repositories
- **Dependency Injection**: Use FastAPI's dependency injection system
- **Type Hints**: Use type hints for all function signatures
- **Documentation**: Add docstrings to all public functions and classes

### 4. Error Handling

- Use specific exception types
- Log errors with context
- Return appropriate HTTP status codes
- Don't expose internal details in error messages

Example:
```python
try:
    result = service.process(data)
except ValueError as e:
    logger.warning("Validation failed", extra={"error": str(e)})
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error("Processing failed", extra={"error": str(e)})
    raise HTTPException(status_code=500, detail="Internal server error")
```

## Database Best Practices

### 1. Migrations

Always use Alembic migrations for schema changes:

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new column"

# Review the generated migration file
# Apply migrations
alembic upgrade head
```

### 2. Connection Management

- Use connection pooling (already configured)
- Close sessions properly (use dependency injection)
- Don't hold connections longer than needed

### 3. Query Optimization

- Use indexes for frequently queried columns
- Limit result sets (pagination)
- Avoid N+1 queries (use eager loading)

### 4. Transactions

- Keep transactions short
- Use rollback on errors (automatic with SessionLocal)
- Avoid nested transactions

## API Design Best Practices

### 1. Versioning

- Use URL path versioning (`/api/v1/...`)
- Maintain backwards compatibility
- Deprecate endpoints before removing them

### 2. Request/Response Format

- Use Pydantic models for validation
- Return consistent response structures
- Include appropriate metadata (counts, pagination info)

### 3. HTTP Methods

- **GET**: Retrieve resources (idempotent, cacheable)
- **POST**: Create resources or trigger actions
- **PUT/PATCH**: Update resources (use PATCH for partial updates)
- **DELETE**: Remove resources

### 4. Status Codes

- **200 OK**: Successful GET, PUT, PATCH
- **201 Created**: Successful POST that creates a resource
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Client error (validation failed)
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Server error

## Performance Best Practices

### 1. Caching

- Use Redis for distributed caching
- Set appropriate TTL values
- Invalidate cache on updates

### 2. Batch Operations

- Use batch endpoints for multiple operations
- Limit batch size to prevent resource exhaustion
- Process batches asynchronously for large datasets

### 3. Rate Limiting

- Apply rate limits to prevent abuse
- Use different limits for authenticated vs. anonymous users
- Return 429 Too Many Requests with Retry-After header

### 4. Async Processing

- Use async/await for I/O-bound operations
- Offload long-running tasks to background workers
- Return 202 Accepted for async operations

## Security Best Practices

See [SECURITY.md](SECURITY.md) for detailed security guidelines.

### Quick Checklist

- ✅ Validate all inputs
- ✅ Use authentication and authorization
- ✅ Apply rate limiting
- ✅ Enable security headers
- ✅ Use HTTPS in production
- ✅ Keep dependencies updated
- ✅ Log security events
- ✅ Regular security audits

## Deployment Best Practices

### 1. Environment Configuration

- Use environment variables for configuration
- Never commit secrets to version control
- Use different configurations for dev/staging/production

### 2. Container Deployment

```dockerfile
# Use official Python image
FROM python:3.10-slim

# Don't run as root
RUN useradd -m -u 1000 urn
USER urn

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Run with gunicorn (production)
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker"]
```

### 3. Health Checks

- Implement health and readiness endpoints
- Use `/healthz` for liveness checks
- Use `/readyz` for readiness checks

### 4. Monitoring

- Enable Prometheus metrics (`/metrics`)
- Set up alerting for errors and performance issues
- Track key business metrics (URN generation rate, resolution time)

### 5. Logging

- Use structured logging (JSON format)
- Log appropriate detail level
- Centralize logs for distributed systems
- Implement log rotation

### 6. Scaling

- Design for horizontal scaling
- Use Redis for shared state
- Avoid session state in application
- Use load balancer for traffic distribution

## Federation Best Practices

### 1. Circuit Breaker

- Configure appropriate failure thresholds
- Monitor circuit breaker state
- Implement fallback strategies

### 2. Timeouts

- Set reasonable timeouts (3-5 seconds)
- Handle timeout errors gracefully
- Return cached data when peers are unavailable

### 3. mTLS

- Use mutual TLS for peer communication
- Rotate certificates regularly
- Store private keys securely

### 4. Service Discovery

- Use Kubernetes DNS for service discovery
- Implement health checks for peers
- Remove unhealthy peers from rotation

## Maintenance Best Practices

### 1. Regular Updates

- Update dependencies monthly
- Review security advisories
- Test updates in staging before production

### 2. Backups

- Backup database regularly (daily recommended)
- Test restore procedures
- Store backups in different location

### 3. Monitoring

- Monitor application performance
- Track error rates
- Set up alerting for anomalies

### 4. Documentation

- Keep README up-to-date
- Document API changes
- Maintain changelog

## Development Workflow

### 1. Branching Strategy

- `main`: Production-ready code
- `develop`: Integration branch
- Feature branches: `feature/feature-name`
- Bugfix branches: `bugfix/bug-name`

### 2. Code Review

- Review all code before merging
- Check for security issues
- Verify tests pass
- Ensure documentation is updated

### 3. Continuous Integration

- Run tests on all commits
- Run linters and type checkers
- Check for security vulnerabilities
- Build and test Docker images

### 4. Versioning

- Use semantic versioning (MAJOR.MINOR.PATCH)
- Tag releases in git
- Maintain CHANGELOG.md

## Common Pitfalls to Avoid

1. **Don't disable security features in production**
   - Always use authentication
   - Never use wildcard CORS with auth enabled
   - Don't disable security headers

2. **Don't log sensitive data**
   - API keys, passwords, tokens
   - Personal information (GDPR compliance)
   - Full error stack traces to clients

3. **Don't trust user input**
   - Always validate
   - Sanitize for logging
   - Use parameterized queries

4. **Don't expose internal details**
   - Generic error messages to clients
   - Don't return stack traces
   - Hide infrastructure details

5. **Don't neglect error handling**
   - Handle all exceptions
   - Log errors with context
   - Return appropriate status codes

6. **Don't ignore performance**
   - Use connection pooling
   - Implement caching
   - Limit result sets
   - Use indexes

7. **Don't skip testing**
   - Write unit tests
   - Write integration tests
   - Test error cases
   - Test security features

## Resources

- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy Best Practices](https://docs.sqlalchemy.org/en/20/orm/queryguide/)
- [Python Best Practices](https://docs.python-guide.org/)
- [12-Factor App](https://12factor.net/)
- [API Design Best Practices](https://swagger.io/resources/articles/best-practices-in-api-design/)
