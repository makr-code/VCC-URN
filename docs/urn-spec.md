# URN-Spezifikation (VCC-URN)

Diese Spezifikation orientiert sich an RFC 2141/8141 und der strategischen Doku. Sie legt das Format und die Validierung für föderale URNs fest.

## Syntax

```
urn:de:<state>:<domain>:<obj_type>:<local_aktenzeichen>:<uuid>[:<version>]
```

- `urn` – Präfix
- `de` – NID (Namespace Identifier), konfigurierbar über `URN_NID` (Default: `de`) und zur Laufzeit erzwungen
- `<state>` – Länderkürzel, 2–3 Zeichen, Kleinbuchstaben; Regex per `URN_STATE_RE` konfiguriert (Default: `^[a-z]{2,3}$`)
- `<domain>` – Fachdomäne (z. B. `bimschg`, `bau`), Kleinbuchstaben/Ziffern/Bindestrich
- `<obj_type>` – Objekttyp (z. B. `anlage`, `bescheid`, `gutachten`), Kleinbuchstaben/Ziffern/Bindestrich
- `<local_aktenzeichen>` – lokales Aktenzeichen, URL-kodiert (RFC3986 safe subset)
- `<uuid>` – RFC 4122 UUID (36 Zeichen, z. B. `8-4-4-4-12` hex)
- `:<version>` – optional, Format `v[0-9A-Za-z-.]+`

Beispiel:

```
urn:de:nrw:bimschg:anlage:4711-0815-K1:6e8bc430-9c3a-11d9-9669-0800200c9a66
```

## Validierung

- Parser prüft:
  - Grundmuster (Regex) für Struktur und erlaubte Zeichen
  - NID == `settings.nid`
  - `state` passt auf `settings.state_pattern`
  - Optionale Kataloge:
    - Global: `URN_ALLOWED_DOMAINS` und `URN_ALLOWED_OBJ_TYPES` (Komma-separiert)
    - Landes-spezifisch: `URN_CATALOGS_JSON` im Format `{ "<state>": { "domains": [...], "obj_types": [...] } }`
      – Falls für ein Land Einträge vorhanden sind, haben diese Vorrang vor den globalen Listen.
- `local_aktenzeichen` wird beim Parsen URL-dekodiert zurückgegeben

## Generierung

- `URN.generate(...)` normalisiert `state`, `domain`, `obj_type` zu Kleinbuchstaben, kodiert `local_aktenzeichen` URL-sicher und erzeugt eine UUID, sofern nicht vorgegeben.
- Die NID wird aus `settings.nid` bezogen, kann optional überschrieben werden.

## API-Vertrag (Auszug)

- `POST /api/v1/generate` – erzeugt eine URN (optional speichert ein Manifest)
- `POST /api/v1/validate` – prüft eine URN gegen obige Regeln und gibt Komponenten zurück
- `GET /api/v1/resolve?urn=...` – liefert Manifest oder minimalen Stub

## Föderation

- Die URN ist global eindeutig und dient als Referenz über Landes- und Systemgrenzen. Bei `resolve` wird bei Bedarf die zuständige Landesinstanz kontaktiert (konfigurierbare Peers) und das Ergebnis lokal gecached.

## Erweiterungen (Optionen)

- Kataloge für `domain`/`obj_type` können zentral gepflegt werden, global oder landesspezifisch (siehe oben). 
- Versionierungsregeln (z. B. semver-ähnlich) können präzisiert werden; derzeit freie Zeichen gemäß Schema `v...`.
