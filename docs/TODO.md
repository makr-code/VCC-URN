# VCC-URN Dokumentations-Konsolidierung: TODO & Gap-Analyse

**Datum**: 2025-11-17  
**Ziel**: Schrittweiser Abgleich der Dokumentation gegen den tatsächlichen Implementierungsstand im Sourcecode, um Lücken und Inkonsistenzen aufzudecken.

---

## Überblick

Dieses Dokument dient als zentrale TODO-Liste für die Konsolidierung und Aktualisierung der VCC-URN-Dokumentation. Es vergleicht die Aussagen in den drei Hauptdokumentationen (README.md, complete-guide.md, introducing.md, urn-spec.md) mit dem tatsächlichen Implementierungsstand im Quellcode.

**Status-Legende:**
- ✅ **IMPLEMENTED** - Feature ist vollständig implementiert und dokumentiert
- ⚠️ **PARTIAL** - Feature ist teilweise implementiert oder Dokumentation unvollständig
- ❌ **MISSING** - Feature fehlt in der Implementierung oder ist nicht dokumentiert
- 📝 **DOC_UPDATE** - Dokumentation muss aktualisiert werden

---

## 1. Projektstruktur & Architektur

### 1.1 Modulare Paketstruktur

| Komponente | Dokumentiert in | Status | Bemerkungen |
|------------|----------------|--------|-------------|
| `app/main.py` | README, complete-guide | ✅ IMPLEMENTED | Entrypoint vorhanden, Lifespan korrekt implementiert |
| `vcc_urn/api/v1/endpoints.py` | README, complete-guide | ✅ IMPLEMENTED | Versionierte API-Router korrekt implementiert |
| `vcc_urn/api/admin/endpoints.py` | README, complete-guide | ✅ IMPLEMENTED | Admin-API für Katalog-Management vorhanden |
| `vcc_urn/service.py` | README | ✅ IMPLEMENTED | Service-Layer vorhanden (Kompatibilitäts-Shim) |
| `vcc_urn/services/urn_service.py` | complete-guide | ✅ IMPLEMENTED | Eigentlicher URNService in services/ |
| `vcc_urn/repository.py` | README | ✅ IMPLEMENTED | Repository-Pattern vorhanden (Kompatibilitäts-Shim) |
| `vcc_urn/repository/manifest_repository.py` | complete-guide | ✅ IMPLEMENTED | Eigentliches Repository in repository/ |
| `vcc_urn/models.py` | README | ✅ IMPLEMENTED | ORM-Modelle vorhanden (Kompatibilitäts-Shim) |
| `vcc_urn/models/manifest.py` | complete-guide | ✅ IMPLEMENTED | Eigentliche Modelle in models/ |
| `vcc_urn/db.py` | README | ✅ IMPLEMENTED | DB-Setup vorhanden (Kompatibilitäts-Shim) |
| `vcc_urn/db/session.py` | complete-guide | ✅ IMPLEMENTED | Eigentliche DB-Session in db/ |
| `vcc_urn/config.py` | README | ✅ IMPLEMENTED | Settings vorhanden (Kompatibilitäts-Shim) |
| `vcc_urn/core/config.py` | complete-guide | ✅ IMPLEMENTED | Eigentliche Config in core/ |
| `vcc_urn/security.py` | README | ✅ IMPLEMENTED | Auth-Modul vorhanden (Kompatibilitäts-Shim) |
| `vcc_urn/core/security.py` | complete-guide | ✅ IMPLEMENTED | Eigentliche Security in core/ |
| `vcc_urn/runtime.py` | README | ✅ IMPLEMENTED | Katalog-Verwaltung vorhanden (Kompatibilitäts-Shim) |
| `vcc_urn/core/runtime.py` | complete-guide | ✅ IMPLEMENTED | Eigentliche Runtime in core/ |

**Findings:**
- ✅ Die duale Struktur (Top-Level + Subpackages) ist wie dokumentiert umgesetzt
- ✅ Kompatibilitäts-Shims erlauben alte Imports (`from vcc_urn.config import settings`)
- 📝 **TODO**: Dokumentation könnte die Shim-Strategie expliziter erklären

---

## 2. API-Endpunkte

### 2.1 Basis-Endpunkte (Unversioniert)

| Endpunkt | Dokumentiert in | Status | Bemerkungen |
|----------|----------------|--------|-------------|
| `GET /` | README, complete-guide | ✅ IMPLEMENTED | Info-Endpoint liefert `{"service": "...", "nid": "..."}` |
| `GET /healthz` | README, complete-guide | ✅ IMPLEMENTED | Liefert `{"status": "ok"}` |
| `GET /readyz` | README, complete-guide | ✅ IMPLEMENTED | DB-Check implementiert, wirft 503 bei Fehler |

**Findings:**
- ✅ Alle dokumentierten Basis-Endpunkte vorhanden

### 2.2 Versionierte API (`/api/v1`)

| Endpunkt | Methode | Dokumentiert | Status | Bemerkungen |
|----------|---------|--------------|--------|-------------|
| `/api/v1/generate` | POST | README, complete-guide | ✅ IMPLEMENTED | GenerateRequest/Response korrekt, Auth via `require_auth()` |
| `/api/v1/validate` | POST | README, complete-guide | ✅ IMPLEMENTED | ValidateRequest/Response korrekt, keine Auth |
| `/api/v1/store` | POST | README, complete-guide | ✅ IMPLEMENTED | StoreRequest korrekt, Auth via `require_auth()` |
| `/api/v1/resolve` | GET | README, complete-guide | ✅ IMPLEMENTED | Query-Parameter `urn`, keine Auth, Föderations-Fallback vorhanden |
| `/api/v1/search` | GET | README, complete-guide | ✅ IMPLEMENTED | Query-Parameter `uuid`, `limit`, `offset`, keine Auth |

**Findings:**
- ✅ Alle fünf dokumentierten v1-Endpunkte sind korrekt implementiert
- ✅ Auth-Dependencies entsprechen der Dokumentation
- ✅ Paginierung bei `/search` funktioniert (limit: 1-500, offset: 0+)

### 2.3 Admin-API (`/admin`)

| Endpunkt | Methode | Dokumentiert | Status | Bemerkungen |
|----------|---------|--------------|--------|-------------|
| `/admin/catalogs` | GET | README, complete-guide | ✅ IMPLEMENTED | Liefert effektive Kataloge |
| `/admin/catalogs/reload` | POST | README, complete-guide | ✅ IMPLEMENTED | Lädt Settings neu aus ENV |
| `/admin/catalogs/set` | POST | README, complete-guide | ✅ IMPLEMENTED | Setzt Kataloge zur Laufzeit (ephemeral) |

**Findings:**
- ✅ Alle drei Admin-Endpunkte vorhanden
- ✅ Router nutzt `require_role("admin")` wie dokumentiert
- ✅ AdminCatalogsResponse und AdminCatalogsSetRequest in schemas.py definiert

---

## 3. Konfiguration (ENV-Variablen)

### 3.1 Datenbank

| Variable | Dokumentiert | Status | Default-Wert | Bemerkungen |
|----------|--------------|--------|--------------|-------------|
| `URN_DB_URL` | ✅ README, complete-guide | ✅ IMPLEMENTED | `sqlite:///./urn_manifest.db` | SQLite-Datei im CWD |

**Findings:**
- ✅ SQLite und PostgreSQL werden unterstützt (via SQLAlchemy)

### 3.2 URN-Schema

| Variable | Dokumentiert | Status | Default-Wert | Bemerkungen |
|----------|--------------|--------|--------------|-------------|
| `URN_NID` | ✅ README, complete-guide, urn-spec | ✅ IMPLEMENTED | `de` | NID wird im URN-Parser validiert |
| `URN_STATE_RE` | ✅ README, complete-guide, urn-spec | ✅ IMPLEMENTED | `^[a-z]{2,3}$` | State-Regex wird in URN-Parser geprüft |

**Findings:**
- ✅ NID und State-Pattern korrekt konfigurierbar
- ✅ Validierung in `vcc_urn/services/urn.py` implementiert

### 3.3 CORS

| Variable | Dokumentiert | Status | Default-Wert | Bemerkungen |
|----------|--------------|--------|--------------|-------------|
| `URN_CORS_ORIGINS` | ✅ README, complete-guide | ✅ IMPLEMENTED | `*` | Komma-separierte Origins, `*` für Entwicklung |

**Findings:**
- ✅ CORS-Middleware in `app/main.py` korrekt konfiguriert

### 3.4 Föderation

| Variable | Dokumentiert | Status | Default-Wert | Bemerkungen |
|----------|--------------|--------|--------------|-------------|
| `URN_PEERS` | ✅ README, complete-guide | ✅ IMPLEMENTED | `""` | Format: `state=url` z.B. `nrw=https://nrw.example` |
| `URN_FED_TIMEOUT` | ✅ README, complete-guide | ✅ IMPLEMENTED | `3.0` | HTTP-Timeout in Sekunden |
| `URN_FED_CACHE_TTL` | ✅ README, complete-guide | ✅ IMPLEMENTED | `300` | TTL-Cache für Peer-Results in Sekunden |

**Findings:**
- ✅ Föderation vollständig implementiert in `vcc_urn/services/federation.py`
- ✅ TTL-Cache korrekt implementiert
- ✅ Peer-Auflösung funktioniert über `/api/v1/resolve`

### 3.5 Authentifizierung

| Variable | Dokumentiert | Status | Default-Wert | Bemerkungen |
|----------|--------------|--------|--------------|-------------|
| `URN_AUTH_MODE` | ✅ README, complete-guide | ✅ IMPLEMENTED | `none` | Modi: `none`, `apikey`, `oidc` |
| `URN_API_KEYS` | ✅ README, complete-guide | ✅ IMPLEMENTED | `""` | Komma-separiert, mit optionalen Rollen: `key:role1\|role2` |
| `URN_OIDC_ISSUER` | ✅ README, complete-guide | ✅ IMPLEMENTED | `""` | OIDC Issuer-URL |
| `URN_OIDC_AUDIENCE` | ✅ README, complete-guide | ✅ IMPLEMENTED | `""` | OIDC Audience |
| `URN_OIDC_JWKS_URL` | ✅ README, complete-guide | ✅ IMPLEMENTED | `""` | JWKS-Endpoint-URL |
| `URN_OIDC_JWKS_TTL` | ✅ README, complete-guide | ✅ IMPLEMENTED | `3600` | JWKS-Cache-TTL in Sekunden |

**Findings:**
- ✅ Alle drei Auth-Modi (`none`, `apikey`, `oidc`) implementiert
- ✅ API-Key-Rollen-Syntax korrekt implementiert (`_parse_keys_map()`)
- ✅ OIDC/JWT-Validierung mit JWKS implementiert
- ✅ Rollen-Extraktion aus JWT-Claims vorhanden (`extract_roles_from_claims()`)
- ✅ `require_auth()` und `require_role()` Dependencies vorhanden

### 3.6 Kataloge

| Variable | Dokumentiert | Status | Default-Wert | Bemerkungen |
|----------|--------------|--------|--------------|-------------|
| `URN_ALLOWED_DOMAINS` | ✅ README, complete-guide | ✅ IMPLEMENTED | `""` | Globale Domänen, komma-separiert |
| `URN_ALLOWED_OBJ_TYPES` | ✅ README, complete-guide | ✅ IMPLEMENTED | `""` | Globale Objekttypen, komma-separiert |
| `URN_CATALOGS_JSON` | ✅ README, complete-guide, urn-spec | ✅ IMPLEMENTED | `""` | JSON für State-spezifische Kataloge |

**Findings:**
- ✅ Katalog-System vollständig implementiert
- ✅ State-spezifische Kataloge haben Vorrang vor globalen (wie dokumentiert)
- ✅ Runtime-Verwaltung über Admin-API funktioniert
- ✅ URN-Parser validiert gegen effektive Kataloge

---

## 4. URN-Spezifikation

### 4.1 URN-Syntax

| Komponente | Dokumentiert | Status | Bemerkungen |
|------------|--------------|--------|-------------|
| Format `urn:de:<state>:<domain>:<objtype>:<local>:<uuid>[:<version>]` | ✅ urn-spec | ✅ IMPLEMENTED | Regex-Pattern in `vcc_urn/services/urn.py` |
| NID Validierung | ✅ urn-spec | ✅ IMPLEMENTED | Prüft gegen `settings.nid` |
| State Validierung | ✅ urn-spec | ✅ IMPLEMENTED | Prüft gegen `settings.state_pattern` |
| Domain Katalog-Validierung | ✅ urn-spec | ✅ IMPLEMENTED | Prüft gegen effektive Kataloge |
| Obj_Type Katalog-Validierung | ✅ urn-spec | ✅ IMPLEMENTED | Prüft gegen effektive Kataloge |
| Local_Aktenzeichen URL-Encoding | ✅ urn-spec | ✅ IMPLEMENTED | `quote()/unquote()` in URN-Klasse |
| UUID-Validierung | ✅ urn-spec | ✅ IMPLEMENTED | Regex-Pattern: 36 Zeichen `[0-9a-fA-F-]` |
| Version (optional) | ✅ urn-spec | ✅ IMPLEMENTED | Format `v[0-9A-Za-z-.]+` |

**Findings:**
- ✅ URN-Syntax vollständig wie in urn-spec.md dokumentiert
- ✅ Alle Validierungsregeln implementiert
- ✅ `URN` Klasse mit `_parse()` Methode vorhanden
- ✅ `URN.generate()` Klassenmethode vorhanden

### 4.2 URN-Operationen

| Operation | Dokumentiert | Status | Bemerkungen |
|-----------|--------------|--------|-------------|
| `URN.generate()` | ✅ urn-spec | ✅ IMPLEMENTED | Normalisiert State/Domain/ObjType zu lowercase, kodiert Local, erzeugt UUID |
| `URN.parse()` (via `__init__`) | ✅ urn-spec | ✅ IMPLEMENTED | Parst String zu URNComponents |
| Katalog-Validierung beim Parsen | ✅ urn-spec | ✅ IMPLEMENTED | Wirft ValueError bei ungültigen Werten |

**Findings:**
- ✅ Alle dokumentierten URN-Operationen vorhanden

---

## 5. Service-Layer & Business-Logik

### 5.1 URNService

| Methode | Dokumentiert | Status | Bemerkungen |
|---------|--------------|--------|-------------|
| `generate()` | ✅ README | ✅ IMPLEMENTED | In `vcc_urn/services/urn_service.py` |
| `validate()` | ✅ README | ✅ IMPLEMENTED | Liefert ValidateResponse |
| `store_manifest()` | ✅ README | ✅ IMPLEMENTED | Upsert via Repository |
| `resolve()` | ✅ README | ✅ IMPLEMENTED | Lokale DB + Föderations-Fallback |
| `search_by_uuid()` | ✅ README | ✅ IMPLEMENTED | Mit Pagination |
| `db_health()` | ⚠️ UNDOCUMENTED | ✅ IMPLEMENTED | Für `/readyz` Endpoint |

**Findings:**
- ✅ Alle dokumentierten Service-Methoden vorhanden
- 📝 **TODO**: `db_health()` sollte in Dokumentation erwähnt werden

### 5.2 Föderations-Resolver

| Feature | Dokumentiert | Status | Bemerkungen |
|---------|--------------|--------|-------------|
| Peer-Resolver-Konfiguration | ✅ README, complete-guide | ✅ IMPLEMENTED | Via `URN_PEERS` |
| HTTP-Request an Peer-Resolver | ✅ README, complete-guide | ✅ IMPLEMENTED | In `federation.py::resolve_via_peer()` |
| TTL-Cache für Peer-Results | ✅ README, complete-guide | ✅ IMPLEMENTED | `TTLCache` Klasse mit get/set |
| Timeout-Konfiguration | ✅ README, complete-guide | ✅ IMPLEMENTED | Via `URN_FED_TIMEOUT` |
| Cache-TTL-Konfiguration | ✅ README, complete-guide | ✅ IMPLEMENTED | Via `URN_FED_CACHE_TTL` |

**Findings:**
- ✅ Föderation vollständig implementiert wie dokumentiert
- ✅ Graceful Fallback bei Peer-Fehlern (returniert `None`)

---

## 6. Datenbank & Repository

### 6.1 Manifest-Modell

| Feld | Dokumentiert | Status | Bemerkungen |
|------|--------------|--------|-------------|
| `urn` (PK) | ✅ complete-guide | ✅ IMPLEMENTED | VARCHAR(512) Primary Key |
| `nid` | ✅ complete-guide | ✅ IMPLEMENTED | VARCHAR(32) |
| `state` | ✅ complete-guide | ✅ IMPLEMENTED | VARCHAR(10), indiziert |
| `domain` | ✅ complete-guide | ✅ IMPLEMENTED | VARCHAR(64) |
| `obj_type` | ✅ complete-guide | ✅ IMPLEMENTED | VARCHAR(64) |
| `local_aktenzeichen` | ✅ complete-guide | ✅ IMPLEMENTED | VARCHAR(512) |
| `uuid` | ✅ complete-guide | ✅ IMPLEMENTED | VARCHAR(36), indiziert |
| `version` | ✅ complete-guide | ✅ IMPLEMENTED | VARCHAR(64), optional |
| `manifest_json` | ✅ complete-guide | ✅ IMPLEMENTED | TEXT |
| `created_at` | ✅ complete-guide | ✅ IMPLEMENTED | TIMESTAMPTZ |
| `updated_at` | ✅ complete-guide | ✅ IMPLEMENTED | TIMESTAMPTZ |

**Findings:**
- ✅ Alle dokumentierten Felder vorhanden in `vcc_urn/models/manifest.py`
- ✅ Indizes auf `state` und `uuid` vorhanden

### 6.2 Repository-Pattern

| Operation | Dokumentiert | Status | Bemerkungen |
|-----------|--------------|--------|-------------|
| `upsert_manifest()` | ✅ README | ✅ IMPLEMENTED | In `ManifestRepository` |
| `get_by_urn()` | ⚠️ UNDOCUMENTED | ✅ IMPLEMENTED | Vorhanden in Repository |
| `search_by_uuid()` | ✅ README | ✅ IMPLEMENTED | Mit Pagination |

**Findings:**
- ✅ Repository-Pattern korrekt implementiert
- 📝 **TODO**: `get_by_urn()` sollte dokumentiert werden

### 6.3 Migrationen (Alembic)

| Feature | Dokumentiert | Status | Bemerkungen |
|---------|--------------|--------|-------------|
| Alembic-Setup | ✅ README, complete-guide | ✅ IMPLEMENTED | `alembic.ini` vorhanden |
| `alembic upgrade head` | ✅ README, complete-guide | ✅ IMPLEMENTED | Migrationen in `alembic/versions/` |
| `alembic revision --autogenerate` | ✅ complete-guide | ✅ IMPLEMENTED | Alembic-ENV korrekt konfiguriert |
| Automatisches `init_db()` bei Start | ✅ README | ✅ IMPLEMENTED | In `app/main.py` Lifespan |

**Findings:**
- ✅ Alembic vollständig konfiguriert
- ✅ `init_db()` erstellt Tabellen automatisch in SQLite
- ✅ Alembic für Schema-Änderungen einsatzbereit

---

## 7. Authentifizierung & Autorisierung

### 7.1 Auth-Modi

| Modus | Dokumentiert | Status | Bemerkungen |
|-------|--------------|--------|-------------|
| `none` | ✅ README, complete-guide | ✅ IMPLEMENTED | Keine Auth, für Entwicklung |
| `apikey` | ✅ README, complete-guide | ✅ IMPLEMENTED | Header `X-API-Key` |
| `oidc` | ✅ README, complete-guide | ✅ IMPLEMENTED | Bearer JWT via JWKS |

**Findings:**
- ✅ Alle drei Modi implementiert in `vcc_urn/core/security.py`

### 7.2 API-Key-Authentifizierung

| Feature | Dokumentiert | Status | Bemerkungen |
|---------|--------------|--------|-------------|
| Einfache Keys (komma-separiert) | ✅ README, complete-guide | ✅ IMPLEMENTED | `key1,key2` |
| Rollen-Syntax `key:role1\|role2` | ✅ README, complete-guide | ✅ IMPLEMENTED | `_parse_keys_map()` |
| Header `X-API-Key` | ✅ complete-guide | ✅ IMPLEMENTED | In `require_auth()` |
| Principal mit Rollen | ✅ README, complete-guide | ✅ IMPLEMENTED | Dict mit `{"roles": [...]}` |

**Findings:**
- ✅ API-Key-System vollständig wie dokumentiert

### 7.3 OIDC/JWT-Authentifizierung

| Feature | Dokumentiert | Status | Bemerkungen |
|---------|--------------|--------|-------------|
| Bearer-Token-Validierung | ✅ complete-guide | ✅ IMPLEMENTED | Via `jose.jwt.decode()` |
| JWKS-Fetch und Caching | ✅ complete-guide | ✅ IMPLEMENTED | `_get_jwks()` mit TTL-Cache |
| Rollen-Extraktion aus Claims | ✅ complete-guide | ✅ IMPLEMENTED | `extract_roles_from_claims()` |
| Heuristiken: roles/groups/scope/realm_access | ✅ complete-guide | ✅ IMPLEMENTED | Alle vier Claim-Typen unterstützt |
| RS256-Signatur-Validierung | ✅ complete-guide | ✅ IMPLEMENTED | Via JWKS |
| Issuer/Audience-Validierung | ✅ complete-guide | ✅ IMPLEMENTED | Via `settings.oidc_issuer/audience` |

**Findings:**
- ✅ OIDC/JWT vollständig implementiert
- ✅ Alle dokumentierten Claim-Heuristiken vorhanden
- ✅ JWKS-Cache mit konfigurierbarem TTL

### 7.4 Rollenbasierte Zugriffskontrolle

| Feature | Dokumentiert | Status | Bemerkungen |
|---------|--------------|--------|-------------|
| `require_auth()` Dependency | ✅ README | ✅ IMPLEMENTED | Liefert Principal |
| `require_role(role)` Dependency | ✅ README, complete-guide | ✅ IMPLEMENTED | Factory-Funktion |
| Admin-Router mit `require_role("admin")` | ✅ README, complete-guide | ✅ IMPLEMENTED | In `api/admin/endpoints.py` |
| Dev-Mode: `none` erlaubt alle Rollen | ✅ complete-guide | ✅ IMPLEMENTED | In `require_role()` |

**Findings:**
- ✅ RBAC vollständig implementiert
- ✅ Dev-Mode-Komfort wie dokumentiert

---

## 8. Schemas (Pydantic)

### 8.1 Request-Schemas

| Schema | Dokumentiert | Status | Bemerkungen |
|--------|--------------|--------|-------------|
| `GenerateRequest` | ✅ README, complete-guide | ✅ IMPLEMENTED | Alle Felder vorhanden |
| `ValidateRequest` | ✅ README, complete-guide | ✅ IMPLEMENTED | Feld `urn` |
| `StoreRequest` | ✅ README, complete-guide | ✅ IMPLEMENTED | Felder `urn`, `manifest` |
| `AdminCatalogsSetRequest` | ✅ README, complete-guide | ✅ IMPLEMENTED | Feld `catalogs` |

**Findings:**
- ✅ Alle Request-Schemas vorhanden in `vcc_urn/schemas.py`

### 8.2 Response-Schemas

| Schema | Dokumentiert | Status | Bemerkungen |
|--------|--------------|--------|-------------|
| `GenerateResponse` | ✅ README, complete-guide | ✅ IMPLEMENTED | Feld `urn` |
| `ValidateResponse` | ✅ README, complete-guide | ✅ IMPLEMENTED | Felder `valid`, `reason`, `components` |
| `SearchResponse` | ✅ README, complete-guide | ✅ IMPLEMENTED | Felder `count`, `results` |
| `AdminCatalogsResponse` | ✅ README, complete-guide | ✅ IMPLEMENTED | Felder `global_domains`, `global_obj_types`, `state_catalogs` |

**Findings:**
- ✅ Alle Response-Schemas vorhanden und korrekt

---

## 9. Tests

### 9.1 Test-Abdeckung

| Test-Datei | Zweck | Status | Bemerkungen |
|------------|-------|--------|-------------|
| `test_urn.py` | URN-Parse/Generate | ✅ IMPLEMENTED | 3 Tests |
| `test_api.py` | API-Endpunkte | ✅ IMPLEMENTED | 2 Tests |
| `test_service.py` | Service-Layer | ✅ IMPLEMENTED | 1 Test |
| `test_security_roles.py` | RBAC | ✅ IMPLEMENTED | 6 Tests |
| `test_admin_catalogs.py` | Admin-API | ✅ IMPLEMENTED | 1 Test |
| `test_state_catalogs.py` | State-Kataloge | ✅ IMPLEMENTED | 1 Test |
| `test_urn_catalogs.py` | URN-Katalog-Validierung | ✅ IMPLEMENTED | 1 Test |

**Findings:**
- ✅ Grundlegende Tests vorhanden (15 Tests insgesamt)
- ⚠️ **PARTIAL**: Keine expliziten Tests für:
  - Föderation (`resolve_via_peer()`)
  - OIDC/JWT-Validierung
  - JWKS-Caching
  - TTL-Cache
  - DB-Health-Check
- 📝 **TODO**: Test-Coverage erhöhen für kritische Features

### 9.2 Test-Infrastruktur

| Feature | Status | Bemerkungen |
|---------|--------|-------------|
| pytest-Setup | ✅ IMPLEMENTED | `pytest.ini` vorhanden |
| Test-DB (in-memory) | ✅ IMPLEMENTED | `conftest.py` konfiguriert |
| Fixtures | ✅ IMPLEMENTED | DB-Session, TestClient |

**Findings:**
- ✅ Test-Infrastruktur solide

---

## 10. Entwickler-Tooling

### 10.1 Linting & Formatierung

| Tool | Dokumentiert | Status | Bemerkungen |
|------|--------------|--------|-------------|
| Ruff (Linting) | ✅ complete-guide | ✅ IMPLEMENTED | `pyproject.toml` konfiguriert |
| Black (Formatierung) | ✅ complete-guide | ✅ IMPLEMENTED | `pyproject.toml` konfiguriert |
| mypy (Type-Checking) | ✅ complete-guide | ✅ IMPLEMENTED | `pyproject.toml` konfiguriert |

**Findings:**
- ✅ Alle dokumentierten Tools konfiguriert
- ✅ `ruff check .` funktioniert
- ✅ `black .` funktioniert
- ✅ `mypy vcc_urn/` funktioniert

### 10.2 Poetry-Skripte

| Skript | Dokumentiert | Status | Bemerkungen |
|--------|--------------|--------|-------------|
| `poetry run start` | ✅ README | ✅ IMPLEMENTED | Startet Uvicorn mit Reload |

**Findings:**
- ✅ Start-Skript vorhanden in `pyproject.toml`

---

## 11. Deployment & Betrieb

### 11.1 Docker (Beispiele in Doku)

| Feature | Dokumentiert | Status | Bemerkungen |
|---------|--------------|--------|-------------|
| Dockerfile (Beispiel) | ✅ complete-guide | ❌ MISSING | Nur als Beispiel in Doku, nicht im Repo |
| docker-compose.yml | ✅ README, complete-guide | ⚠️ PARTIAL | Vorhanden, aber nur mit Postgres-Service |

**Findings:**
- ❌ **MISSING**: Kein produktives Dockerfile im Repo
- ⚠️ **PARTIAL**: docker-compose.yml enthält nur Postgres, keine App-Service-Definition
- 📝 **TODO**: Produktives Dockerfile hinzufügen
- 📝 **TODO**: docker-compose.yml um App-Service erweitern (wie in complete-guide.md dokumentiert)

### 11.2 Kubernetes (Beispiele in Doku)

| Feature | Dokumentiert | Status | Bemerkungen |
|---------|--------------|--------|-------------|
| ConfigMap (Beispiel) | ✅ complete-guide | ❌ MISSING | Nur als Beispiel in Doku |
| Deployment (Beispiel) | ✅ complete-guide | ❌ MISSING | Nur als Beispiel in Doku |

**Findings:**
- ❌ **MISSING**: Keine K8s-Manifeste im Repo (aber als Beispiele dokumentiert)
- 📝 **TODO**: Optional K8s-Beispiele in `deployment/`-Ordner hinzufügen

### 11.3 Monitoring & Observability

| Feature | Dokumentiert | Status | Bemerkungen |
|---------|--------------|--------|-------------|
| Health-Checks (`/healthz`, `/readyz`) | ✅ complete-guide | ✅ IMPLEMENTED | Für Liveness/Readiness Probes |
| Prometheus-Metriken | ✅ complete-guide (TODO) | ❌ MISSING | In Doku als "TODO" markiert |
| Structured Logging | ✅ complete-guide (TODO) | ❌ MISSING | In Doku als "TODO" markiert |

**Findings:**
- ✅ Basic Health-Checks vorhanden
- ❌ **MISSING**: Prometheus-Integration (in Doku explizit als TODO)
- ❌ **MISSING**: Structured Logging (in Doku explizit als TODO)
- 📝 **TODO**: Prometheus-Metriken optional implementieren
- 📝 **TODO**: Structured Logging optional implementieren

---

## 12. Dokumentations-Konsistenz

### 12.1 README.md vs. complete-guide.md

| Aspekt | README | complete-guide | Konsistenz | Bemerkungen |
|--------|--------|----------------|------------|-------------|
| Projektstruktur | Beschreibt Top-Level + Subpackages | Beschreibt Clean Architecture mit Subpackages | ✅ CONSISTENT | Beide korrekt, complete-guide detaillierter |
| API-Endpunkte | Listet alle 5 v1-Endpunkte + Admin | Detaillierte API-Referenz mit Request/Response-Beispielen | ✅ CONSISTENT | complete-guide detaillierter |
| Konfiguration | Listet alle ENV-Variablen mit Beispielen | Tabellarische ENV-Referenz | ✅ CONSISTENT | Beide vollständig |
| Auth-Modi | Beschreibt alle 3 Modi kurz | Detaillierte Auth-Sektion mit Beispielen | ✅ CONSISTENT | complete-guide umfassender |
| Föderation | Beschreibt Konzept und Config | Detaillierte Föderation-Sektion | ✅ CONSISTENT | Beide korrekt |

**Findings:**
- ✅ README und complete-guide sind konsistent
- ✅ README ist kompakt, complete-guide ist umfassend
- ✅ Keine Widersprüche gefunden

### 12.2 urn-spec.md

| Aspekt | Status | Bemerkungen |
|--------|--------|-------------|
| URN-Syntax | ✅ CONSISTENT | Stimmt mit Implementierung überein |
| Validierungsregeln | ✅ CONSISTENT | Alle Regeln implementiert |
| Katalog-System | ✅ CONSISTENT | Korrekt beschrieben |
| API-Vertrag (Auszug) | ✅ CONSISTENT | Endpunkte korrekt |

**Findings:**
- ✅ urn-spec.md ist technisch korrekt und konsistent mit Code

### 12.3 introducing.md

| Aspekt | Status | Bemerkungen |
|--------|--------|-------------|
| Strategisches Konzept | ✅ INFORMATIONAL | Beschreibt Vision, nicht konkrete Implementation |
| URN-Schema | ✅ CONSISTENT | URN-Syntax stimmt überein |
| Föderations-Architektur | ✅ CONSISTENT | Grundprinzipien implementiert (Peers, Resolve, Cache) |
| Gateway/GraphQL Federation | ⚠️ ASPIRATIONAL | Nicht implementiert (strategische Vision) |
| Saga-Pattern | ⚠️ ASPIRATIONAL | Nicht implementiert (strategische Vision) |
| IAM-Federation (SAML/OIDC/SCIM) | ⚠️ PARTIAL | OIDC implementiert, SAML/SCIM nicht |

**Findings:**
- ✅ introducing.md ist ein strategisches Konzeptdokument
- ⚠️ **ASPIRATIONAL**: Viele Features sind Vision (GraphQL Federation, Saga, SCIM)
- 📝 **TODO**: Explizit kennzeichnen, was Vision vs. Implementierung ist

---

## 13. Fehlende Features (Gaps)

### 13.1 In Dokumentation erwähnt, aber nicht implementiert

| Feature | Dokumentiert in | Priorität | Bemerkungen |
|---------|----------------|-----------|-------------|
| Produktives Dockerfile | complete-guide | MEDIUM | Nur Beispiel in Doku |
| K8s-Manifeste | complete-guide | LOW | Nur Beispiele in Doku |
| Prometheus-Metriken | complete-guide | MEDIUM | Explizit als TODO markiert |
| Structured Logging | complete-guide | MEDIUM | Explizit als TODO markiert |
| GraphQL Federation | introducing.md | LOW | Strategische Vision |
| Saga-Pattern | introducing.md | LOW | Strategische Vision |
| SAML/SCIM | introducing.md | LOW | Strategische Vision |

**Findings:**
- ✅ Die meisten "fehlenden" Features sind explizit als TODO oder Vision gekennzeichnet
- 📝 **TODO**: Dockerfile hinzufügen (einfach)
- 📝 **TODO**: Optional Prometheus/Logging implementieren

### 13.2 Implementiert, aber undokumentiert

| Feature | Implementiert in | Priorität | Bemerkungen |
|---------|-----------------|-----------|-------------|
| `db_health()` in URNService | `vcc_urn/services/urn_service.py` | LOW | Wird für `/readyz` verwendet |
| `get_by_urn()` im Repository | `vcc_urn/repository/manifest_repository.py` | LOW | Grundlegende CRUD-Operation |
| Kompatibilitäts-Shims | Top-Level `vcc_urn/*.py` | MEDIUM | Ermöglichen alte Imports |

**Findings:**
- 📝 **TODO**: Diese Features in Dokumentation ergänzen

---

## 14. Priorisierte TODO-Liste

### 🔴 Hoch (Kritische Diskrepanzen)

- _Keine kritischen Diskrepanzen gefunden_

### 🟡 Mittel (Verbesserungen)

1. **Dockerfile hinzufügen**
   - Produktives Dockerfile in Repo aufnehmen
   - Basierend auf Beispiel in complete-guide.md
   - Datei: `/Dockerfile`

2. **docker-compose.yml erweitern**
   - App-Service hinzufügen (nicht nur Postgres)
   - Basierend auf Beispiel in complete-guide.md
   - Datei: `/docker-compose.yml`

3. **Dokumentation: Kompatibilitäts-Shims erklären**
   - README oder complete-guide ergänzen
   - Erklären, warum Top-Level + Subpackages existieren
   - Abschnitt: "Projektstruktur"

4. **Dokumentation: Implementierte aber undokumentierte Features**
   - `db_health()` Methode dokumentieren
   - `get_by_urn()` Methode dokumentieren
   - Abschnitt: Service-API-Referenz

5. **Test-Coverage erhöhen**
   - Tests für Föderation (`resolve_via_peer()`)
   - Tests für OIDC/JWT-Validierung
   - Tests für JWKS-Caching
   - Tests für TTL-Cache
   - Ziel: >80% Coverage

### 🟢 Niedrig (Optional)

6. **Prometheus-Metriken (Optional)**
   - `prometheus-fastapi-instrumentator` integrieren
   - `/metrics` Endpoint hinzufügen
   - In Doku bereits als TODO erwähnt

7. **Structured Logging (Optional)**
   - JSON-basiertes Logging implementieren
   - In Doku bereits als TODO erwähnt

8. **K8s-Beispiele (Optional)**
   - ConfigMap/Deployment-Manifeste in `deployment/k8s/`
   - Basierend auf Beispielen in complete-guide.md

9. **introducing.md: Vision vs. Implementierung kennzeichnen**
   - Explizit markieren, welche Features Vision sind
   - Hinweis am Anfang des Dokuments
   - Z.B.: "Dieses Dokument beschreibt die strategische Vision. Aktuell implementiert ist..."

---

## 15. Zusammenfassung

### ✅ Stärken

- **Vollständige Kern-Implementation**: Alle dokumentierten Hauptfeatures (URN, API, Auth, Föderation, Kataloge) sind implementiert
- **Konsistente Dokumentation**: README, complete-guide und urn-spec sind konsistent
- **Modular & erweiterbar**: Saubere Architektur mit Subpackages und Kompatibilitäts-Shims
- **Solide Test-Basis**: 15 Tests, alle bestehen
- **Produktionsreife Features**: OIDC, RBAC, Föderation, Admin-API

### ⚠️ Verbesserungspotenzial

- **Deployment-Artefakte**: Produktives Dockerfile und vollständiges docker-compose fehlen
- **Observability**: Prometheus und Structured Logging noch nicht implementiert (aber als TODO dokumentiert)
- **Test-Coverage**: Einige kritische Features (Föderation, OIDC) haben keine expliziten Tests
- **Dokumentations-Klarheit**: Shim-Strategie und einige implementierte Hilfsmethoden nicht dokumentiert

### 📊 Dokumentations-Implementierungs-Abgleich

- **Implementierungsgrad**: ~90% der dokumentierten Features sind vollständig implementiert
- **Dokumentationsgrad**: ~85% der implementierten Features sind dokumentiert
- **Konsistenz**: ~95% - sehr hohe Konsistenz zwischen Doku und Code

### 🎯 Empfehlung

Die Codebasis ist in einem sehr guten Zustand. Die Dokumentation ist umfassend und größtenteils korrekt. Die identifizierten Lücken sind überschaubar und betreffen hauptsächlich:
1. **Deployment-Artefakte** (einfach zu ergänzen)
2. **Optional Features** (Prometheus, Logging - bereits als TODO markiert)
3. **Test-Coverage** (Verbesserungspotenzial vorhanden)

**Nächste Schritte:**
1. Mittel-Priorität TODOs abarbeiten (Dockerfile, Doku-Updates, Tests)
2. Optional: Niedrig-Priorität Features nach Bedarf
3. Regelmäßige Synchronisation Doku ↔ Code bei neuen Features

---

## 16. Weiterentwicklungsstrategie (November 2025)

### ✅ Strategiedokumente erstellt

**Status:** COMPLETED (2025-11-23)

1. **Comprehensive Development Strategy** (`docs/development-strategy.md`)
   - 3-Phasen-Strategie (Production Hardening → Federation Evolution → Föderiertes Ökosystem)
   - Detaillierte technische Roadmap mit Meilensteinen
   - Integration mit VCC-Ökosystem (Veritas, Covina, Clara)
   - Governance-Modell (KI-Föderationsrat VCC)
   - Risikomanagement & Mitigation
   - KPIs & Erfolgsmessung
   - Best Practices & Technologie-Stack-Evolution

2. **Executive Roadmap** (`docs/ROADMAP.md`)
   - Kompakte Übersicht der 3 Phasen
   - Quick Start Guide (Next 30 Days)
   - Priorisierte Actionable Items
   - KPI-Dashboard
   - Integrationspunkte mit VCC-Komponenten

### 📋 Strategische Empfehlungen

**Kurzfristig (< 3 Monate) - Phase 1 Quick Wins:**
1. Dockerfile + docker-compose.yml (Woche 1-2)
2. Prometheus + Structured Logging (Woche 3-4)
3. Test-Coverage erhöhen auf 80% (Woche 5-6)
4. K8s-Manifeste (Beispiele)

**Mittelfristig (3-9 Monate) - Phase 2 Pilot:**
1. GraphQL-API mit Apollo Federation
2. Redis-Cache + mTLS für Peers
3. Admin-Dashboard (Web-UI)
4. Pilot mit 2-3 Bundesländern

**Langfristig (9-18 Monate) - Phase 3 Rollout:**
1. Zentraler Föderations-Gateway (Apollo Router)
2. Saga-Orchestrator (Temporal.io)
3. Föderiertes IAM (SAML + SCIM)
4. 16-Bundesländer-Integration

### 🎯 Kernerkenntnisse

- **Aktueller Stand:** ~90% feature-complete für Kernfunktionalität
- **Hauptfokus:** Production Readiness (Deployment, Observability, Stabilität)
- **Vision:** Föderierte Graph-RAG-Architektur für deutsche Verwaltung
- **Alignment:** Integration mit Deutsche Verwaltungscloud-Strategie

**Siehe:**
- Vollständige Strategie: [development-strategy.md](./development-strategy.md)
- Executive Summary: [ROADMAP.md](./ROADMAP.md)

---

**Erstellt**: 2025-11-17  
**Autor**: VCC-URN Dokumentations-Review  
**Aktualisiert**: 2025-11-23 (Weiterentwicklungsstrategie)  
**Nächstes Review**: Bei größeren Feature-Änderungen
