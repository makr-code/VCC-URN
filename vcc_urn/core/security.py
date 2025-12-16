from typing import List, Optional, Dict, Any
from fastapi import Header, HTTPException, status, Depends
from vcc_urn.config import settings
from jose import jwt
import httpx
import time
import secrets


def _parse_keys(keys: str) -> List[str]:
    return [k.strip() for k in keys.split(",") if k.strip()]


def _parse_keys_map(keys: str) -> Dict[str, List[str]]:
    """Parse API keys string into a mapping key -> list of roles.

    Supported formats:
      - "key1,key2" -> {"key1": [], "key2": []}
      - "key1:admin|user,key2:reader" -> {"key1": ["admin","user"], "key2": ["reader"]}
    """
    out: Dict[str, List[str]] = {}
    if not keys:
        return out
    for item in keys.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" in item:
            key, roles = item.split(":", 1)
            roles_list = [r.strip() for r in roles.split("|") if r.strip()]
        else:
            key = item
            roles_list = []
        out[key.strip()] = roles_list
    return out


def _constant_time_compare(a: str, b: str) -> bool:
    """
    Constant-time string comparison to prevent timing attacks.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        True if strings are equal, False otherwise
    """
    return secrets.compare_digest(a.encode('utf-8'), b.encode('utf-8'))


_jwks_cache: Dict[str, Any] = {"expires": 0.0, "keys": None}


def _get_jwks() -> Dict[str, Any]:
    now = time.time()
    if _jwks_cache["keys"] is not None and _jwks_cache["expires"] > now:
        return _jwks_cache["keys"]
    if not settings.oidc_jwks_url:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="auth misconfigured: OIDC jwks url missing")
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(settings.oidc_jwks_url)
            resp.raise_for_status()
            data = resp.json()
            _jwks_cache["keys"] = data
            _jwks_cache["expires"] = now + max(60, settings.oidc_jwks_ttl)
            return data
    except Exception:
        # Hide upstream errors behind 401 to avoid leaking infra details
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unable to fetch JWKS")


def _find_key_for_kid(jwks: Dict[str, Any], kid: str) -> Optional[Dict[str, Any]]:
    for k in jwks.get("keys", []):
        if k.get("kid") == kid:
            return k
    return None


def extract_roles_from_claims(claims: Dict[str, Any]) -> List[str]:
    """Extract role-like values from common JWT claim locations.

    Heuristics look for (in order):
      - 'roles' claim (list or comma/space separated string)
      - 'groups' claim
      - 'scope' claim (space-separated)
      - 'realm_access.roles' (Keycloak)
    Returns a list of role strings (may be empty).
    """
    roles: List[str] = []
    if not claims:
        return roles
    # 1) explicit 'roles' claim (list or space/comma separated string)
    raw_roles = claims.get("roles")
    if raw_roles:
        if isinstance(raw_roles, list):
            return [str(r) for r in raw_roles]
        else:
            return [r.strip() for r in str(raw_roles).replace(",", " ").split() if r.strip()]
    # 2) 'groups' claim
    gr = claims.get("groups")
    if gr:
        if isinstance(gr, list):
            return [str(r) for r in gr]
        else:
            return [r.strip() for r in str(gr).replace(",", " ").split() if r.strip()]
    # 3) 'scope' claim
    sc = claims.get("scope")
    if sc:
        return [r.strip() for r in str(sc).split() if r.strip()]
    # 4) Keycloak-style realm_access.roles
    ra = claims.get("realm_access")
    if isinstance(ra, dict):
        rr = ra.get("roles")
        if isinstance(rr, list):
            return [str(r) for r in rr]
    return roles


async def require_auth(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> dict:
    """Minimal auth dependency.
    Modes:
      - none: allow all
      - apikey: require X-API-Key header to match configured keys
      - oidc: JWT Validation via JWKS
    Returns a principal dict (subject and mode).
    """
    mode = settings.auth_mode.lower().strip()
    if mode == "none":
        return {"sub": "anonymous", "mode": mode}
    if mode == "apikey":
        allowed_map = _parse_keys_map(settings.api_keys)
        allowed = list(allowed_map.keys())
        if not allowed:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="auth misconfigured: no API keys configured")
        if x_api_key is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or missing API key")
        
        # Use constant-time comparison to prevent timing attacks
        valid_key = None
        for key in allowed:
            if _constant_time_compare(x_api_key, key):
                valid_key = key
                break
        
        if valid_key is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or missing API key")
        
        roles = allowed_map.get(valid_key, []) or ["api-key"]
        return {"sub": f"api-key:{valid_key}", "mode": mode, "roles": roles}
    if mode == "oidc":
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")
        token = authorization.split(" ", 1)[1].strip()
        if not settings.oidc_issuer or not settings.oidc_audience:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="auth misconfigured: issuer or audience missing")
        try:
            headers = jwt.get_unverified_header(token)
            kid = headers.get("kid")
            jwks = _get_jwks()
            key = None
            if kid:
                k = _find_key_for_kid(jwks, kid)
                if k:
                    key = jwt.algorithms.RSAAlgorithm.from_jwk(k)
            if key is None:
                for k in jwks.get("keys", []):
                    if k.get("kty") == "RSA":
                        key = jwt.algorithms.RSAAlgorithm.from_jwk(k)
                        break
            if key is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no suitable JWKS key")
            claims = jwt.decode(
                token,
                key,
                algorithms=[headers.get("alg", "RS256")],
                audience=settings.oidc_audience,
                issuer=settings.oidc_issuer,
                options={"verify_at_hash": False},
            )
            sub = claims.get("sub", "")
            roles = extract_roles_from_claims(claims)
            return {"sub": sub or "unknown", "mode": mode, "claims": claims, "roles": roles}
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"unknown auth mode: {settings.auth_mode}")


def require_role(role: str):
    """Dependency factory that enforces a principal has given role."""
    async def _checker(principal = Depends(require_auth)):
        if not isinstance(principal, dict):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthenticated")
        if settings.auth_mode.lower().strip() == "none":
            return principal
        if principal.get("mode") == "none":
            return principal
        roles = principal.get("roles") or []
        if isinstance(roles, str):
            roles = [roles]
        if role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient role")
        return principal

    return _checker
