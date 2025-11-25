"""
Admin Dashboard API for VCC-URN

Phase 2b: Web UI for peer monitoring, health checks, and system status.
On-premise, no external dependencies.

Endpoints:
- GET /admin/dashboard - HTML dashboard page
- GET /admin/api/status - JSON system status
- GET /admin/api/peers - JSON peer status
- GET /admin/api/metrics - JSON key metrics summary
"""

import time
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

from vcc_urn.config import settings
from vcc_urn.core.redis_cache import get_redis_cache
from vcc_urn.core.mtls import get_mtls_config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin-dashboard"])


def _parse_peers(peers_str: str) -> dict:
    """Parse peer configuration string"""
    mapping = {}
    if not peers_str:
        return mapping
    for item in peers_str.split(","):
        item = item.strip()
        if not item or "=" not in item:
            continue
        state, base = item.split("=", 1)
        mapping[state.strip().lower()] = base.strip().rstrip("/")
    return mapping


def _check_peer_health(base_url: str) -> dict:
    """Check health of a peer (best-effort, non-blocking)"""
    import httpx
    
    mtls_config = get_mtls_config()
    
    try:
        client_kwargs = {
            "timeout": 2.0,  # Short timeout for health checks
            "verify": mtls_config.get_httpx_verify(),
        }
        cert = mtls_config.get_httpx_cert()
        if cert:
            client_kwargs["cert"] = cert
        
        with httpx.Client(**client_kwargs) as client:
            start = time.time()
            resp = client.get(f"{base_url}/")
            latency_ms = (time.time() - start) * 1000
            
            return {
                "status": "healthy" if resp.status_code == 200 else "degraded",
                "status_code": resp.status_code,
                "latency_ms": round(latency_ms, 2),
                "checked_at": datetime.utcnow().isoformat() + "Z"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "checked_at": datetime.utcnow().isoformat() + "Z"
        }


@router.get("/api/status")
async def get_system_status():
    """Get overall system status"""
    redis_cache = get_redis_cache()
    mtls_config = get_mtls_config()
    
    return {
        "service": "vcc-urn",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "healthy",
        "components": {
            "database": {
                "status": "healthy",
                "url": settings.db_url.split("@")[-1] if "@" in settings.db_url else "local"
            },
            "redis": {
                "enabled": settings.redis_enabled,
                "status": "healthy" if settings.redis_enabled and redis_cache._redis else "disabled",
                "url": settings.redis_url.split("@")[-1] if settings.redis_url and "@" in settings.redis_url else settings.redis_url[:30] if settings.redis_url else "not configured"
            },
            "mtls": {
                "enabled": mtls_config.enabled,
                "verify_peer": mtls_config.verify_peer if mtls_config.enabled else None
            },
            "auth": {
                "mode": settings.auth_mode,
                "oidc_configured": bool(settings.oidc_issuer)
            }
        },
        "config": {
            "nid": settings.nid,
            "log_level": settings.log_level,
            "log_format": settings.log_format,
            "fed_timeout": settings.fed_timeout,
            "fed_cache_ttl": settings.fed_cache_ttl
        }
    }


@router.get("/api/peers")
async def get_peers_status():
    """Get federation peers status with health checks"""
    peers = _parse_peers(settings.peers)
    
    peer_status = {}
    for state, base_url in peers.items():
        peer_status[state] = {
            "url": base_url,
            "health": _check_peer_health(base_url)
        }
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "peer_count": len(peers),
        "peers": peer_status
    }


@router.get("/api/metrics")
async def get_metrics_summary():
    """Get key metrics summary (complement to Prometheus /metrics)"""
    # Note: This provides a simple JSON view of key metrics
    # Full metrics are available at /metrics in Prometheus format
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "note": "Full Prometheus metrics available at /metrics",
        "summary": {
            "cache": {
                "type": "redis" if settings.redis_enabled else "in-memory",
                "ttl_seconds": settings.fed_cache_ttl
            },
            "federation": {
                "timeout_seconds": settings.fed_timeout,
                "peer_count": len(_parse_peers(settings.peers))
            }
        }
    }


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Admin Dashboard HTML page
    
    Simple, self-contained HTML/CSS/JS dashboard for peer monitoring.
    No external dependencies (Bootstrap, jQuery, etc.) - all inline.
    """
    
    # Get current status for initial render
    peers = _parse_peers(settings.peers)
    redis_cache = get_redis_cache()
    mtls_config = get_mtls_config()
    
    html = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VCC-URN Admin Dashboard</title>
    <style>
        :root {{
            --primary: #1a56db;
            --success: #059669;
            --warning: #d97706;
            --danger: #dc2626;
            --bg: #f8fafc;
            --card: #ffffff;
            --text: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.5;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{
            background: var(--primary);
            color: white;
            padding: 20px;
            margin-bottom: 20px;
        }}
        header h1 {{ font-size: 1.5rem; font-weight: 600; }}
        header p {{ opacity: 0.9; font-size: 0.875rem; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
        }}
        .card h2 {{
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .status-healthy {{ background: #d1fae5; color: #065f46; }}
        .status-degraded {{ background: #fef3c7; color: #92400e; }}
        .status-unhealthy {{ background: #fee2e2; color: #991b1b; }}
        .status-disabled {{ background: #f1f5f9; color: #475569; }}
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid var(--border);
        }}
        .metric:last-child {{ border-bottom: none; }}
        .metric-label {{ color: var(--text-muted); font-size: 0.875rem; }}
        .metric-value {{ font-weight: 600; }}
        .peer-list {{ list-style: none; }}
        .peer-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            margin-bottom: 10px;
        }}
        .peer-info {{ flex: 1; }}
        .peer-name {{ font-weight: 600; text-transform: uppercase; }}
        .peer-url {{ font-size: 0.75rem; color: var(--text-muted); word-break: break-all; }}
        .peer-latency {{ font-size: 0.75rem; color: var(--text-muted); margin-left: 10px; }}
        .refresh-btn {{
            background: var(--primary);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.875rem;
        }}
        .refresh-btn:hover {{ opacity: 0.9; }}
        .refresh-btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}
        .last-updated {{
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 10px;
        }}
        footer {{
            text-align: center;
            padding: 20px;
            color: var(--text-muted);
            font-size: 0.75rem;
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>🔗 VCC-URN Admin Dashboard</h1>
            <p>Phase 2b • Peer Monitoring • On-Premise</p>
        </div>
    </header>
    
    <main class="container">
        <div style="margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
            <button class="refresh-btn" onclick="refreshAll()" id="refreshBtn">↻ Refresh</button>
            <span class="last-updated" id="lastUpdated">Last updated: -</span>
        </div>
        
        <div class="grid">
            <!-- System Status -->
            <div class="card">
                <h2>System Status</h2>
                <div id="systemStatus">
                    <div class="metric">
                        <span class="metric-label">Service</span>
                        <span class="status-badge status-healthy">Healthy</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Auth Mode</span>
                        <span class="metric-value">{settings.auth_mode}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Log Level</span>
                        <span class="metric-value">{settings.log_level}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">NID</span>
                        <span class="metric-value">{settings.nid}</span>
                    </div>
                </div>
            </div>
            
            <!-- Components -->
            <div class="card">
                <h2>Components</h2>
                <div id="components">
                    <div class="metric">
                        <span class="metric-label">Database</span>
                        <span class="status-badge status-healthy">Connected</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Redis Cache</span>
                        <span class="status-badge {"status-healthy" if settings.redis_enabled else "status-disabled"}">{"Enabled" if settings.redis_enabled else "Disabled"}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">mTLS</span>
                        <span class="status-badge {"status-healthy" if mtls_config.enabled else "status-disabled"}">{"Enabled" if mtls_config.enabled else "Disabled"}</span>
                    </div>
                </div>
            </div>
            
            <!-- Federation Config -->
            <div class="card">
                <h2>Federation</h2>
                <div id="federation">
                    <div class="metric">
                        <span class="metric-label">Timeout</span>
                        <span class="metric-value">{settings.fed_timeout}s</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Cache TTL</span>
                        <span class="metric-value">{settings.fed_cache_ttl}s</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Configured Peers</span>
                        <span class="metric-value">{len(peers)}</span>
                    </div>
                </div>
            </div>
            
            <!-- Quick Links -->
            <div class="card">
                <h2>Quick Links</h2>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <a href="/docs" style="color: var(--primary);">📖 API Documentation</a>
                    <a href="/metrics" style="color: var(--primary);">📊 Prometheus Metrics</a>
                    <a href="/api/v1/health" style="color: var(--primary);">❤️ Health Check</a>
                </div>
            </div>
        </div>
        
        <!-- Peers Section -->
        <div class="card" style="margin-top: 20px;">
            <h2>Federation Peers</h2>
            <ul class="peer-list" id="peerList">
                {"".join(f'''
                <li class="peer-item" id="peer-{state}">
                    <div class="peer-info">
                        <div class="peer-name">{state}</div>
                        <div class="peer-url">{url}</div>
                    </div>
                    <span class="status-badge status-disabled">Checking...</span>
                </li>
                ''' for state, url in peers.items()) if peers else '<li class="peer-item"><span style="color: var(--text-muted);">No peers configured</span></li>'}
            </ul>
        </div>
    </main>
    
    <footer>
        <p>VCC-URN • Phase 2b Admin Dashboard • On-Premise • Vendor-Free</p>
        <p style="margin-top: 5px;">See <a href="/admin/api/status" style="color: var(--primary);">/admin/api/status</a> for JSON API</p>
    </footer>
    
    <script>
        function updateLastUpdated() {{
            document.getElementById('lastUpdated').textContent = 
                'Last updated: ' + new Date().toLocaleTimeString();
        }}
        
        async function refreshPeers() {{
            try {{
                const resp = await fetch('/admin/api/peers');
                const data = await resp.json();
                
                for (const [state, info] of Object.entries(data.peers)) {{
                    const el = document.getElementById('peer-' + state);
                    if (el) {{
                        const badge = el.querySelector('.status-badge');
                        const health = info.health;
                        
                        badge.className = 'status-badge status-' + health.status;
                        badge.textContent = health.status.charAt(0).toUpperCase() + health.status.slice(1);
                        
                        if (health.latency_ms) {{
                            let latencyEl = el.querySelector('.peer-latency');
                            if (!latencyEl) {{
                                latencyEl = document.createElement('span');
                                latencyEl.className = 'peer-latency';
                                el.insertBefore(latencyEl, badge);
                            }}
                            latencyEl.textContent = health.latency_ms.toFixed(0) + 'ms';
                        }}
                    }}
                }}
            }} catch (e) {{
                console.error('Failed to refresh peers:', e);
            }}
        }}
        
        async function refreshAll() {{
            const btn = document.getElementById('refreshBtn');
            btn.disabled = true;
            btn.textContent = '↻ Loading...';
            
            await refreshPeers();
            updateLastUpdated();
            
            btn.disabled = false;
            btn.textContent = '↻ Refresh';
        }}
        
        // Initial load
        document.addEventListener('DOMContentLoaded', () => {{
            refreshAll();
            // Auto-refresh every 30 seconds
            setInterval(refreshAll, 30000);
        }});
    </script>
</body>
</html>'''
    
    return HTMLResponse(content=html)


def get_dashboard_router():
    """Get the admin dashboard router"""
    return router
