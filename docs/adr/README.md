# README: Architecture Decision Records (ADRs)

Dieses Verzeichnis enthält Architecture Decision Records (ADRs) für wichtige technologische und architektonische Entscheidungen im VCC-URN-Projekt.

## Was sind ADRs?

Architecture Decision Records dokumentieren wichtige Entscheidungen mit:
- **Kontext**: Warum mussten wir entscheiden?
- **Entscheidung**: Was haben wir beschlossen?
- **Konsequenzen**: Was sind die Auswirkungen?
- **Alternativen**: Was haben wir erwogen und warum verworfen?

## Index

### ADR-0001: Themis AQL statt GraphQL

**Datum:** 2025-11-23  
**Status:** Akzeptiert  
**Datei:** [0001-themis-aql-statt-graphql.md](./0001-themis-aql-statt-graphql.md)

**Zusammenfassung:**
VCC verwendet **Themis AQL** anstelle von GraphQL für föderierte Abfragen. Dies bietet:
- VCC-Ökosystem-Integration (Veritas, Covina, Clara)
- Souveränität (keine Apollo/US-Abhängigkeit)
- DSGVO & BSI-konform by design
- On-Premise & vendor-free

**Auswirkungen:**
- Phase 2: Themis AQL statt Strawberry GraphQL
- Phase 3: Themis Federation Gateway statt Apollo Router
- GraphQL bleibt optional verfügbar (experimentell)

---

## Format

ADRs folgen diesem Format:

```markdown
# ADR-XXXX: Titel der Entscheidung

**Status:** [Vorgeschlagen | Akzeptiert | Abgelehnt | Überholt]
**Datum:** YYYY-MM-DD
**Entscheidung:** Kurze Zusammenfassung

## Kontext
Warum müssen wir entscheiden?

## Entscheidung
Was haben wir beschlossen?

## Begründung
Warum haben wir so entschieden?

## Konsequenzen
Was sind die Auswirkungen?

## Alternativen
Was haben wir erwogen und warum verworfen?
```

## Weitere ADRs (geplant)

- ADR-0002: Postgres vs. andere Datenbanken
- ADR-0003: Redis vs. Memcached für Caching
- ADR-0004: Keycloak vs. andere IAM-Lösungen
- ADR-0005: OPA vs. andere Policy Engines

---

**Hinweis:** ADRs sind unveränderlich. Wenn eine Entscheidung geändert wird, erstelle einen neuen ADR, der den alten überholt.
