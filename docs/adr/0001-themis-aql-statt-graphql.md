# Architecture Decision Record: Themis AQL statt GraphQL

**Status:** Akzeptiert  
**Datum:** 2025-11-23  
**Entscheidung:** Verwendung von Themis AQL anstelle von GraphQL für föderierte Abfragen

---

## Kontext

Für Phase 2 und 3 der VCC-URN-Entwicklung wurde ursprünglich GraphQL (Apollo Federation) als Query-Sprache für föderierte Abfragen geplant. Das VCC-Projekt hat jedoch mit **Themis AQL** eine eigene, speziell für föderale Verwaltungsstrukturen entwickelte Alternative.

## Entscheidung

**Wir verwenden Themis AQL anstelle von GraphQL** für alle föderierten Abfragen und die Query-API.

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

### Nachteile von GraphQL (die AQL vermeidet)

1. **Vendor-Abhängigkeit**
   - Apollo Federation ist kommerzielles Produkt (Elastic License 2.0)
   - Router hat Einschränkungen in freier Version
   - Mögliche zukünftige Lizenzänderungen (wie bei Elasticsearch)

2. **Komplexität**
   - GraphQL Federation erfordert komplexes Setup
   - N+1-Problem erfordert DataLoader-Pattern
   - Steile Lernkurve

3. **Nicht VCC-nativ**
   - Externe Technologie, nicht auf VCC-Bedürfnisse zugeschnitten
   - Zusätzlicher Integrationsaufwand

## Konsequenzen

### Positiv

- ✅ Einheitliche Query-Sprache im gesamten VCC-Ökosystem
- ✅ Bessere Integration mit Veritas, Covina, Clara
- ✅ Volle Kontrolle über Spezifikation
- ✅ Optimiert für föderale Verwaltungsstrukturen
- ✅ Keine Vendor-Lock-In-Risiken
- ✅ DSGVO & BSI-konform by design

### Negativ

- ⚠️ Themis AQL ist weniger bekannt als GraphQL
- ⚠️ Kleinere Community (VCC-fokussiert)
- ⚠️ Weniger Tooling-Unterstützung (noch)

### Neutral

- 🔄 GraphQL-Implementierung bleibt optional verfügbar (backward compatibility)
- 🔄 Migration von REST zu AQL (statt zu GraphQL)
- 🔄 Dokumentation muss aktualisiert werden

## Implementierung

### Phase 2 (Angepasst)

**Statt GraphQL:**
- ❌ ~~Strawberry GraphQL~~
- ❌ ~~Apollo Federation~~

**Mit Themis AQL:**
- ✅ Themis AQL Parser/Executor Integration
- ✅ AQL-Endpunkt: `/aql` oder `/api/v2/aql`
- ✅ AQL-Schema für URN-Operationen
- ✅ Föderation via Themis Query Routing

### Phase 3 (Angepasst)

**Statt Apollo Router:**
- ❌ ~~Apollo Router (Gateway)~~

**Mit Themis:**
- ✅ Themis Federation Gateway
- ✅ AQL Query Federation über 16 Bundesländer
- ✅ Themis-basierte Transaktionen (statt Saga-Pattern)

## Alternative erwogen

**GraphQL (Apollo Federation)** wurde erwogen, aber aus oben genannten Gründen zugunsten von Themis AQL verworfen.

## Referenzen

- Themis Projekt: (intern)
- VCC-Ökosystem: Veritas, Covina, Clara
- Verwandt: ThemisDB (Copyright-Inhaber)

## Aktionen

- [x] GraphQL als optional belassen (bereits implementiert)
- [ ] Themis AQL Integration planen (Phase 2b)
- [ ] Dokumentation aktualisieren (development-strategy.md, ROADMAP.md)
- [x] ADR dokumentieren (dieses Dokument)
- [ ] Team informieren

---

**Autor:** VCC Development Team  
**Reviewer:** @makr-code  
**Status:** Akzeptiert
