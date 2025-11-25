# GraphQL API

GraphQL API for VCC-URN - Available alongside REST and Themis AQL APIs.

## Status

**✅ SUPPORTED** - GraphQL is a fully supported API for VCC-URN.

## API Options

VCC-URN provides three API options:

1. **REST API** (`/api/v1/*`) - Traditional REST endpoints
2. **GraphQL API** (`/graphql`) - Flexible query language (this API)
3. **Themis AQL** (`/aql`) - VCC-native query language

Choose the API that best fits your use case.

## Features

GraphQL provides:

1. **Flexible queries** - Request only the fields you need
2. **Strong typing** - Type-safe API with introspection
3. **Single endpoint** - All operations via `/graphql`
4. **GraphiQL interface** - Interactive API explorer
5. **Open-Source** - Strawberry GraphQL (MIT License)

## Installation

GraphQL is optional. Install with:

```bash
pip install strawberry-graphql[fastapi]
```

## Endpoint

- **GraphQL endpoint**: `/graphql`
- **GraphiQL interface**: Available at `/graphql` in browser

## Operations

### Queries

```graphql
# Resolve a URN
query {
  resolveUrn(urn: "urn:de:nrw:bimschg:anlage:...") {
    urn
    manifestJson
    createdAt
    updatedAt
  }
}

# Validate a URN
query {
  validateUrn(urn: "urn:de:nrw:bimschg:anlage:...") {
    valid
    reason
    components {
      nid
      state
      domain
      objType
      localAktenzeichen
      uuid
      version
    }
  }
}

# Search by UUID
query {
  searchByUuid(uuid: "abc123", limit: 10, offset: 0) {
    urn
    manifestJson
  }
}

# Batch resolve multiple URNs
query {
  resolveBatch(urns: ["urn:de:nrw:...", "urn:de:by:..."]) {
    urn
    manifestJson
  }
}
```

### Mutations

```graphql
# Generate a new URN
mutation {
  generateUrn(input: {
    state: "nrw"
    domain: "bimschg"
    objType: "anlage"
    localAktenzeichen: "2024-001"
    store: true
  }) {
    urn
    components {
      nid
      state
      domain
      objType
      localAktenzeichen
      uuid
    }
  }
}

# Store a manifest
mutation {
  storeManifest(
    urn: "urn:de:nrw:bimschg:anlage:..."
    manifest: { title: "Example", data: "..." }
  ) {
    urn
    manifestJson
  }
}
```

## Files

- `schema.py` - GraphQL type definitions
- `resolvers.py` - GraphQL query/mutation resolvers

## See Also

- [REST API Documentation](/api/v1/docs)
- [Themis AQL Documentation](/aql/docs)
- [ROADMAP.md](../../docs/ROADMAP.md)

---

**Last Updated:** 2025-11-25
