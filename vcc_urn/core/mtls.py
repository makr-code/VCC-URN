"""
mTLS (Mutual TLS) Configuration for VCC-URN Federation

Phase 2b: Secure peer-to-peer authentication using mutual TLS.
All certificates are managed locally (on-premise, no cloud PKI dependency).

This module provides:
- Client certificate verification for incoming federation requests
- Client certificate presentation for outgoing federation requests
- Certificate management utilities

Security Model:
- Each VCC-URN instance has its own certificate signed by a shared CA
- Federation peers verify each other's certificates before communication
- Certificate chain: CA → Instance Certificate
"""

import os
import ssl
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MTLSConfig:
    """mTLS configuration for federation communication"""
    
    # Enable/disable mTLS
    enabled: bool = False
    
    # CA certificate (for verifying peer certificates)
    ca_cert_path: Optional[str] = None
    
    # This instance's certificate (for presenting to peers)
    cert_path: Optional[str] = None
    
    # This instance's private key
    key_path: Optional[str] = None
    
    # Verify peer certificates (set to False only for testing)
    verify_peer: bool = True
    
    # Minimum TLS version (TLS 1.2 or 1.3)
    min_tls_version: str = "TLSv1_2"
    
    @classmethod
    def from_env(cls) -> "MTLSConfig":
        """Load mTLS configuration from environment variables"""
        return cls(
            enabled=os.getenv("URN_MTLS_ENABLED", "").lower() in ("true", "1", "yes"),
            ca_cert_path=os.getenv("URN_MTLS_CA_CERT"),
            cert_path=os.getenv("URN_MTLS_CERT"),
            key_path=os.getenv("URN_MTLS_KEY"),
            verify_peer=os.getenv("URN_MTLS_VERIFY_PEER", "true").lower() in ("true", "1", "yes"),
            min_tls_version=os.getenv("URN_MTLS_MIN_VERSION", "TLSv1_2"),
        )
    
    def validate(self) -> bool:
        """Validate mTLS configuration"""
        if not self.enabled:
            return True
        
        errors = []
        
        if not self.ca_cert_path:
            errors.append("URN_MTLS_CA_CERT is required when mTLS is enabled")
        elif not Path(self.ca_cert_path).is_file():
            errors.append(f"CA certificate not found: {self.ca_cert_path}")
        
        if not self.cert_path:
            errors.append("URN_MTLS_CERT is required when mTLS is enabled")
        elif not Path(self.cert_path).is_file():
            errors.append(f"Certificate not found: {self.cert_path}")
        
        if not self.key_path:
            errors.append("URN_MTLS_KEY is required when mTLS is enabled")
        elif not Path(self.key_path).is_file():
            errors.append(f"Private key not found: {self.key_path}")
        
        if errors:
            for error in errors:
                logger.error(f"mTLS configuration error: {error}")
            return False
        
        logger.info("mTLS configuration validated successfully")
        return True
    
    def create_ssl_context(self, purpose: str = "client") -> Optional[ssl.SSLContext]:
        """
        Create SSL context for mTLS communication
        
        Args:
            purpose: "client" for outgoing requests, "server" for incoming requests
        
        Returns:
            SSL context configured for mTLS, or None if mTLS is disabled
        """
        if not self.enabled:
            return None
        
        if not self.validate():
            logger.error("Cannot create SSL context: invalid mTLS configuration")
            return None
        
        try:
            # Create SSL context based on purpose
            if purpose == "client":
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            else:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            
            # Set minimum TLS version
            if self.min_tls_version == "TLSv1_3":
                context.minimum_version = ssl.TLSVersion.TLSv1_3
            else:
                context.minimum_version = ssl.TLSVersion.TLSv1_2
            
            # Load CA certificate for verification
            context.load_verify_locations(self.ca_cert_path)
            
            # Load this instance's certificate and key
            context.load_cert_chain(self.cert_path, self.key_path)
            
            # Configure verification mode
            if self.verify_peer:
                context.verify_mode = ssl.CERT_REQUIRED
            else:
                context.verify_mode = ssl.CERT_OPTIONAL
                logger.warning("mTLS peer verification disabled - use only for testing")
            
            logger.info(f"SSL context created for {purpose}", extra={
                "min_tls_version": self.min_tls_version,
                "verify_peer": self.verify_peer
            })
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to create SSL context: {e}")
            return None
    
    def get_httpx_verify(self) -> bool | str:
        """
        Get httpx verify parameter for outgoing requests
        
        Returns:
            Path to CA cert if mTLS enabled, True for system CA, False if verify disabled
        """
        if not self.enabled:
            return True  # Use system CA certificates
        
        if not self.verify_peer:
            return False  # No verification (testing only)
        
        return self.ca_cert_path  # Use custom CA
    
    def get_httpx_cert(self) -> Optional[tuple[str, str]]:
        """
        Get httpx cert parameter for outgoing requests (client certificate)
        
        Returns:
            Tuple of (cert_path, key_path) if mTLS enabled, None otherwise
        """
        if not self.enabled:
            return None
        
        return (self.cert_path, self.key_path)


# Singleton instance
_mtls_config: Optional[MTLSConfig] = None


def get_mtls_config() -> MTLSConfig:
    """Get mTLS configuration singleton"""
    global _mtls_config
    if _mtls_config is None:
        _mtls_config = MTLSConfig.from_env()
    return _mtls_config


def create_sample_certs_script() -> str:
    """
    Generate a script for creating sample self-signed certificates for testing.
    
    This script should be used for development/testing only.
    Production deployments should use proper PKI/CA infrastructure.
    """
    return '''#!/bin/bash
# VCC-URN mTLS Certificate Generation Script
# ⚠️ FOR TESTING ONLY - Use proper PKI for production!

set -e

CERT_DIR="${CERT_DIR:-./certs}"
CA_DAYS=3650
CERT_DAYS=365
KEY_SIZE=4096

mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

echo "=== Generating CA certificate ==="
openssl genrsa -out ca.key $KEY_SIZE
openssl req -new -x509 -days $CA_DAYS -key ca.key -out ca.crt \\
    -subj "/C=DE/ST=NRW/L=Duesseldorf/O=VCC/OU=URN-Federation/CN=VCC-URN-CA"

echo "=== Generating instance certificate ==="
openssl genrsa -out instance.key $KEY_SIZE
openssl req -new -key instance.key -out instance.csr \\
    -subj "/C=DE/ST=NRW/L=Duesseldorf/O=VCC/OU=URN-Instance/CN=$(hostname)"

# Sign with CA
openssl x509 -req -days $CERT_DAYS -in instance.csr \\
    -CA ca.crt -CAkey ca.key -CAcreateserial -out instance.crt

# Clean up CSR
rm -f instance.csr

echo "=== Certificates generated in $CERT_DIR ==="
echo "CA Certificate: $CERT_DIR/ca.crt"
echo "Instance Cert:  $CERT_DIR/instance.crt"
echo "Instance Key:   $CERT_DIR/instance.key"
echo ""
echo "Set these environment variables:"
echo "  URN_MTLS_ENABLED=true"
echo "  URN_MTLS_CA_CERT=$CERT_DIR/ca.crt"
echo "  URN_MTLS_CERT=$CERT_DIR/instance.crt"
echo "  URN_MTLS_KEY=$CERT_DIR/instance.key"
'''
