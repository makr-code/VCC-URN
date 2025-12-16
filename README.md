# VCC-URN

**Version 0.2.0** - Production-ready URN Resolver with comprehensive security features

Kleines FastAPI-Backend zur Generierung, Validierung und Auflösung föderaler URNs.

## ⚡ Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API documentation available at `http://localhost:8000/docs`

## 🔒 Security Features (v0.2.0)

This version includes comprehensive security hardening:

- ✅ **Input Validation**: Length limits, regex patterns, control character filtering
- ✅ **Security Headers**: CSP, X-Frame-Options, X-Content-Type-Options, HSTS
- ✅ **Authentication Security**: Constant-time API key comparison, OIDC support
- ✅ **Database Security**: Connection pooling, query timeouts, parameterized queries
- ✅ **Error Handling**: Information disclosure prevention, log sanitization
- ✅ **Dependency Security**: All known vulnerabilities patched
- ✅ **CodeQL Verified**: 0 security alerts

📖 **See [SECURITY.md](docs/SECURITY.md) for complete security documentation**

## 📚 Documentation

- **[SECURITY.md](docs/SECURITY.md)** - Security features, configuration, and deployment checklist
- **[BEST_PRACTICES.md](docs/BEST_PRACTICES.md)** - Development and deployment best practices
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[SECURITY_REVIEW_SUMMARY.md](docs/SECURITY_REVIEW_SUMMARY.md)** - Security audit findings

## Projektstruktur (Best Practice)

Der Code ist modular in Pakete gegliedert. Die API-Endpunkte sind aus dem Entrypoint herausgelöst und als Router organisiert:

- `app/main.py` – FastAPI-App, CORS, Startup (DB init), Router-Registrierung, Health-/Ready-Endpunkte
- `vcc_urn/api/v1/endpoints.py` – versionierte URN-API (generate/validate/store/resolve/search)
- `vcc_urn/api/admin/endpoints.py` – Admin-API für Katalog-Management (reload/get/set)
- `vcc_urn/service.py` – Service-Layer (Fachlogik URN, DB-Zugriff via Repository, Föderations-Fallback)
- `vcc_urn/repository.py` – Repository für Manifeste (SQLAlchemy-Queries, Upsert)
- `vcc_urn/models.py` – ORM-Modelle (SQLAlchemy)
- `vcc_urn/schemas.py` – Pydantic-Schemas (Request/Response)
- `vcc_urn/db.py` – Engine/Session/Base und `init_db()`
- `vcc_urn/config.py` – Settings (ENV)
- `vcc_urn/security.py` – Auth (none/apikey/oidc), Rollen, `require_role()`
- `vcc_urn/runtime.py` – Katalog-Verwaltung zur Laufzeit (reload/set, effective catalogs)

Weitere Aufteilung (z. B. `core/`, `db/`-Subpackage) ist vorbereitet und kann schrittweise erfolgen, ohne öffentliche Importe zu brechen.

## API

- Basis: `GET /` Info
- Health: `GET /healthz`, `GET /readyz`
- Versionierte API: Präfix `/api/v1`
	- `POST /api/v1/generate` → GenerateResponse
	- `POST /api/v1/validate` → ValidateResponse
	- `POST /api/v1/store` → Manifest speichern (Upsert)
	- `GET  /api/v1/resolve?urn=...` → Manifest oder minimaler Stub
	- `GET  /api/v1/search?uuid=...&limit=&offset=` → SearchResponse

OpenAPI ist unter `/docs` verfügbar (Swagger UI).

## Konfiguration

Umgebungsvariablen (optional):

- `URN_DB_URL` (Default: SQLite-Datei im aktuellen Arbeitsverzeichnis)
Beispiel für Postgres:

```
URN_DB_URL=postgresql+psycopg://urn:urn@localhost:5432/urn
```
- `URN_NID` (Default: `de`)
- `URN_STATE_RE` (Default: `^[a-z]{2,3}$`)
- `URN_CORS_ORIGINS` (Default: `*` für Entwicklung; Komma-separiert für mehrere Origins)
- Föderation:
	- `URN_PEERS` (z. B. `nrw=https://nrw.example,by=https://by.example`) – Basis-URL je Land; der Resolver wird unter `/api/v1/resolve` erwartet.
	- `URN_FED_TIMEOUT` (Default: `3.0` Sekunden) – Timeout für Peer-Anfragen.
	- `URN_FED_CACHE_TTL` (Default: `300` Sekunden) – In-Memory TTL Cache für Peer-Results.
 - Authentifizierung:
	 - `URN_AUTH_MODE` (Default: `none`) – `none` | `apikey` | `oidc`
	 - `URN_API_KEYS` – Komma-separierte API Keys; werden gegen Header `X-API-Key` geprüft, wenn `auth_mode=apikey`.
		- `URN_API_KEYS` – Komma-separierte API Keys; werden gegen Header `X-API-Key` geprüft, wenn `auth_mode=apikey`.
			Zusätzliche Syntax: Du kannst Rollen pro Key angeben im Format `key1:admin|user,key2:reader`.
			Beispiel: `URN_API_KEYS=admin-key:admin|editor,reader-key:reader`.
	 - `URN_OIDC_ISSUER`, `URN_OIDC_AUDIENCE`, `URN_OIDC_JWKS_URL` – OIDC Einstellungen für JWT-Validierung (RS256 via JWKS).
	 - `URN_OIDC_JWKS_TTL` (Default: `3600`) – Cache-TTL für JWKS (Sekunden).
 - Kataloge (optional):
	 - `URN_ALLOWED_DOMAINS` – Komma-separierte Liste zulässiger Domänen (lowercase). Wenn gesetzt, werden andere Domänen abgewiesen.
	 - `URN_ALLOWED_OBJ_TYPES` – Komma-separierte Liste zulässiger Objekttypen (lowercase). Wenn gesetzt, werden andere Typen abgewiesen.
	 - `URN_CATALOGS_JSON` – JSON-Objekt für landesspezifische Kataloge mit Vorrang vor den globalen Listen. Format:
	   `{ "nrw": { "domains": ["bimschg"], "obj_types": ["anlage"] }, "by": { "domains": ["bau"], "obj_types": ["bescheid"] } }`
	   Wenn für ein `state` Einträge vorhanden sind, gelten ausschließlich diese; für andere Länder greift der globale Fallback (`URN_ALLOWED_*`).

Beispiel `.env`:

```
URN_DB_URL=sqlite:///./urn_manifest.db
URN_NID=de
URN_STATE_RE=^[a-z]{2,3}$
URN_CORS_ORIGINS=http://localhost:3000
# Federation
URN_PEERS=nrw=https://nrw.resolver.example,by=https://by.resolver.example
URN_FED_TIMEOUT=3.0
URN_FED_CACHE_TTL=300
# Auth
URN_AUTH_MODE=apikey
URN_API_KEYS=dev-secret-1,dev-secret-2
# OIDC (optional)
# URN_AUTH_MODE=oidc
# URN_OIDC_ISSUER=https://issuer.example/realms/realm
# URN_OIDC_AUDIENCE=api://urn-resolver
# URN_OIDC_JWKS_URL=https://issuer.example/realms/realm/protocol/openid-connect/certs
# URN_OIDC_JWKS_TTL=3600
# Kataloge (optional)
# URN_ALLOWED_DOMAINS=bimschg,bau
# URN_ALLOWED_OBJ_TYPES=anlage,bescheid,gutachten
# URN_CATALOGS_JSON={"nrw":{"domains":["bimschg"],"obj_types":["anlage"]},"by":{"domains":["bau"],"obj_types":["bescheid"]}}
```

## Starten (Entwicklung)

Python 3.10+ und Abhängigkeiten gemäß `requirements.txt` installieren. Start via Poetry-Skript:

```
poetry run start
```

oder direkt:

```
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Hinweise zur Föderation

Dieses Backend implementiert die URN-Logik gemäß der begleitenden Strategie und legt Grundlagen für Föderations-Readiness (versionierte API, Health/Ready, CORS, paginierte Suche). Peer-Resolver können konfiguriert werden; bei fehlendem lokalen Manifest wird – falls vorhanden – die zuständige Landesinstanz per `/api/v1/resolve` angefragt und der Befund lokal gecached. Weitere Schritte (IAM, Gateway/GraphQL Federation, Metriken) folgen.

## Migrationen (Alembic)

1. Environment konfigurieren (`.env`), insbesondere `URN_DB_URL` (SQLite oder Postgres).
2. Migrationen anwenden:

Mit Poetry:

```
poetry run alembic upgrade head
```

Mit pip/venv:

```
alembic upgrade head
```

Neue Migration erzeugen (nach Model-Änderungen):

```
alembic revision --autogenerate -m "<beschreibung>"
alembic upgrade head
```

## Postgres via Docker Compose (optional)

Eine lokale Postgres-Instanz kann per Docker Compose gestartet werden. Danach `URN_DB_URL` entsprechend setzen.

```
docker compose up -d postgres
```

## Admin-Endpoints (optional)

Die folgenden Admin-Routen unterstützen das Katalog-Management zur Laufzeit und sind durch die bestehende Authentifizierung geschützt (API-Key oder OIDC, je nach `URN_AUTH_MODE`).

- `GET /admin/catalogs` – Liefert die effektiven Kataloge:
	- `global_domains`, `global_obj_types` (aus `URN_ALLOWED_*`)
	- `state_catalogs` (aus `URN_CATALOGS_JSON`)
- `POST /admin/catalogs/reload` – Lädt die Konfiguration neu und aktualisiert abhängige Module (z. B. URN-Parser), sodass neue Werte sofort wirken.
- `POST /admin/catalogs/set` – Setzt `URN_CATALOGS_JSON` zur Laufzeit (nur im Prozess) und lädt die Konfiguration neu. Payload:

```
{
	"catalogs": {
		"nrw": {"domains": ["bimschg"], "obj_types": ["anlage"]},
		"by": {"domains": ["bau"], "obj_types": ["bescheid"]}
	}
}
```

Hinweis: Die Admin-Operationen wirken pro Prozess/Instanz. In einem verteilten Setup muss die Konfiguration über ein gemeinsames Backend (z. B. ENV/Secrets-Manager) synchronisiert werden.

## Auth / IAM (Kurzreferenz)

Das Projekt unterstützt zwei Haupt-Modi für Zugangssteuerung, konfigurierbar über `URN_AUTH_MODE`:

- `none` (Default) – keine Authentifizierung, geeignet für Entwicklung.
- `apikey` – einfache API-Key-Authentifizierung über Header `X-API-Key`.
- `oidc` – OIDC/JWT Validierung gegen JWKS (konfiguriert über `URN_OIDC_ISSUER`, `URN_OIDC_AUDIENCE`, `URN_OIDC_JWKS_URL`).

API-Key Rollen
- `URN_API_KEYS` unterstützt abwärtskompatibel einfache komma-separierte Keys, z. B. `key1,key2`.
- Zusätzliche Syntax erlaubt Rollen pro Key: `key1:admin|editor,key2:reader`.
	- Beispiel: `URN_API_KEYS=admin-key:admin|editor,reader-key:reader`
	- Bei erfolgreicher Auth liefert die Dependency `require_auth()` ein Principal mit `"roles": [...]`.

OIDC / JWT
- Bei `auth_mode=oidc` validiert das Backend das Bearer-JWT gegen die konfigurierten JWKS.
- Rollen/Claims werden heuristisch extrahiert aus `roles`, `groups`, `scope` oder `realm_access.roles` und ebenfalls in `principal['roles']` abgelegt.

Role-based Endpoints
- Für Endpoints, die eine bestimmte Rolle benötigen, steht die Dependency-Factory `require_role("<role>")` zur Verfügung.
	- Beispiel: `dependencies=[Depends(require_role("admin"))]` sichert Admin-Router.

Entwickler-Hinweis: In Entwicklung ist `URN_AUTH_MODE=none` praktisch; `require_role` erlaubt in diesem Fall weiterhin Zugriff (Komfort für Tests). **In Produktion sollte `none` niemals verwendet werden.**

⚠️ **Production Security Requirements:**
- Authentication MUST be enabled (`URN_AUTH_MODE=apikey` or `oidc`)
- CORS origins MUST be explicitly configured (not `*`)
- PostgreSQL MUST be used (not SQLite)
- See [SECURITY.md](docs/SECURITY.md) for complete deployment checklist

## Developer notes / Warnings

- Starlette meldet eine PendingDeprecationWarning zur Multipart-Implementierung; zur Beseitigung solltest du `python-multipart` in deiner Umgebung installieren (ich habe es in `requirements.txt` ergänzt):

```powershell
& "C:/Program Files/Python313/python.exe" -m pip install python-multipart
```

- httpx gibt gelegentlich eine DeprecationWarning über den `app`-Shortcut aus; das betrifft Fällen in denen `httpx.Client(app=fastapi_app)` verwendet wird. Die empfohlene Alternative ist:

```py
from httpx import WSGITransport
client = httpx.Client(transport=WSGITransport(app=fastapi_app))
```

Diese Warnungen sind nicht kritisch, aber das Aufräumen reduziert Rauschen in CI.

## .env.example

Eine Beispiel-Datei `.env.example` wurde beigefügt mit sinnvollen Defaults und Beispielen (inkl. API-Key-Rollen-Syntax).