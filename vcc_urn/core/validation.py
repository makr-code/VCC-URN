"""
Input validation utilities for VCC-URN
Security: Validate and sanitize all inputs to prevent injection attacks
"""
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator, ValidationError, ConfigDict


# Security limits to prevent DoS attacks
MAX_URN_LENGTH = 512
MAX_MANIFEST_SIZE = 100_000  # 100KB max manifest size
MAX_LOCAL_AKTENZEICHEN_LENGTH = 256
MAX_DOMAIN_LENGTH = 64
MAX_OBJ_TYPE_LENGTH = 64
MAX_STATE_LENGTH = 10
MAX_UUID_LENGTH = 36
MAX_VERSION_LENGTH = 64
MAX_BATCH_SIZE = 100  # Maximum URNs per batch request


class ManifestValidator(BaseModel):
    """Validate manifest structure and content"""
    
    model_config = ConfigDict(
        extra="allow",
        str_max_length=10000  # Max length for any additional string field
    )
    
    # Required fields
    urn: str = Field(..., max_length=MAX_URN_LENGTH)
    type: str = Field(..., max_length=MAX_OBJ_TYPE_LENGTH, pattern=r"^[a-z0-9\-]+$")
    domain: str = Field(..., max_length=MAX_DOMAIN_LENGTH, pattern=r"^[a-z0-9\-]+$")
    country: str = Field(..., max_length=MAX_STATE_LENGTH, pattern=r"^[a-z]{2,3}$")
    uuid: str = Field(..., max_length=MAX_UUID_LENGTH, pattern=r"^[0-9a-fA-F\-]{36}$")
    
    # Optional fields
    local_aktenzeichen: Optional[str] = Field(None, max_length=MAX_LOCAL_AKTENZEICHEN_LENGTH)
    label: Optional[str] = Field(None, max_length=512)
    version: Optional[str] = Field(None, max_length=MAX_VERSION_LENGTH)


def validate_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate manifest structure and content.
    
    Args:
        manifest: The manifest dictionary to validate
        
    Returns:
        Validated manifest dictionary
        
    Raises:
        ValueError: If manifest is invalid
    """
    # Check manifest size
    import json
    manifest_json = json.dumps(manifest, ensure_ascii=False)
    if len(manifest_json) > MAX_MANIFEST_SIZE:
        raise ValueError(f"Manifest too large: {len(manifest_json)} bytes (max: {MAX_MANIFEST_SIZE})")
    
    try:
        # Validate using Pydantic model
        validated = ManifestValidator(**manifest)
        return validated.model_dump()
    except ValidationError as e:
        # Convert Pydantic validation error to simple ValueError
        errors = []
        for error in e.errors():
            field = '.'.join(str(x) for x in error['loc'])
            msg = error['msg']
            errors.append(f"{field}: {msg}")
        raise ValueError(f"Invalid manifest: {'; '.join(errors)}")


def validate_urn_length(urn: str) -> str:
    """
    Validate URN length to prevent DoS attacks.
    
    Args:
        urn: The URN string to validate
        
    Returns:
        The validated URN
        
    Raises:
        ValueError: If URN is too long
    """
    if len(urn) > MAX_URN_LENGTH:
        raise ValueError(f"URN too long: {len(urn)} characters (max: {MAX_URN_LENGTH})")
    return urn


def validate_batch_size(urns: List[str]) -> List[str]:
    """
    Validate batch size to prevent DoS attacks.
    
    Args:
        urns: List of URNs to validate
        
    Returns:
        The validated URN list
        
    Raises:
        ValueError: If batch is too large
    """
    if len(urns) > MAX_BATCH_SIZE:
        raise ValueError(f"Batch too large: {len(urns)} URNs (max: {MAX_BATCH_SIZE})")
    
    # Also validate each individual URN length
    for urn in urns:
        validate_urn_length(urn)
    
    return urns


def sanitize_log_value(value: Any) -> str:
    """
    Sanitize value for safe logging (prevent log injection).
    
    Args:
        value: The value to sanitize
        
    Returns:
        Sanitized string safe for logging
    """
    if value is None:
        return "None"
    
    s = str(value)
    
    # Remove newlines and control characters to prevent log injection
    s = re.sub(r'[\r\n\t\x00-\x1f\x7f-\x9f]', ' ', s)
    
    # Truncate very long values
    max_log_length = 500
    if len(s) > max_log_length:
        s = s[:max_log_length] + "...(truncated)"
    
    return s


def validate_state_code(state: str) -> str:
    """
    Validate state code format.
    
    Args:
        state: The state code to validate
        
    Returns:
        Normalized state code (lowercase)
        
    Raises:
        ValueError: If state code is invalid
    """
    state = state.strip().lower()
    
    if not state:
        raise ValueError("State code cannot be empty")
    
    if len(state) > MAX_STATE_LENGTH:
        raise ValueError(f"State code too long: {len(state)} characters (max: {MAX_STATE_LENGTH})")
    
    if not re.match(r"^[a-z]{2,3}$", state):
        raise ValueError(f"Invalid state code format: {state}")
    
    return state


def validate_domain(domain: str) -> str:
    """
    Validate domain format.
    
    Args:
        domain: The domain to validate
        
    Returns:
        Normalized domain (lowercase)
        
    Raises:
        ValueError: If domain is invalid
    """
    domain = domain.strip().lower()
    
    if not domain:
        raise ValueError("Domain cannot be empty")
    
    if len(domain) > MAX_DOMAIN_LENGTH:
        raise ValueError(f"Domain too long: {len(domain)} characters (max: {MAX_DOMAIN_LENGTH})")
    
    if not re.match(r"^[a-z0-9\-]+$", domain):
        raise ValueError(f"Invalid domain format: {domain}")
    
    return domain


def validate_obj_type(obj_type: str) -> str:
    """
    Validate object type format.
    
    Args:
        obj_type: The object type to validate
        
    Returns:
        Normalized object type (lowercase)
        
    Raises:
        ValueError: If object type is invalid
    """
    obj_type = obj_type.strip().lower()
    
    if not obj_type:
        raise ValueError("Object type cannot be empty")
    
    if len(obj_type) > MAX_OBJ_TYPE_LENGTH:
        raise ValueError(f"Object type too long: {len(obj_type)} characters (max: {MAX_OBJ_TYPE_LENGTH})")
    
    if not re.match(r"^[a-z0-9\-]+$", obj_type):
        raise ValueError(f"Invalid object type format: {obj_type}")
    
    return obj_type


def validate_local_aktenzeichen(local: str) -> str:
    """
    Validate local Aktenzeichen.
    
    Args:
        local: The local Aktenzeichen to validate
        
    Returns:
        The validated Aktenzeichen
        
    Raises:
        ValueError: If local Aktenzeichen is invalid
    """
    if not local:
        raise ValueError("Local Aktenzeichen cannot be empty")
    
    if len(local) > MAX_LOCAL_AKTENZEICHEN_LENGTH:
        raise ValueError(f"Local Aktenzeichen too long: {len(local)} characters (max: {MAX_LOCAL_AKTENZEICHEN_LENGTH})")
    
    # Allow a wide range of characters for Aktenzeichen, but prevent control characters
    if re.search(r'[\x00-\x1f\x7f-\x9f]', local):
        raise ValueError("Local Aktenzeichen contains invalid control characters")
    
    return local
