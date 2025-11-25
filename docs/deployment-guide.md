# VCC-URN Deployment Guide

**Phase 1: Production Hardening - Deployment**

Dieser Guide beschreibt verschiedene Deployment-Optionen für VCC-URN.

## Quick Start: Docker Compose (empfohlen für Entwicklung/Test)

### Voraussetzungen

- Docker 24+
- Docker Compose 2.0+

### Start

```bash
# 1. Repository klonen
git clone https://github.com/makr-code/VCC-URN.git
cd VCC-URN

# 2. .env-Datei erstellen (optional)
cp .env.example .env
# Bearbeite .env nach Bedarf

# 3. Services starten
docker-compose up -d

# 4. Status prüfen
docker-compose ps
docker-compose logs -f app

# 5. Testen
curl http://localhost:8000/
curl http://localhost:8000/healthz
curl http://localhost:8000/metrics
```

**Zugriff:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics
- PostgreSQL: localhost:5432

### Stop

```bash
docker-compose down
# Mit Daten-Cleanup:
docker-compose down -v
```

## Produktions-Deployment: Kubernetes

Siehe [deployment/k8s/README.md](./deployment/k8s/README.md) für detaillierte Kubernetes-Anleitung.

**Kurzfassung:**

```bash
# 1. Image bauen
docker build -t vcc-urn-resolver:v1.0.0 .

# 2. Secrets anpassen
vi deployment/k8s/secret.yaml

# 3. Deployen
kubectl apply -f deployment/k8s/

# 4. Status
kubectl get pods -l app=vcc-urn-resolver
kubectl logs -l app=vcc-urn-resolver --tail=100 -f
```

## Manuelles Deployment (ohne Container)

### Voraussetzungen

- Python 3.11+
- PostgreSQL 15+ (oder SQLite für Tests)
- pip

### Installation

```bash
# 1. Repository klonen
git clone https://github.com/makr-code/VCC-URN.git
cd VCC-URN

# 2. Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# 3. Dependencies installieren
pip install -r requirements.txt

# 4. Umgebungsvariablen setzen
cp .env.example .env
# Bearbeite .env

# 5. Datenbank initialisieren
alembic upgrade head

# 6. Server starten
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Monitoring & Observability

### Prometheus Metrics

Metriken sind unter `/metrics` verfügbar:

```bash
curl http://localhost:8000/metrics
```

**Wichtige Metriken:**

- `http_requests_total` - Anzahl HTTP-Requests
- `http_request_duration_seconds` - Request-Latenz
- `http_requests_inprogress` - Aktive Requests

**Prometheus-Konfiguration (prometheus.yml):**

```yaml
scrape_configs:
  - job_name: 'vcc-urn'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Structured Logging

**JSON-Logs aktivieren:**

```bash
export URN_LOG_FORMAT=json
export URN_LOG_LEVEL=INFO
```

**Beispiel JSON-Log:**

```json
{
  "timestamp": "2025-11-23T09:00:00.123Z",
  "logger": "vcc_urn.services.federation",
  "level": "INFO",
  "msg": "Federation resolved via peer",
  "urn": "urn:de:nrw:bimschg:anlage:4711:...",
  "state": "nrw",
  "peer_url": "https://nrw.example.com"
}
```

**Loki-Integration (docker-compose.yml erweitern):**

```yaml
services:
  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    volumes:
      - loki-data:/loki

  promtail:
    image: grafana/promtail:2.9.0
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml

volumes:
  loki-data:
```

### Grafana Dashboard

**Empfohlene Panels:**

1. **Request Rate** (Requests/Sekunde)
   - Metric: `rate(http_requests_total[5m])`

2. **Latency (P50, P95, P99)**
   - Metric: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`

3. **Error Rate**
   - Metric: `rate(http_requests_total{status=~"5.."}[5m])`

4. **Active Connections**
   - Metric: `http_requests_inprogress`

5. **Federation Cache Hit Rate**
   - Custom Metric (Phase 2)

## Health Checks

### Liveness Probe

```bash
curl http://localhost:8000/healthz
# Expected: {"status": "ok"}
```

### Readiness Probe

```bash
curl http://localhost:8000/readyz
# Expected: {"status": "ready"}
# Bei DB-Problem: 503 Service Unavailable
```

## Sicherheit

### TLS/HTTPS

**Option 1: Reverse Proxy (empfohlen)**

Nginx-Konfiguration:

```nginx
server {
    listen 443 ssl http2;
    server_name urn.example.com;

    ssl_certificate /etc/ssl/certs/urn.example.com.crt;
    ssl_certificate_key /etc/ssl/private/urn.example.com.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Option 2: Uvicorn mit SSL**

```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8443 \
  --ssl-keyfile=/path/to/key.pem \
  --ssl-certfile=/path/to/cert.pem
```

### Rate Limiting

Rate Limiting ist bereits in Phase 1 integriert (slowapi):

- Default: 100 Requests/Minute pro IP
- Anpassbar per Endpoint

**Custom Limit:**

```python
@app.get("/api/v1/generate")
@limiter.limit("10/minute")  # Nur 10 Requests/Minute
async def generate(request: Request, ...):
    ...
```

### Authentifizierung

**API-Key-Modus (einfach):**

```bash
export URN_AUTH_MODE=apikey
export URN_API_KEYS=prod-key-1:admin,prod-key-2:reader
```

Request mit API-Key:

```bash
curl -H "X-API-Key: prod-key-1" http://localhost:8000/api/v1/generate
```

**OIDC-Modus (enterprise):**

```bash
export URN_AUTH_MODE=oidc
export URN_OIDC_ISSUER=https://keycloak.example.com/realms/vcc
export URN_OIDC_AUDIENCE=api://urn-resolver
export URN_OIDC_JWKS_URL=https://keycloak.example.com/realms/vcc/protocol/openid-connect/certs
```

Request mit JWT:

```bash
curl -H "Authorization: Bearer <jwt-token>" http://localhost:8000/api/v1/generate
```

## Troubleshooting

### App startet nicht

**Problem:** `ModuleNotFoundError`

```bash
# Lösung: Dependencies neu installieren
pip install -r requirements.txt
```

**Problem:** `Database connection failed`

```bash
# Lösung: DB-URL prüfen
echo $URN_DB_URL
# Für SQLite: sicherstellen dass Verzeichnis schreibbar ist
# Für PostgreSQL: Verbindung testen
psql $URN_DB_URL -c "SELECT 1"
```

### Metrics nicht sichtbar

```bash
# Prüfe ob /metrics erreichbar ist
curl http://localhost:8000/metrics

# Prüfe Logs
docker-compose logs app | grep -i prometheus
```

### Hohe Latenz

**Diagnose:**

```bash
# Prüfe DB-Verbindung
curl http://localhost:8000/readyz

# Prüfe Logs für langsame Queries
docker-compose logs app | grep -i "slow"

# Prüfe Prometheus-Metriken
curl http://localhost:8000/metrics | grep http_request_duration
```

**Lösungen:**

- DB-Indizes prüfen (siehe `alembic/versions/`)
- Connection-Pool-Size erhöhen (SQLAlchemy Config)
- Föderation-Cache-TTL erhöhen (`URN_FED_CACHE_TTL`)

### Circuit Breaker ausgelöst

**Symptom:** Federation-Requests schlagen fehl mit "Circuit breaker is open"

**Diagnose:**

```bash
# Logs prüfen
docker-compose logs app | grep -i "circuit"
```

**Lösung:**

- Peer-Status prüfen (ist Peer erreichbar?)
- Circuit Breaker Reset abwarten (60 Sekunden)
- Peer-URL korrigieren (`URN_PEERS`)

## Performance Tuning

### Uvicorn Workers

Für Produktion: Mehrere Worker-Prozesse

```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker
```

Faustregel: `workers = (2 * CPU_cores) + 1`

### Database Connection Pool

SQLAlchemy Pool-Größe anpassen (in `vcc_urn/db/session.py`):

```python
engine = create_engine(
    settings.db_url,
    pool_size=20,        # Maximale Connections
    max_overflow=10,     # Zusätzliche bei Bedarf
    pool_pre_ping=True   # Connection-Check vor Nutzung
)
```

### Cache-Optimierung

Federation-Cache TTL erhöhen:

```bash
export URN_FED_CACHE_TTL=600  # 10 Minuten statt 5
```

## Backup & Recovery

### PostgreSQL Backup

**Automatisiert (cronjob):**

```bash
#!/bin/bash
# backup-urn-db.sh
BACKUP_DIR=/var/backups/vcc-urn
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $URN_DB_URL > $BACKUP_DIR/urn_$DATE.sql
# Alte Backups löschen (älter als 30 Tage)
find $BACKUP_DIR -name "urn_*.sql" -mtime +30 -delete
```

Cronjob:

```cron
0 2 * * * /usr/local/bin/backup-urn-db.sh
```

**Restore:**

```bash
psql $URN_DB_URL < /var/backups/vcc-urn/urn_20251123_020000.sql
```

### Disaster Recovery

1. **Backup:** Täglich automatisiert (siehe oben)
2. **Replikation:** PostgreSQL Streaming Replication (optional)
3. **Monitoring:** Alerts für DB-Ausfälle
4. **Failover:** Kubernetes HPA für automatisches Failover

## Checkliste: Produktions-Deployment

- [ ] **Secrets:** Alle Secrets in `secret.yaml` geändert (nicht Beispielwerte)
- [ ] **TLS:** HTTPS konfiguriert (Nginx/Ingress)
- [ ] **Authentifizierung:** `URN_AUTH_MODE` auf `apikey` oder `oidc` gesetzt
- [ ] **Logging:** JSON-Format aktiviert (`URN_LOG_FORMAT=json`)
- [ ] **Monitoring:** Prometheus + Grafana eingerichtet
- [ ] **Alerting:** Kritische Alerts konfiguriert (DB down, hohe Latenz)
- [ ] **Backups:** Automatische DB-Backups aktiviert
- [ ] **Health Checks:** Liveness/Readiness Probes getestet
- [ ] **Resource Limits:** CPU/Memory Limits gesetzt (K8s)
- [ ] **Auto-Scaling:** HPA konfiguriert (K8s)
- [ ] **Documentation:** Runbooks für Ops-Team erstellt

## Support

- **GitHub Issues:** https://github.com/makr-code/VCC-URN/issues
- **Dokumentation:** [docs/](../docs/)
- **API-Referenz:** http://localhost:8000/docs (Swagger UI)

---

**Erstellt:** 2025-11-23  
**Phase:** Phase 1 - Production Hardening  
**Version:** 1.0
