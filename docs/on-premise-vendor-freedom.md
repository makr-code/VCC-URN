# On-Premise & Vendor-Lock-In Freiheit

## Grundsatz

**VCC-URN ist zu 100% on-premise deploybar und frei von Vendor-Lock-In.**

Dieser Grundsatz gilt für alle Phasen der Entwicklung und ist nicht verhandelbar.

## Prinzipien

### 1. Open-Source-First

Alle verwendeten Technologien sind Open-Source und selbst hostbar:

**Phase 1 & 2:**
- ✅ **FastAPI** - MIT License, Python-basiert
- ✅ **PostgreSQL** - PostgreSQL License (permissive)
- ✅ **SQLite** - Public Domain
- ✅ **Redis** - BSD License, selbst hostbar
- ✅ **Themis AQL** - VCC-intern, Open-Source (bevorzugt)
- ⚠️ **Strawberry GraphQL** - MIT License (optional, wird durch Themis AQL ersetzt)
- ✅ **Prometheus** - Apache 2.0 License
- ✅ **Docker** - Apache 2.0 License
- ✅ **Kubernetes** - Apache 2.0 License

**Phase 3 (geplant):**
- ✅ **Themis Federation Gateway** - VCC-intern, selbst hostbar (bevorzugt)
- ⚠️ **Apollo Router** - Elastic License 2.0 (vermieden - nicht vendor-free genug)
- ✅ **Temporal.io** - MIT License (selbst hostbar, für Saga-Pattern)
- ✅ **Keycloak** - Apache 2.0 License (selbst hostbar)
- ✅ **OpenTelemetry** - Apache 2.0 License
- ✅ **Jaeger** - Apache 2.0 License

**Wichtig:** VCC verwendet **Themis AQL** statt GraphQL (siehe [ADR-0001](./adr/0001-themis-aql-statt-graphql.md))

### 2. Standard-Protokolle

Keine proprietären APIs oder Protokolle:

- ✅ **HTTP/HTTPS** - Offener Standard (RFC 2616/7230)
- ✅ **Themis AQL** - VCC-intern, offen spezifiziert
- ⚠️ **GraphQL** - Offene Spezifikation (optional, wird durch AQL ersetzt)
- ✅ **REST** - Architekturstil (nicht proprietär)
- ✅ **OIDC/OAuth 2.0** - Offene Standards (RFC 6749, RFC 7519)
- ✅ **SAML 2.0** - OASIS-Standard
- ✅ **Redis Protocol** - Offen dokumentiert

### 3. Container-Portabilität

Deployment ist nicht an einen Cloud-Anbieter gebunden:

- ✅ **Docker** - Läuft auf jeder Linux-Plattform
- ✅ **Kubernetes** - Läuft auf:
  - On-Premise (Bare Metal / VMware)
  - Sovereign Cloud (Gaia-X-konforme Provider)
  - Rancher / K3s (Edge Computing)
  - OpenShift (Enterprise)

### 4. Datenbank-Flexibilität

Keine Cloud-spezifischen Datenbankdienste:

- ✅ **PostgreSQL** - Selbst hostbar (v10+)
- ✅ **SQLite** - Dateibasiert, keine Infrastruktur nötig
- ✅ **Redis** - Selbst hostbar (v7+)

**Explizit NICHT verwendet:**
- ❌ AWS RDS
- ❌ AWS DynamoDB
- ❌ Azure Cosmos DB
- ❌ Google Cloud Spanner

### 5. Cache & Messaging

Keine Cloud-spezifischen Cache- oder Messaging-Dienste:

- ✅ **Redis** - Open-Source, selbst hostbar
- ✅ **Redis Pub/Sub** - Kein separater Service nötig

**Explizit NICHT verwendet:**
- ❌ AWS ElastiCache
- ❌ AWS SQS/SNS
- ❌ Azure Cache for Redis (Managed)
- ❌ Google Cloud Memorystore

## Deployment-Optionen (alle on-premise)

### Option 1: Docker Compose

```bash
docker-compose up -d
```

- Läuft auf jedem Linux-Server
- Keine Cloud-Abhängigkeit
- Ideal für kleine Installationen (einzelne Landesinstanz)

### Option 2: Kubernetes

```bash
kubectl apply -f deployment/k8s/
```

- Läuft auf jedem Kubernetes-Cluster (on-premise oder sovereign cloud)
- Unterstützt Gaia-X-konforme Infrastrukturen
- Ideal für Produktionsbetrieb (16 Bundesländer)

### Option 3: Bare Metal

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app
```

- Läuft direkt auf Linux-Server (ohne Container)
- Maximale Kontrolle
- Ideal für spezielle Sicherheitsanforderungen

## Sovereign Cloud Compatibility

VCC-URN ist kompatibel mit **Gaia-X-konformen** Cloud-Providern:

### Deutsche/EU-Provider

- **Sovereign Cloud Stack (SCS)** - Open-Source Cloud-Plattform
- **IONOS Cloud** - Deutscher Anbieter
- **Open Telekom Cloud** - Deutsche Telekom
- **OVHcloud** - Europäischer Anbieter
- **plusserver** - Deutscher Hosting-Provider
- **gridscale** - Deutscher Cloud-Provider

### Government Clouds

- **Deutsche Verwaltungscloud (DVS)** - Für öffentliche Verwaltung
- **Bundes-Cloud** - Für Bundesbehörden
- **Landes-Rechenzentren** - Eigene RZ der Bundesländer

## Migration-Freiheit

Einfache Migration zwischen Umgebungen:

### Export

```bash
# Datenbank-Dump
pg_dump $URN_DB_URL > backup.sql

# Container-Images
docker save vcc-urn-resolver > vcc-urn.tar
```

### Import

```bash
# Auf neuem System
psql $URN_DB_URL < backup.sql
docker load < vcc-urn.tar
```

**Keine proprietären Datenformate!**

## Vermiedene Cloud-Lock-Ins

Folgende Cloud-spezifische Services werden **NICHT** verwendet:

### AWS (Amazon Web Services)
- ❌ Lambda (Serverless) → ✅ Stattdessen: Docker Container
- ❌ DynamoDB → ✅ Stattdessen: PostgreSQL / Redis
- ❌ ElastiCache → ✅ Stattdessen: Self-hosted Redis
- ❌ Cognito (IAM) → ✅ Stattdessen: Keycloak
- ❌ CloudWatch → ✅ Stattdessen: Prometheus + Grafana
- ❌ API Gateway → ✅ Stattdessen: FastAPI + Apollo Router

### Azure (Microsoft)
- ❌ Functions (Serverless) → ✅ Stattdessen: Docker Container
- ❌ Cosmos DB → ✅ Stattdessen: PostgreSQL
- ❌ Cache for Redis (Managed) → ✅ Stattdessen: Self-hosted Redis
- ❌ Active Directory B2C → ✅ Stattdessen: Keycloak + OIDC
- ❌ Application Insights → ✅ Stattdessen: Prometheus + Jaeger

### Google Cloud Platform (GCP)
- ❌ Cloud Functions → ✅ Stattdessen: Docker Container
- ❌ Cloud Spanner → ✅ Stattdessen: PostgreSQL
- ❌ Memorystore → ✅ Stattdessen: Self-hosted Redis
- ❌ Identity Platform → ✅ Stattdessen: Keycloak
- ❌ Cloud Monitoring → ✅ Stattdessen: Prometheus + Grafana

## Compliance & Datenschutz

### DSGVO-konform

- ✅ Daten verbleiben in Deutschland/EU
- ✅ Keine Datenübertragung an US-Anbieter
- ✅ Volle Kontrolle über Datenverarbeitung
- ✅ Audit-Logs für alle Zugriffe

### BSI-konform

- ✅ IT-Grundschutz-kompatibel
- ✅ Verschlüsselung (TLS 1.3, at-rest optional)
- ✅ Zugriffskontrolle (RBAC, mTLS)
- ✅ Logging & Monitoring

### Gaia-X-konform

- ✅ Datensouveränität gewährleistet
- ✅ Transparente Datenverarbeitung
- ✅ Europäische Werte (DSGVO, Digital Sovereignty)

## Zukunftssicherheit

### Langfristige Wartbarkeit

- ✅ Alle Abhängigkeiten sind Open-Source
- ✅ Standard-Technologien (Python, PostgreSQL, Redis)
- ✅ Große Communities (FastAPI, Kubernetes)
- ✅ Keine "Sunset"-Gefahr bei proprietären Services

### Unabhängigkeit

- ✅ Keine Lizenzkosten für Runtime
- ✅ Keine Abhängigkeit von Anbietern
- ✅ Freie Wahl des Hosting-Providers
- ✅ Interne Entwicklung möglich (Python-Skills)

## Empfehlungen für Bundesländer

### Deployment-Strategie

1. **Phase 1 (Test):**
   - Docker Compose in eigenem Rechenzentrum
   - SQLite oder lokales PostgreSQL

2. **Phase 2 (Pilot):**
   - Kubernetes in Landes-Rechenzentrum
   - PostgreSQL Cluster + Redis
   - 2-3 Bundesländer

3. **Phase 3 (Produktion):**
   - Kubernetes in DVS / Sovereign Cloud
   - PostgreSQL HA + Redis Cluster
   - Alle 16 Bundesländer

### Shared Infrastructure (optional)

Möglichkeit für gemeinsame Infrastruktur (Bund oder IT-Verbund):

- ✅ **Zentraler Gateway** (Apollo Router) - On-Premise beim Bund
- ✅ **Shared Monitoring** (Prometheus) - Föderal zugänglich
- ✅ **IAM Federation** (Keycloak) - Trust zwischen Ländern

**ABER:** Daten verbleiben bei den Ländern (Datensouveränität)!

## Checkliste: Vendor-Lock-In Vermeidung

- [x] Keine Cloud-spezifischen APIs (AWS/Azure/GCP)
- [x] Alle Komponenten Open-Source
- [x] Container-basiert (Docker/Kubernetes)
- [x] Standard-Protokolle (HTTP, GraphQL, OIDC)
- [x] Portable Datenformate (SQL, JSON)
- [x] Selbst hostbare Datenbanken (PostgreSQL, Redis)
- [x] Kein Vendor-spezifisches Monitoring (Prometheus statt CloudWatch)
- [x] Kein Vendor-spezifisches IAM (Keycloak statt Cognito/B2C)
- [x] Migration-ready (Export/Import ohne Vendor-Tools)

## Support & Community

- **GitHub Issues:** Community-Support
- **Dokumentation:** Vollständig Open-Source
- **Training:** Interne Schulung möglich (Python/FastAPI)
- **Kommerzieller Support:** Freie Wahl des Dienstleisters

---

**Fazit:** VCC-URN ist zu 100% on-premise deploybar, basiert auf Open-Source-Technologien und ist frei von jeglichem Vendor-Lock-In. Dies sichert langfristige Unabhängigkeit, Datensouveränität und Compliance mit deutschen/europäischen Anforderungen.

**Version:** 1.0  
**Stand:** 2025-11-23  
**Gültig für:** Alle Phasen (1, 2, 3)
