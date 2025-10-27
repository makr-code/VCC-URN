# VCC-URN Resolver – Vollständige Dokumentation

## Inhaltsverzeichnis

1. [Überblick](#überblick)
2. [Architektur](#architektur)
3. [Installation & Setup](#installation--setup)
4. [Konfiguration](#konfiguration)
5. [API-Referenz](#api-referenz)
6. [Authentifizierung & Autorisierung](#authentifizierung--autorisierung)
7. [Föderation](#föderation)
8. [Katalog-Management](#katalog-management)
9. [Datenbank & Migrationen](#datenbank--migrationen)
10. [Entwicklung](#entwicklung)
11. [Betrieb & Deployment](#betrieb--deployment)
12. [Troubleshooting](#troubleshooting)

---

## Überblick

**VCC-URN Resolver** ist ein FastAPI-basierter Microservice zur Generierung, Validierung, Speicherung und Auflösung föderaler URNs (Uniform Resource Names) für die deutsche Verwaltungsdigitalisierung.

### Kernfunktionen

- **URN-Generierung**: Erstelle eindeutige URNs nach RFC 8141 mit konfigurierbaren Katalogen
- **Validierung**: Prüfe URN-Syntax und Katalog-Konformität
- **Auflösung (Resolve)**: Erhalte zugehörige Manifeste (lokal oder via Föderation)
- **Suche**: Finde URNs per UUID mit Pagination
- **Föderations-Support**: Verteilte Resolver mit Peer-Integration und Caching
- **Katalog-Management**: Laufzeit-Verwaltung von Domänen und Objekttypen (global/landesspezifisch)
- **Authentifizierung**: API-Key oder OIDC/JWT mit rollenbasierter Autorisierung
- **Admin-API**: Verwaltungsendpunkte für Kataloge und Systemstatus

### Technologie-Stack

- **FastAPI 0.120+** (Pydantic v2)
- **SQLAlchemy 1.4** (ORM)
- **Alembic** (Migrationen)
- **PostgreSQL** oder **SQLite** (DB)
- **httpx** (Föderation, OIDC JWKS)
- **python-jose** (JWT-Validierung)

---

## Architektur

### Projektstruktur (Clean Architecture)

```
VCC-URN/
├── app/
│   └── main.py                   # FastAPI Entrypoint, Lifespan, Router-Registrierung
├── vcc_urn/
│   ├── api/                      # API-Routers (modular)
│   │   ├── v1/
│   │   │   └── endpoints.py      # v1-Endpunkte (generate, validate, resolve, search)
│   │   └── admin/
│   │       └── endpoints.py      # Admin-Endpunkte (catalogs)
│   ├── core/                     # Kern-Module
│   │   ├── config.py             # Settings (ENV)
│   │   ├── security.py           # Auth (API-Key, OIDC, require_role)
│   │   └── runtime.py            # Katalog-Reload/Management
│   ├── db/                       # Datenbank
│   │   └── session.py            # Engine, SessionLocal, Base, init_db()
│   ├── models/                   # ORM-Modelle
│   │   └── manifest.py           # Manifest-Tabelle
│   ├── repository/               # Data-Access
│   │   └── manifest_repository.py# ManifestRepository (CRUD)
│   ├── services/                 # Business-Logik
│   │   ├── urn.py                # URN-Klasse (Parse/Generate)
│   │   ├── federation.py         # Föderations-Resolver + TTL-Cache
│   │   └── urn_service.py        # URNService (High-Level API)
│   └── schemas.py                # Pydantic Request/Response-Schemas
├── alembic/                      # DB-Migrationen
├── tests/                        # Pytest-Tests
├── docs/                         # Dokumentation (Markdown)
├── requirements.txt              # Python-Dependencies
├── pyproject.toml                # Poetry-Konfiguration, Tooling
└── .env.example                  # ENV-Template
```

### Schichten-Modell

```
┌────────────────────────────────────────┐
│  FastAPI App (app/main.py)            │ ← Entrypoint, CORS, Lifespan
├────────────────────────────────────────┤
│  API Router (vcc_urn/api/*)           │ ← v1, admin
├────────────────────────────────────────┤
│  Services (vcc_urn/services/*)        │ ← URNService, URN, Federation
├────────────────────────────────────────┤
│  Repository (vcc_urn/repository/*)    │ ← ManifestRepository
├────────────────────────────────────────┤
│  ORM Models (vcc_urn/models/*)        │ ← Manifest
├────────────────────────────────────────┤
│  DB (vcc_urn/db/session.py)           │ ← SQLAlchemy Engine/Session
└────────────────────────────────────────┘
```

**Kompatibilitäts-Shims**: Top-Level-Module (`vcc_urn/config.py`, `vcc_urn/urn.py`, etc.) re-exportieren aus Subpaketen, sodass bestehende Importe (`from vcc_urn.urn import URN`) weiterhin funktionieren.

---

## Installation & Setup

### Voraussetzungen

- **Python 3.10+** (empfohlen: 3.11 oder 3.13)
- **pip** oder **poetry**
- Optional: **PostgreSQL** (für Produktion)

### Installation

#### Mit pip

```bash
# Clone Repository
git clone https://github.com/makr-code/VCC-URN.git
cd VCC-URN

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt
```

#### Mit Poetry

```bash
# Clone Repository
git clone https://github.com/makr-code/VCC-URN.git
cd VCC-URN

# Dependencies installieren
poetry install

# Shell aktivieren
poetry shell
```

### Schnellstart (Entwicklung)

```bash
# .env erstellen (optional)
cp .env.example .env

# DB initialisieren (SQLite Default)
# (wird automatisch beim ersten Start erstellt)

# Server starten
poetry run start
# oder
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Zugriff**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

---

## Konfiguration

Alle Konfigurationen erfolgen über **Umgebungsvariablen** (`.env` oder System-ENV).

### Datenbank

| Variable | Default | Beschreibung |
|----------|---------|--------------|
| `URN_DB_URL` | `sqlite:///./urn_manifest.db` | SQLAlchemy DB-URL |

**Beispiele**:
- SQLite: `sqlite:///./urn_manifest.db`
- PostgreSQL: `postgresql+psycopg://user:pass@localhost:5432/urn`

### URN-Schema

| Variable | Default | Beschreibung |
|----------|---------|--------------|
| `URN_NID` | `de` | Namespace Identifier (NID) |
| `URN_STATE_RE` | `^[a-z]{2,3}$` | Regex für State-Code-Validierung |

### CORS

| Variable | Default | Beschreibung |
|----------|---------|--------------|
| `URN_CORS_ORIGINS` | `*` | Komma-separierte Origins (z. B. `http://localhost:3000,https://app.example`) |

### Föderation

| Variable | Default | Beschreibung |
|----------|---------|--------------|
| `URN_PEERS` | `""` | Peer-Resolver als `state=url` (z. B. `nrw=https://nrw.resolver,by=https://by.resolver`) |
| `URN_FED_TIMEOUT` | `3.0` | HTTP-Timeout für Peer-Anfragen (Sekunden) |
| `URN_FED_CACHE_TTL` | `300` | TTL für Peer-Cache (Sekunden) |

### Authentifizierung

| Variable | Default | Beschreibung |
|----------|---------|--------------|
| `URN_AUTH_MODE` | `none` | `none` \| `apikey` \| `oidc` |
| `URN_API_KEYS` | `""` | Komma-separiert; optional mit Rollen: `key:role1\|role2` |
| `URN_OIDC_ISSUER` | `""` | OIDC Issuer-URL |
| `URN_OIDC_AUDIENCE` | `""` | OIDC Audience (z. B. `api://urn-resolver`) |
| `URN_OIDC_JWKS_URL` | `""` | JWKS-Endpoint-URL |
| `URN_OIDC_JWKS_TTL` | `3600` | JWKS-Cache-TTL (Sekunden) |

### Kataloge

| Variable | Default | Beschreibung |
|----------|---------|--------------|
| `URN_ALLOWED_DOMAINS` | `""` | Globale Domänen (lowercase, komma-separiert) |
| `URN_ALLOWED_OBJ_TYPES` | `""` | Globale Objekttypen (lowercase, komma-separiert) |
| `URN_CATALOGS_JSON` | `""` | JSON für State-spezifische Kataloge (Vorrang vor Globals) |

**Beispiel `URN_CATALOGS_JSON`**:
```json
{
  "nrw": {
    "domains": ["bimschg", "bau"],
    "obj_types": ["anlage", "bescheid"]
  },
  "by": {
    "domains": ["bau"],
    "obj_types": ["gutachten"]
  }
}
```

---

## API-Referenz

**Basis-URL**: `/api/v1`

### URN-Endpunkte

#### `POST /api/v1/generate`

Generiere eine neue URN (optional mit Speicherung).

**Request Body** (`GenerateRequest`):
```json
{
  "state": "nrw",
  "domain": "bimschg",
  "obj_type": "anlage",
  "local_aktenzeichen": "4711-0815-K1",
  "uuid": "optional-uuid",
  "version": "optional-v1.0",
  "store": true
}
```

**Response** (`GenerateResponse`):
```json
{
  "urn": "urn:de:nrw:bimschg:anlage:4711-0815-K1:a1b2c3d4-..."
}
```

**Auth**: `require_auth()` (je nach `URN_AUTH_MODE`)

---

#### `POST /api/v1/validate`

Validiere URN-Syntax und Katalog-Konformität.

**Request Body** (`ValidateRequest`):
```json
{
  "urn": "urn:de:nrw:bimschg:anlage:4711-0815-K1:a1b2c3d4-..."
}
```

**Response** (`ValidateResponse`):
```json
{
  "valid": true,
  "reason": null,
  "components": {
    "nid": "de",
    "state": "nrw",
    "domain": "bimschg",
    "obj_type": "anlage",
    "local_aktenzeichen": "4711-0815-K1",
    "uuid": "a1b2c3d4-...",
    "version": null
  }
}
```

**Auth**: Keine

---

#### `POST /api/v1/store`

Speichere oder aktualisiere ein Manifest für eine URN.

**Request Body** (`StoreRequest`):
```json
{
  "urn": "urn:de:nrw:bimschg:anlage:4711-0815-K1:a1b2c3d4-...",
  "manifest": {
    "@id": "urn:de:nrw:...",
    "label": "Anlage 4711",
    "custom_field": "value"
  }
}
```

**Response**:
```json
{
  "status": "ok",
  "urn": "urn:de:nrw:..."
}
```

**Auth**: `require_auth()`

---

#### `GET /api/v1/resolve?urn={urn}`

Löse eine URN zu einem Manifest auf (lokal oder via Föderation).

**Query Parameters**:
- `urn` (required): URN-String

**Response**:
```json
{
  "@id": "urn:de:nrw:...",
  "urn": "urn:de:nrw:...",
  "type": "anlage",
  "domain": "bimschg",
  "country": "nrw",
  "local_aktenzeichen": "4711-0815-K1",
  "uuid": "a1b2c3d4-...",
  "label": "Anlage 4711 (NRW)"
}
```

**Auth**: Keine

**Hinweis**: Falls nicht lokal vorhanden, wird via `URN_PEERS` ein Peer-Resolver angefragt und das Ergebnis lokal gecacht.

---

#### `GET /api/v1/search?uuid={uuid}&limit={limit}&offset={offset}`

Suche URNs nach UUID.

**Query Parameters**:
- `uuid` (required): UUID-String
- `limit` (optional, default: 50, max: 500)
- `offset` (optional, default: 0)

**Response** (`SearchResponse`):
```json
{
  "count": 2,
  "results": [
    {
      "urn": "urn:de:nrw:...:v1",
      "manifest": { ... }
    },
    {
      "urn": "urn:de:nrw:...:v2",
      "manifest": { ... }
    }
  ]
}
```

**Auth**: Keine

---

### Admin-Endpunkte

**Basis**: `/admin`  
**Auth**: `require_role("admin")` (außer `URN_AUTH_MODE=none`)

#### `GET /admin/catalogs`

Zeige effektive Kataloge (global + state-spezifisch).

**Response** (`AdminCatalogsResponse`):
```json
{
  "global_domains": ["bimschg", "bau"],
  "global_obj_types": ["anlage", "bescheid"],
  "state_catalogs": {
    "nrw": {
      "domains": ["bimschg"],
      "obj_types": ["anlage"]
    }
  }
}
```

---

#### `POST /admin/catalogs/reload`

Lade Konfiguration neu (ENV-Refresh).

**Response**: wie `GET /admin/catalogs`

---

#### `POST /admin/catalogs/set`

Setze State-Kataloge zur Laufzeit (ephemeral).

**Request Body** (`AdminCatalogsSetRequest`):
```json
{
  "catalogs": {
    "nrw": {
      "domains": ["bimschg", "bau"],
      "obj_types": ["anlage", "bescheid", "gutachten"]
    }
  }
}
```

**Response**: wie `GET /admin/catalogs`

**Hinweis**: Änderungen gelten nur für den aktuellen Prozess; bei Restart gehen sie verloren (ENV ist maßgeblich).

---

### System-Endpunkte

#### `GET /`

Info-Endpoint.

**Response**:
```json
{
  "service": "VCC URN resolver",
  "nid": "de"
}
```

---

#### `GET /healthz`

Lightweight Health-Check (immer 200 OK).

**Response**:
```json
{
  "status": "ok"
}
```

---

#### `GET /readyz`

Readiness-Check (DB-Connectivity).

**Response**:
```json
{
  "status": "ready"
}
```

**Status**: 200 wenn DB verfügbar, 503 sonst.

---

## Authentifizierung & Autorisierung

### Modi

#### `none` (Default)

- Keine Authentifizierung
- Für lokale Entwicklung

#### `apikey`

- Header: `X-API-Key: <key>`
- Keys via `URN_API_KEYS`
- Optional mit Rollen: `admin-key:admin|editor`

**Beispiel ENV**:
```bash
URN_AUTH_MODE=apikey
URN_API_KEYS=dev-key:admin,read-key:reader
```

**Request**:
```bash
curl -H "X-API-Key: dev-key" http://localhost:8000/api/v1/generate ...
```

#### `oidc`

- Header: `Authorization: Bearer <JWT>`
- JWT-Validierung via JWKS (RS256)
- Rollen extrahiert aus Claims (`roles`, `groups`, `scope`, `realm_access.roles`)

**Beispiel ENV**:
```bash
URN_AUTH_MODE=oidc
URN_OIDC_ISSUER=https://keycloak.example/realms/vcc
URN_OIDC_AUDIENCE=api://urn-resolver
URN_OIDC_JWKS_URL=https://keycloak.example/realms/vcc/protocol/openid-connect/certs
```

**Request**:
```bash
curl -H "Authorization: Bearer eyJhbGciOi..." http://localhost:8000/api/v1/generate ...
```

### Rollenbasierte Zugriffskontrolle

**Dependency**: `require_role("admin")`

**Beispiel** (Admin-Router):
```python
from vcc_urn.security import require_role

router = APIRouter(dependencies=[Depends(require_role("admin"))])
```

**Verhalten**:
- `URN_AUTH_MODE=none`: Zugriff erlaubt (Dev-Mode)
- `apikey` oder `oidc`: Prüft, ob Rolle im Principal vorhanden ist (sonst 403)

---

## Föderation

### Konzept

URN-Resolver können dezentral betrieben werden (z. B. je Bundesland). Bei Auflösung einer URN prüft der Resolver:
1. Lokale DB
2. Falls nicht gefunden → Peer-Resolver (State-spezifisch)
3. Caching des Peer-Ergebnisses

### Konfiguration

**ENV**:
```bash
URN_PEERS=nrw=https://nrw-resolver.example,by=https://by-resolver.example
URN_FED_TIMEOUT=3.0
URN_FED_CACHE_TTL=300
```

### Ablauf (Resolve-Endpoint)

1. Client: `GET /api/v1/resolve?urn=urn:de:nrw:...`
2. Resolver:
   - Lokale DB abfragen
   - Falls nicht vorhanden: `GET https://nrw-resolver.example/api/v1/resolve?urn=...`
   - Antwort cachen (300s TTL)
   - Rückgabe an Client
3. Bei erneutem Request innerhalb TTL: Cache-Hit

### Peer-API-Kompatibilität

Peers müssen `/api/v1/resolve?urn=...` implementieren und ein Manifest zurückgeben:
```json
{
  "urn": "urn:de:nrw:...",
  "@id": "urn:de:nrw:...",
  "type": "anlage",
  ...
}
```

---

## Katalog-Management

### Globale Kataloge

Definiere zulässige Domänen und Objekttypen für **alle** States:

```bash
URN_ALLOWED_DOMAINS=bimschg,bau,umwelt
URN_ALLOWED_OBJ_TYPES=anlage,bescheid,gutachten
```

**Wirkung**: URN-Generierung/Validierung lehnt andere Werte ab.

### State-spezifische Kataloge

Überschreibe für einzelne States:

```bash
URN_CATALOGS_JSON='{"nrw":{"domains":["bimschg"],"obj_types":["anlage"]}}'
```

**Vorrang**: State-Katalog > Global-Katalog

**Fallback**: States ohne Eintrag nutzen globale Kataloge.

### Laufzeit-Verwaltung (Admin-API)

```bash
# Aktuelle Kataloge abfragen
curl http://localhost:8000/admin/catalogs

# ENV neu laden
curl -X POST http://localhost:8000/admin/catalogs/reload

# Kataloge ephemeral setzen
curl -X POST http://localhost:8000/admin/catalogs/set \
  -H "Content-Type: application/json" \
  -d '{"catalogs":{"nrw":{"domains":["bimschg","bau"],"obj_types":["anlage"]}}}'
```

**Hinweis**: `/set` ist prozess-lokal; bei Restart gehen Änderungen verloren.

---

## Datenbank & Migrationen

### Unterstützte Datenbanken

- **SQLite** (Dev/Testing)
- **PostgreSQL** (Produktion)

### Schema

**Tabelle: `manifests`**

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| `urn` | VARCHAR(512) PK | URN-String |
| `nid` | VARCHAR(32) | Namespace ID (z. B. `de`) |
| `state` | VARCHAR(10) INDEX | State-Code |
| `domain` | VARCHAR(64) | Domäne |
| `obj_type` | VARCHAR(64) | Objekttyp |
| `local_aktenzeichen` | VARCHAR(512) | Aktenzeichen |
| `uuid` | VARCHAR(36) INDEX | UUID |
| `version` | VARCHAR(64) | Version (optional) |
| `manifest_json` | TEXT | JSON-Manifest |
| `created_at` | TIMESTAMPTZ | Erstellungszeitpunkt |
| `updated_at` | TIMESTAMPTZ | Update-Zeitpunkt |

### Migrationen (Alembic)

#### Initiale Migration

```bash
# Alembic-ENV prüfen (alembic/env.py sollte vcc_urn.db.Base kennen)

# Aktuelle Migration erstellen
alembic revision --autogenerate -m "initial schema"

# Migration anwenden
alembic upgrade head
```

#### Neue Migration (nach Schema-Änderung)

```bash
alembic revision --autogenerate -m "add column xyz"
alembic upgrade head
```

#### Rollback

```bash
alembic downgrade -1  # eine Revision zurück
```

### PostgreSQL Setup

**Docker Compose** (optional):
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: urn
      POSTGRES_USER: urn
      POSTGRES_PASSWORD: urn
    ports:
      - "5432:5432"
```

**ENV**:
```bash
URN_DB_URL=postgresql+psycopg://urn:urn@localhost:5432/urn
```

**Init**:
```bash
docker compose up -d postgres
alembic upgrade head
```

---

## Entwicklung

### Test-Suite

```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=vcc_urn --cov-report=html

# Spezifischer Test
pytest tests/test_urn.py::test_generate_and_parse_roundtrip -v
```

**Test-DB**: Automatisch SQLite in-memory oder `test_urn.db` (siehe `tests/conftest.py`).

### Code-Qualität

#### Linting (Ruff)

```bash
ruff check .
ruff check --fix .
```

#### Formatierung (Black)

```bash
black .
black --check .
```

#### Type-Checking (mypy)

```bash
mypy vcc_urn/
```

### CI/CD

**.github/workflows/ci.yml**:
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest -q
```

### Entwickler-Hinweise

- **Pydantic v2**: Nutze `json_schema_extra` statt `example` in `Field()`
- **FastAPI Lifespan**: `@app.on_event("startup")` ist deprecated; nutze `lifespan`-Context
- **httpx Deprecation**: In Tests `WSGITransport(app=...)` statt Shortcut `app=...`

---

## Betrieb & Deployment

### Docker

**Dockerfile** (Beispiel):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV URN_DB_URL=postgresql+psycopg://urn:urn@db:5432/urn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**:
```yaml
version: "3.9"
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      URN_DB_URL: postgresql+psycopg://urn:urn@db:5432/urn
      URN_AUTH_MODE: oidc
      URN_OIDC_ISSUER: https://keycloak.example/realms/vcc
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: urn
      POSTGRES_USER: urn
      POSTGRES_PASSWORD: urn
```

### Kubernetes

**ConfigMap** (ENV):
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: urn-config
data:
  URN_DB_URL: "postgresql+psycopg://urn:urn@postgres:5432/urn"
  URN_AUTH_MODE: "oidc"
  URN_OIDC_ISSUER: "https://keycloak.example/realms/vcc"
```

**Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: urn-resolver
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: urn
        image: ghcr.io/makr-code/vcc-urn:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: urn-config
```

### Monitoring

#### Health-Checks

```bash
# Kubernetes Liveness
livenessProbe:
  httpGet:
    path: /healthz
    port: 8000

# Readiness
readinessProbe:
  httpGet:
    path: /readyz
    port: 8000
```

#### Metrics (TODO)

Optional Prometheus-Integration via `prometheus-fastapi-instrumentator`:
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

→ Metriken unter `/metrics`

### Logging

**Structured Logging** (TODO):
```python
import logging
import json

logging.basicConfig(
    format='%(message)s',
    level=logging.INFO
)
logger = logging.getLogger("vcc_urn")

# JSON-Log
logger.info(json.dumps({"event": "urn_generated", "urn": "urn:de:..."}))
```

### Skalierung

- **Stateless**: Service kann horizontal skaliert werden (Shared DB)
- **Föderation-Cache**: In-Memory TTL-Cache ist prozess-lokal; für geteilten Cache Redis/Memcached nutzen (TODO)

---

## Troubleshooting

### Häufige Probleme

#### `ModuleNotFoundError: No module named 'vcc_urn'`

**Ursache**: Package nicht installiert oder PYTHONPATH fehlt.

**Lösung**:
```bash
pip install -e .
# oder
export PYTHONPATH=$(pwd)
```

#### `sqlalchemy.exc.OperationalError: no such table: manifests`

**Ursache**: DB-Schema nicht initialisiert.

**Lösung**:
```bash
alembic upgrade head
# oder für SQLite:
# Schema wird automatisch bei app-start via init_db() erstellt
```

#### `403 Forbidden` bei Admin-Endpoints

**Ursache**: Keine `admin`-Rolle oder `URN_AUTH_MODE=none` nicht gesetzt.

**Lösung**:
- Dev: `URN_AUTH_MODE=none`
- Prod: `URN_API_KEYS=admin-key:admin` oder OIDC-Token mit `admin`-Rolle

#### Peer-Federation schlägt fehl

**Debug**:
```bash
# Peer-URL testen
curl "https://nrw-resolver.example/api/v1/resolve?urn=urn:de:nrw:..."

# Timeout erhöhen
URN_FED_TIMEOUT=10.0
```

#### Katalog-Validierung schlägt fehl

**Symptom**: `ValueError: Domain 'xyz' not in allowed catalog`

**Lösung**:
```bash
# Kataloge prüfen
curl http://localhost:8000/admin/catalogs

# Ggf. Domäne hinzufügen
URN_ALLOWED_DOMAINS=bimschg,bau,xyz
```

---

## Anhang

### URN-Schema (RFC 8141)

**Format**:
```
urn:de:<state>:<domain>:<objtype>:<localAktenzeichen>:<uuid>[:<version>]
```

**Beispiel**:
```
urn:de:nrw:bimschg:anlage:4711-0815-K1:a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Komponenten**:
- `de`: NID (Namespace Identifier)
- `nrw`: State-Code (2-3 Zeichen, lowercase)
- `bimschg`: Domäne
- `anlage`: Objekttyp
- `4711-0815-K1`: Lokales Aktenzeichen (URL-encoded)
- `a1b2c3d4-...`: UUID (v4)
- optional: `:v1.0` Version

### Weitere Dokumentation

- [URN-Spezifikation](./urn-spec.md)
- [Einführung](./introducing.md)
- [GitHub Repository](https://github.com/makr-code/VCC-URN)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Pydantic v2 Migration](https://docs.pydantic.dev/latest/migration/)

---

**Version**: 0.1.0  
**Datum**: 27. Oktober 2025  
**Autor**: makr-code
