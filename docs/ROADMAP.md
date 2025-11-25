# VCC-URN Roadmap

**Aktueller Stand:** MVP mit Kernfunktionalität (90% feature-complete)  
**Ziel:** Produktionsreife föderale Infrastruktur für 16 Bundesländer

---

## 📍 Aktueller Status (November 2025)

### ✅ Implementiert
- URN-Generierung, Validierung, Auflösung (RFC 8141-konform)
- REST API v1 mit 5 Endpunkten
- Föderations-Basis (HTTP Peer-Resolver + TTL-Cache)
- Authentifizierung (API-Key + OIDC/JWT)
- Katalog-Management (global + landesspezifisch)
- Admin-API
- PostgreSQL/SQLite-Support
- Alembic-Migrationen
- 15 Tests (100% Pass-Rate)
- CI-Pipeline (GitHub Actions)

### ❌ Noch zu tun
- **Production Readiness:** Dockerfile, Prometheus, Structured Logging
- **Federation Evolution:** GraphQL-API, Redis-Cache, mTLS
- **Ecosystem Integration:** Föderations-Gateway, Saga-Pattern, 16-Länder-Rollout

---

## 🎯 3-Phasen-Strategie

### Phase 1: Production Hardening (3-4 Monate) – **Q4 2025 / Q1 2026**

**Ziel:** Produktionsreifes Deployment für einzelne Landesinstanzen

**Deliverables:**
- ✅ Dockerfile (Multi-Stage, Alpine-basiert, <100MB)
- ✅ Vollständige docker-compose.yml (App + Postgres + optional Redis)
- ✅ Kubernetes-Manifeste (Deployment, Service, ConfigMap, Secret, HPA)
- ✅ Prometheus `/metrics` Endpoint
- ✅ Structured Logging (JSON-Format)
- ✅ Circuit Breaker + Retry-Logic für Föderation
- ✅ Rate Limiting
- ✅ Test-Coverage >80%

**Priorität:** 🔴 HOCH (Blocker für Produktiveinsatz)

**Quick Wins (< 1 Monat):**
1. Dockerfile + docker-compose.yml (Woche 1-2)
2. Prometheus + Logging (Woche 3-4)

---

### Phase 2: Federation Evolution (4-6 Monate) – **Q2-Q3 2026**

**Ziel:** Erweiterung für Multi-Land-Szenarien (Pilot mit 2-3 Bundesländern)

**Deliverables:**
- ✅ **Themis AQL-API** - VCC-native Query-Sprache
- ✅ **GraphQL-API** - Flexible Query-Sprache (`/graphql`)
- ✅ Redis-basierter Cache (ersetzt In-Memory)
- ✅ **Mutual TLS (mTLS)** für Peer-Authentifizierung - konfigurierbar, on-premise
- ✅ Batch-Resolution-Endpoint (`/api/v1/resolve/batch`)
- ✅ **Admin-Dashboard** (Web-UI für Peer-Monitoring) - `/admin/dashboard`
- ✅ **Service Discovery** (Kubernetes DNS + Manual) - `vcc_urn/core/service_discovery.py`
- ✅ **Contract Testing** (Pact) - `vcc_urn/testing/contract_testing.py`

**Hinweis:** GraphQL und Themis AQL sind parallel verfügbar ([ADR-0001](adr/0001-themis-aql-statt-graphql.md))

**Priorität:** 🟡 MITTEL (für Pilot erforderlich)

**Erfolgskriterien:**
- Föderierte Auflösung über 3 Länder in <300ms (P95)
- Cache-Hit-Rate >70%
- Themis AQL-Query-Latenz <100ms (lokal)

---

### Phase 3: Föderiertes Ökosystem (6-12 Monate) – **2027**

**Ziel:** Vollständige Integration der 16 Bundesländer

**Deliverables:**
- ✅ **Themis Federation Gateway** (statt Apollo Router) - `vcc_urn/integrations/themis_gateway.py`
- ✅ **Themis Transactions / Saga-Orchestrator** - `vcc_urn/integrations/themis_transactions.py`
- ✅ **Themis AQL Client** - `vcc_urn/integrations/themis_aql.py`
- ✅ **Veritas Graph-DB Integration** - `vcc_urn/integrations/veritas.py`
- ✅ **Föderiertes IAM** (SAML 2.0 + SCIM) - `vcc_urn/core/federated_identity.py`
- ✅ **Open Policy Agent (OPA)** für zentrale RBAC - `vcc_urn/core/opa.py`
- ✅ **Distributed Tracing** (OpenTelemetry + Jaeger) - `vcc_urn/core/tracing.py`
- ⏳ 16 Bundesländer angebunden (Deployment-Phase)

**Priorität:** 🟢 NIEDRIG (langfristige Vision)

**Erfolgskriterien:**
- Föderierte AQL-Query über 5+ Länder in <2 Sekunden
- Gateway-Uptime >99.9%
- Saga-Success-Rate >99%

---

## 🛠️ Technologie-Stack (Evolution)

### Aktuell (Phase 1)
```
FastAPI → SQLAlchemy → PostgreSQL/SQLite
   ↓
httpx (Föderation) + Redis-Cache (optional, Fallback: In-Memory)
   ↓
API-Key/OIDC (Auth) + Circuit Breaker + Rate Limiting
```

### Phase 2 (Angepasst)
```
FastAPI + Themis AQL + GraphQL → Redis-Cache
   ↓
mTLS (Peer-Auth) + Circuit Breaker
   ↓
Admin-Dashboard (Web-UI)
```

**Hinweis:** Drei API-Optionen: REST, GraphQL, Themis AQL

### Phase 3 (Angepasst)
```
Themis Federation Gateway (statt Apollo Router) → 16 AQL-Endpunkte
   ↓
Themis Transactions / Temporal (Saga) + OPA (Policy) + OpenTelemetry (Tracing)
   ↓
Keycloak (SAML + SCIM) + Veritas Graph-DB Integration
```

**Wichtig:** Drei API-Optionen: REST, GraphQL, Themis AQL - alle on-premise, vendor-free (siehe [ADR-0001](adr/0001-themis-aql-statt-graphql.md))


---

## 📊 KPIs & Erfolgsmessung

| Metrik                          | Baseline | Phase 1 | Phase 2 | Phase 3 |
|---------------------------------|----------|---------|---------|---------|
| **Test-Coverage**               | ~60%     | 80%     | 85%     | 90%     |
| **API-Latenz (P95)**            | N/A      | <100ms  | <100ms  | <200ms  |
| **Deployment-Zeit**             | N/A      | <5 min  | <3 min  | <3 min  |
| **Uptime**                      | N/A      | 99%     | 99.5%   | 99.9%   |
| **Angebundene Bundesländer**    | 0        | 1       | 3       | 16      |
| **URNs generiert (kumulativ)**  | 0        | 10k     | 100k    | 1M+     |
| **Cache-Hit-Rate**              | 0%       | 50%     | 70%     | 80%     |

---

## 🚀 Quick Start (Next 30 Days)

### Woche 1-2: Deployment-Grundlagen
- [ ] Dockerfile erstellen (Multi-Stage Build, Alpine)
- [ ] docker-compose.yml erweitern (App-Service hinzufügen)
- [ ] Lokales Deployment testen

### Woche 3-4: Observability
- [ ] Prometheus-Integration (`prometheus-fastapi-instrumentator`)
- [ ] Structured Logging (python-json-logger, JSON-Format)
- [ ] Grafana-Dashboard (Basis-Metriken)

### Woche 5-6: Stabilität & Tests
- [ ] Circuit Breaker für Föderation (pybreaker)
- [ ] Test-Coverage erhöhen (Föderation, OIDC)
- [ ] K8s-Manifeste (Beispiele in `deployment/k8s/`)

**Deliverable Ende Monat 1:** Produktionsreifes Docker-Image + Deployment-Docs

---

## 🏛️ Governance & Organisation

### Föderales Governance-Modell

**Gremium:** KI-Föderationsrat VCC (zu gründen in Q1 2026)

**Zusammensetzung:**
- 1 Vertreter je Bundesland (16)
- 1 Bund-Vertreter (Koordination)
- 2 externe Experten

**Aufgaben:**
1. URN-Schema-Erweiterungen (neue Domänen/Objekttypen)
2. GraphQL-Schema-Evolution (API-Breaking-Changes koordinieren)
3. Datenschutz-Policies (DSGVO-konforme Löschkonzepte)
4. Budget & SLA-Definitionen

**Entscheidungsprozess:**
- Mehrheitsentscheidung (9 von 16 Stimmen)
- Konsensempfehlung für kritische Änderungen

### Open Source Strategie

**Lizenz:** MIT mit Government Clause (siehe `license.md`)

**Community:**
- Public Repository: https://github.com/makr-code/VCC-URN
- Issue-Tracking: GitHub Issues
- Roadmap: GitHub Projects
- Contributor-Guidelines: `CONTRIBUTING.md` (to be created)

---

## 🎓 Best Practices & Leitprinzipien

### Architektur
1. ✅ **Twelve-Factor App** (Konfiguration via ENV, Stateless, Logs als Streams)
2. ✅ **Clean Architecture** (Schichtenmodell, DDD)
3. ✅ **API-First Design** (Schema als Vertrag)

### Security
1. ✅ **Zero-Trust** (Mutual TLS, jede Anfrage authentifiziert)
2. ✅ **Secret Management** (Vault/K8s Secrets, Rotation)
3. ✅ **Data Protection** (TLS 1.3, Encryption at Rest, DSGVO-Compliance)

### Testing
1. ✅ **Test-Pyramide** (70% Unit, 25% Integration, 5% E2E)
2. ✅ **Contract Testing** (Phase 2: Pact für API-Verträge)
3. ✅ **Performance Testing** (Ziel: 1000 RPS bei <100ms)

### Dokumentation
1. ✅ **Living Documentation** (OpenAPI/GraphQL Schema)
2. ✅ **Architecture Decision Records** (ADRs in `docs/adr/`)
3. ✅ **Runbooks** (Deployment, Incident Response)

---

## 🔗 Integration mit VCC-Ökosystem

### VCC-Komponenten
- **Veritas (Graph-DB):** URNs als Property in Knoten, Proxy-Knoten für externe Referenzen
- **Covina (Ingestion):** URN-Generierung bei Dokumenten-Erfassung
- **Clara (LLM/RAG):** Föderierte Wissensbasis via URN-Auflösung

### Integrationspunkte
1. Covina → VCC-URN: `POST /api/v1/generate` (bei File Scanner Worker)
2. Veritas → VCC-URN: `GET /api/v1/resolve?urn=...` (bei Graph-Traversal)
3. Clara → VCC-URN: GraphQL-Query (Phase 2, föderierter Kontext)

---

## 📚 Weiterführende Dokumentation

- **[Vollständige Strategie](./development-strategy.md)** – Detaillierte 3-Phasen-Planung
- **[TODO & Gap-Analyse](./TODO.md)** – Identifizierte Lücken und Prioritäten
- **[Strategische Vision](./introducing.md)** – Föderierte Graph-RAG-Architektur
- **[URN-Spezifikation](./urn-spec.md)** – Technische Referenz
- **[Complete Guide](./complete-guide.md)** – API-Referenz & Setup

---

## 📞 Kontakt & Support

**Projekt-Homepage:** https://github.com/makr-code/VCC-URN

**Support-Kanäle:**
- Issues: GitHub Issues
- Diskussionen: GitHub Discussions

**Nächste Schritte:**
1. Review dieser Roadmap mit Stakeholdern
2. Priorisierung der Quick Wins (Dockerfile, Prometheus)
3. Planung des Governance-Kick-offs (Q1 2026)

---

**Letzte Aktualisierung:** 2025-11-23  
**Version:** 1.0
