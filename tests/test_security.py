"""
Security tests for VCC-URN system
Tests input validation, authentication, and other security features
"""
import pytest
from starlette.testclient import TestClient
from fastapi import FastAPI

from vcc_urn.core.validation import (
    validate_manifest,
    validate_urn_length,
    validate_batch_size,
    validate_state_code,
    validate_domain,
    validate_obj_type,
    validate_local_aktenzeichen,
    sanitize_log_value,
    MAX_URN_LENGTH,
    MAX_BATCH_SIZE,
    MAX_MANIFEST_SIZE,
)


class TestInputValidation:
    """Test input validation to prevent injection attacks and DoS"""
    
    def test_validate_urn_length_valid(self):
        """Valid URN should pass"""
        urn = "urn:de:nrw:bimschg:anlage:4711:00000000-0000-0000-0000-000000000000"
        assert validate_urn_length(urn) == urn
    
    def test_validate_urn_length_too_long(self):
        """URN exceeding max length should raise ValueError"""
        urn = "x" * (MAX_URN_LENGTH + 1)
        with pytest.raises(ValueError, match="URN too long"):
            validate_urn_length(urn)
    
    def test_validate_batch_size_valid(self):
        """Valid batch size should pass"""
        urns = [f"urn:de:nrw:bimschg:anlage:{i}:00000000-0000-0000-0000-000000000000" for i in range(10)]
        assert validate_batch_size(urns) == urns
    
    def test_validate_batch_size_too_large(self):
        """Batch exceeding max size should raise ValueError"""
        urns = ["urn:de:nrw:bimschg:anlage:test:00000000-0000-0000-0000-000000000000"] * (MAX_BATCH_SIZE + 1)
        with pytest.raises(ValueError, match="Batch too large"):
            validate_batch_size(urns)
    
    def test_validate_state_code_valid(self):
        """Valid state codes should pass"""
        assert validate_state_code("nrw") == "nrw"
        assert validate_state_code("NRW") == "nrw"  # Should normalize to lowercase
        assert validate_state_code("by") == "by"
    
    def test_validate_state_code_invalid_format(self):
        """Invalid state code format should raise ValueError"""
        with pytest.raises(ValueError, match="Invalid state code format"):
            validate_state_code("invalid123")
        with pytest.raises(ValueError, match="Invalid state code format"):
            validate_state_code("a")
        with pytest.raises(ValueError, match="Invalid state code format"):
            validate_state_code("abcd")
    
    def test_validate_state_code_empty(self):
        """Empty state code should raise ValueError"""
        with pytest.raises(ValueError, match="State code cannot be empty"):
            validate_state_code("")
    
    def test_validate_domain_valid(self):
        """Valid domains should pass"""
        assert validate_domain("bimschg") == "bimschg"
        assert validate_domain("BimSchG") == "bimschg"  # Should normalize
    
    def test_validate_domain_invalid_chars(self):
        """Domain with invalid characters should raise ValueError"""
        with pytest.raises(ValueError, match="Invalid domain format"):
            validate_domain("domain@invalid")
        with pytest.raises(ValueError, match="Invalid domain format"):
            validate_domain("domain with spaces")
    
    def test_validate_obj_type_valid(self):
        """Valid object types should pass"""
        assert validate_obj_type("anlage") == "anlage"
        assert validate_obj_type("Anlage") == "anlage"  # Should normalize
    
    def test_validate_obj_type_invalid_chars(self):
        """Object type with invalid characters should raise ValueError"""
        with pytest.raises(ValueError, match="Invalid object type format"):
            validate_obj_type("type@invalid")
    
    def test_validate_local_aktenzeichen_valid(self):
        """Valid Aktenzeichen should pass"""
        akz = "4711-0815-K1"
        assert validate_local_aktenzeichen(akz) == akz
    
    def test_validate_local_aktenzeichen_control_chars(self):
        """Aktenzeichen with control characters should raise ValueError"""
        with pytest.raises(ValueError, match="invalid control characters"):
            validate_local_aktenzeichen("test\x00malicious")
        with pytest.raises(ValueError, match="invalid control characters"):
            validate_local_aktenzeichen("test\nmalicious")
    
    def test_validate_manifest_valid(self):
        """Valid manifest should pass"""
        manifest = {
            "urn": "urn:de:nrw:bimschg:anlage:4711:00000000-0000-0000-0000-000000000000",
            "type": "anlage",
            "domain": "bimschg",
            "country": "nrw",
            "uuid": "00000000-0000-0000-0000-000000000000",
            "local_aktenzeichen": "4711-0815-K1",
            "label": "Test Anlage"
        }
        result = validate_manifest(manifest)
        assert result["urn"] == manifest["urn"]
        assert result["type"] == manifest["type"]
    
    def test_validate_manifest_missing_required_field(self):
        """Manifest missing required fields should raise ValueError"""
        manifest = {
            "urn": "urn:de:nrw:bimschg:anlage:4711:00000000-0000-0000-0000-000000000000",
            "type": "anlage",
            # Missing domain, country, uuid
        }
        with pytest.raises(ValueError, match="Invalid manifest"):
            validate_manifest(manifest)
    
    def test_validate_manifest_invalid_format(self):
        """Manifest with invalid field format should raise ValueError"""
        manifest = {
            "urn": "urn:de:nrw:bimschg:anlage:4711:00000000-0000-0000-0000-000000000000",
            "type": "INVALID@TYPE",  # Invalid characters
            "domain": "bimschg",
            "country": "nrw",
            "uuid": "00000000-0000-0000-0000-000000000000",
        }
        with pytest.raises(ValueError, match="Invalid manifest"):
            validate_manifest(manifest)
    
    def test_validate_manifest_too_large(self):
        """Manifest exceeding max size should raise ValueError"""
        manifest = {
            "urn": "urn:de:nrw:bimschg:anlage:4711:00000000-0000-0000-0000-000000000000",
            "type": "anlage",
            "domain": "bimschg",
            "country": "nrw",
            "uuid": "00000000-0000-0000-0000-000000000000",
            "large_field": "x" * MAX_MANIFEST_SIZE  # Too large
        }
        with pytest.raises(ValueError, match="Manifest too large"):
            validate_manifest(manifest)


class TestLogSanitization:
    """Test log sanitization to prevent log injection"""
    
    def test_sanitize_log_value_removes_newlines(self):
        """Newlines should be removed to prevent log injection"""
        value = "normal\nmalicious\ninjection"
        sanitized = sanitize_log_value(value)
        assert "\n" not in sanitized
        assert "\r" not in sanitized
    
    def test_sanitize_log_value_removes_control_chars(self):
        """Control characters should be removed"""
        value = "test\x00\x01\x1fvalue"
        sanitized = sanitize_log_value(value)
        assert "\x00" not in sanitized
        assert "\x01" not in sanitized
        assert "\x1f" not in sanitized
    
    def test_sanitize_log_value_truncates_long_values(self):
        """Very long values should be truncated"""
        value = "x" * 1000
        sanitized = sanitize_log_value(value)
        assert len(sanitized) < 600  # Should be truncated
        assert "truncated" in sanitized
    
    def test_sanitize_log_value_handles_none(self):
        """None value should be handled"""
        assert sanitize_log_value(None) == "None"


class TestSecurityHeaders:
    """Test security headers middleware"""
    
    def test_security_headers_applied(self):
        """Security headers should be applied to responses"""
        from vcc_urn.core.security_middleware import SecurityHeadersMiddleware
        
        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware, enable_hsts=False)
        
        @app.get("/test")
        def test_endpoint():
            return {"status": "ok"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        # Check security headers
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "Content-Security-Policy" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Permissions-Policy" in response.headers
    
    def test_hsts_disabled_by_default(self):
        """HSTS should not be enabled by default (development)"""
        from vcc_urn.core.security_middleware import SecurityHeadersMiddleware
        
        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware, enable_hsts=False)
        
        @app.get("/test")
        def test_endpoint():
            return {"status": "ok"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        # HSTS should not be present when disabled
        assert "Strict-Transport-Security" not in response.headers
    
    def test_hsts_enabled_when_configured(self):
        """HSTS should be enabled when configured"""
        from vcc_urn.core.security_middleware import SecurityHeadersMiddleware
        
        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware, enable_hsts=True)
        
        @app.get("/test")
        def test_endpoint():
            return {"status": "ok"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        # HSTS should be present when enabled
        assert "Strict-Transport-Security" in response.headers
        assert "max-age=" in response.headers["Strict-Transport-Security"]


class TestConstantTimeComparison:
    """Test constant-time comparison to prevent timing attacks"""
    
    def test_constant_time_compare_equal(self):
        """Equal strings should return True"""
        from vcc_urn.core.security import _constant_time_compare
        
        assert _constant_time_compare("secret123", "secret123") is True
    
    def test_constant_time_compare_not_equal(self):
        """Different strings should return False"""
        from vcc_urn.core.security import _constant_time_compare
        
        assert _constant_time_compare("secret123", "secret456") is False
    
    def test_constant_time_compare_different_lengths(self):
        """Strings of different lengths should return False"""
        from vcc_urn.core.security import _constant_time_compare
        
        assert _constant_time_compare("short", "much_longer_string") is False
