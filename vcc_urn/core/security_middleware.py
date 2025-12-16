"""
Security middleware for VCC-URN
Adds security headers to protect against common web vulnerabilities
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    
    Headers added:
    - X-Content-Type-Options: Prevent MIME type sniffing
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: Enable XSS protection in older browsers
    - Strict-Transport-Security: Force HTTPS (if enabled)
    - Content-Security-Policy: Restrict resource loading
    - Referrer-Policy: Control referrer information
    - Permissions-Policy: Restrict browser features
    """
    
    def __init__(self, app, enable_hsts: bool = False, hsts_max_age: int = 31536000):
        """
        Initialize security headers middleware.
        
        Args:
            app: The ASGI application
            enable_hsts: Whether to enable HSTS (only for HTTPS deployments)
            hsts_max_age: HSTS max-age in seconds (default: 1 year)
        """
        super().__init__(app)
        self.enable_hsts = enable_hsts
        self.hsts_max_age = hsts_max_age
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS protection for older browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HSTS: Force HTTPS (only enable if deployed with HTTPS)
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = f"max-age={self.hsts_max_age}; includeSubDomains"
        
        # Content Security Policy: Restrict resource loading
        # This is a restrictive policy suitable for an API
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'",  # unsafe-inline needed for Swagger UI
            "style-src 'self' 'unsafe-inline'",   # unsafe-inline needed for Swagger UI
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # Referrer Policy: Don't leak referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy: Restrict browser features
        permissions_directives = [
            "accelerometer=()",
            "camera=()",
            "geolocation=()",
            "gyroscope=()",
            "magnetometer=()",
            "microphone=()",
            "payment=()",
            "usb=()"
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions_directives)
        
        return response
