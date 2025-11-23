# GraphQL API - EXPERIMENTAL / DEPRECATED

⚠️ **DEPRECATED: This GraphQL implementation is experimental and will be removed in future versions.**

## Status

**DEPRECATED in favor of Themis AQL**

See: [ADR-0001: Themis AQL statt GraphQL](../../docs/adr/0001-themis-aql-statt-graphql.md)

## Why Deprecated?

VCC has developed **Themis AQL** as the native query language for the VCC ecosystem. Themis AQL provides:

1. **VCC-native integration** with Veritas (Graph-DB), Covina, Clara
2. **Föderale Optimierung** specifically for German federal structures
3. **Souveränität** - VCC-owned, no dependency on external companies (Apollo)
4. **DSGVO & BSI compliance** by design
5. **On-premise & vendor-free** - 100% self-hostable

## Migration Path

**For new development:**
- Use **Themis AQL** API (planned for Phase 2b)
- Use **REST API** (`/api/v1/*`) for simple operations

**For existing GraphQL users:**
- GraphQL remains available for backward compatibility
- Plan migration to Themis AQL when it becomes available
- GraphQL may be removed in a future major version

## Current Status

- **GraphQL endpoint**: `/graphql` (if strawberry-graphql installed)
- **Availability**: Optional dependency with graceful degradation
- **Support level**: Experimental - use at your own risk
- **Removal timeline**: TBD (after Themis AQL implementation)

## Files

- `schema.py` - GraphQL type definitions (DEPRECATED)
- `resolvers.py` - GraphQL query/mutation resolvers (DEPRECATED)

## Alternatives

### REST API (Recommended for now)

```bash
# Generate URN
POST /api/v1/generate

# Resolve URN
GET /api/v1/resolve?urn=...

# Batch resolve
POST /api/v1/resolve/batch
```

### Themis AQL (Coming in Phase 2b)

```aql
# Resolve URN
QUERY resolveURN(urn: "urn:de:nrw:bimschg:anlage:...")

# Batch resolve
QUERY resolveBatch(urns: ["urn:de:nrw:...", "urn:de:by:..."])
```

## Support

For questions or migration assistance:
- See [ROADMAP.md](../../docs/ROADMAP.md) for Themis AQL timeline
- See [ADR-0001](../../docs/adr/0001-themis-aql-statt-graphql.md) for decision rationale
- Open an issue on GitHub for migration support

---

**Last Updated:** 2025-11-23  
**Deprecation Date:** 2025-11-23  
**Planned Removal:** TBD (after Themis AQL implementation)
