# Architecture Decision Record: Themis AQL als primäre VCC-native API

**Status:** Akzeptiert  
**Datum:** 2025-11-23  
**Aktualisiert:** 2025-11-25  
**Entscheidung:** Themis AQL als primäre VCC-native Query-Sprache, GraphQL als parallele API

---

## Kontext

Für Phase 2 und 3 der VCC-URN-Entwicklung wurde ursprünglich GraphQL (Apollo Federation) als einzige Query-Sprache für föderierte Abfragen geplant. Das VCC-Projekt hat jedoch mit **Themis AQL** eine eigene, speziell für föderale Verwaltungsstrukturen entwickelte Alternative.

## Entscheidung

**Wir bieten drei parallele APIs an:**

1. **REST API** (`/api/v1/*`) - Traditionelle REST-Endpunkte
2. **GraphQL API** (`/graphql`) - Flexible Query-Sprache
3. **Themis AQL** (`/aql`) - VCC-native Query-Sprache

Alle drei APIs sind vollständig unterstützt und können je nach Anwendungsfall gewählt werden.

## Begründung

### Vorteile von Themis AQL

1. **VCC-Ökosystem-Integration**
   - Themis ist Teil des VCC-Projekts
   - Native Integration mit Veritas (Graph-DB)
   - Einheitliche Query-Sprache über alle VCC-Komponenten

2. **Föderale Verwaltung**
   - Speziell für deutsche Verwaltungsstrukturen entwickelt
   - Berücksichtigt DSGVO und BSI-Anforderungen von Anfang an
   - Optimiert für 16-Bundesländer-Föderationsmodell

3. **Souveränität & Kontrolle**
   - Eigene Entwicklung (nicht von Apollo/US-Firma abhängig)
   - Volle Kontrolle über Spezifikation und Weiterentwicklung
   - Kann an deutsche/EU-Anforderungen angepasst werden

4. **On-Premise & Vendor-Freedom**
   - 100% Open-Source (Teil von ThemisDB)
   - Selbst hostbar
   - Keine externen Abhängigkeiten

### Vorteile von GraphQL

1. **Breite Adoption**
   - Bekannte Technologie mit großer Community
   - Umfangreiches Tooling (GraphiQL, Apollo Client, etc.)
   - Viele Entwickler haben Erfahrung damit

2. **Flexible Abfragen**
   - Client wählt benötigte Felder
   - Starke Typisierung mit Introspection
   - Gut für Frontend-Entwicklung

3. **Open-Source Implementation**
   - Strawberry GraphQL (MIT License)
   - Kein Vendor-Lock-In

## Konsequenzen

### Positiv

- ✅ Drei API-Optionen für verschiedene Anwendungsfälle
- ✅ VCC-native Integration über Themis AQL
- ✅ Bekannte Technologie (GraphQL) für externe Partner
- ✅ Einfache REST API für Basis-Operationen
- ✅ Keine Vendor-Lock-In-Risiken
- ✅ DSGVO & BSI-konform

### Negativ

- ⚠️ Drei APIs erfordern Wartung
- ⚠️ Dokumentation für drei APIs
- ⚠️ Themis AQL ist weniger bekannt als GraphQL

### Neutral

- 🔄 Entwickler wählen die passende API
- 🔄 GraphQL für externe Partner, Themis AQL für VCC-interne Systeme
- 🔄 REST für einfache Integrationen

## API-Empfehlungen

| Anwendungsfall | Empfohlene API |
|---------------|----------------|
| Einfache CRUD-Operationen | REST API |
| Frontend-Entwicklung | GraphQL |
| VCC-interne Systeme | Themis AQL |
| Veritas Graph-DB Integration | Themis AQL |
| Externe Partner | GraphQL oder REST |
| Batch-Operationen | Alle drei |

## Implementierung

### Phase 2 (Implementiert)

**GraphQL:**
- ✅ Strawberry GraphQL (MIT License)
- ✅ Endpunkt: `/graphql`
- ✅ GraphiQL Interface

**Themis AQL:**
- ✅ Themis AQL Parser/Executor Integration
- ✅ Endpunkt: `/aql`
- ✅ AQL-Schema für URN-Operationen

### Phase 3 (Implementiert)

**Federation:**
- ✅ Themis Federation Gateway für VCC-interne Föderation
- ✅ GraphQL für externe Partner verfügbar
- ✅ REST API bleibt als Basis-Option

## Referenzen

- Themis Projekt: (intern)
- VCC-Ökosystem: Veritas, Covina, Clara
- Verwandt: ThemisDB (Copyright-Inhaber)
- GraphQL: [graphql.org](https://graphql.org)
- Strawberry GraphQL: [strawberry.rocks](https://strawberry.rocks)

## Aktionen

- [x] GraphQL implementiert (Strawberry)
- [x] Themis AQL Client implementiert
- [x] REST API vollständig
- [x] Dokumentation aktualisiert
- [x] ADR dokumentieren (dieses Dokument)

---

**Autor:** VCC Development Team  
**Reviewer:** @makr-code  
**Status:** Akzeptiert
