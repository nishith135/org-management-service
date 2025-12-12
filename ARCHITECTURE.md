# Architecture Documentation

## System Overview

This is a multi-tenant organization management API built with FastAPI and MongoDB. The system provides secure organization management with isolated data per tenant.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  (Swagger UI, cURL, Postman, Frontend Applications)         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    FastAPI Application                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              app/main.py                              │  │
│  │  - FastAPI app initialization                         │  │
│  │  - CORS middleware                                    │  │
│  │  - Router registration                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────┼──────────────────────────────────┐ │
│  │                      │                                  │ │
│  │  ┌───────────────────▼───────────────────┐             │ │
│  │  │      API Routes (app/api/v1/)        │             │ │
│  │  │  ┌──────────────┐  ┌──────────────┐ │             │ │
│  │  │  │ admin_routes │  │  org_routes  │ │             │ │
│  │  │  │  /admin/login│  │  /org/*      │ │             │ │
│  │  │  └──────┬───────┘  └──────┬───────┘ │             │ │
│  │  └─────────┼─────────────────┼─────────┘             │ │
│  │            │                 │                         │ │
│  │  ┌─────────▼─────────────────▼─────────┐             │ │
│  │  │   Authentication (app/auth/)         │             │ │
│  │  │   - OAuth2PasswordBearer             │             │ │
│  │  │   - get_current_admin()              │             │ │
│  │  └──────────────────────────────────────┘             │ │
│  │            │                                           │ │
│  │  ┌─────────▼───────────────────────────┐             │ │
│  │  │   Business Logic (app/services/)     │             │ │
│  │  │   - auth_service.py                 │             │ │
│  │  │   - org_service.py                  │             │ │
│  │  └──────────────────────────────────────┘             │ │
│  │            │                                           │ │
│  │  ┌─────────▼───────────────────────────┐             │ │
│  │  │   Data Models (app/models/)         │             │ │
│  │  │   - Request models (Pydantic)       │             │ │
│  │  │   - Domain models                   │             │ │
│  │  └──────────────────────────────────────┘             │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Async Motor Driver
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    MongoDB Database                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              org_master_db                            │  │
│  │  ┌──────────────────┐  ┌──────────────────┐        │  │
│  │  │  organizations   │  │     admins       │        │  │
│  │  │  - _id           │  │  - _id          │        │  │
│  │  │  - org_name      │  │  - email        │        │  │
│  │  │  - collection    │  │  - org_id       │        │  │
│  │  └──────────────────┘  │  - password     │        │  │
│  │                         └──────────────────┘        │  │
│  │                                                       │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │  Tenant Collections (Dynamic)                │   │  │
│  │  │  org_acme_corp, org_example_inc, etc.       │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Multi-Tenant Design

### Collection-Based Isolation

Each organization gets its own MongoDB collection named using the pattern: `org_{slugified_organization_name}`.

**Example:**

- Organization: "Acme Corp" → Collection: `org_acme_corp`
- Organization: "Example Inc" → Collection: `org_example_inc`

### Master Database Structure

The `org_master_db` database contains:

1. **`organizations` Collection**: Metadata for all organizations

   ```json
   {
     "_id": ObjectId("..."),
     "organization_name": "Acme Corp",
     "collection_name": "org_acme_corp",
     "created_at": ISODate("..."),
     "updated_at": ISODate("...")
   }
   ```

2. **`admins` Collection**: Admin user accounts linked to organizations

   ```json
   {
     "_id": ObjectId("..."),
     "email": "admin@acme.com",
     "organization_id": "507f1f77bcf86cd799439011",
     "hashed_password": "$2b$12$...",
     "is_active": true,
     "created_at": ISODate("..."),
     "updated_at": ISODate("...")
   }
   ```

3. **Tenant Collections**: Dynamic collections for each organization's data

### Data Flow

1. **Organization Creation**:

   - Create entry in `organizations` collection
   - Generate collection name (slugified)
   - Create admin account in `admins` collection
   - Link admin to organization via `organization_id`

2. **Authentication**:

   - Admin logs in with email/password
   - System verifies credentials against `admins` collection
   - JWT token generated with `sub` (admin ID), `email`, and `organization_id`

3. **Data Access**:
   - JWT token contains `organization_id`
   - Service layer uses `organization_id` to determine tenant collection
   - All operations scoped to specific organization's collection

## Component Responsibilities

### API Routes (`app/api/v1/`)

- Handle HTTP requests/responses
- Validate request models
- Call service layer
- Return standardized responses

### Services (`app/services/`)

- Business logic
- Database operations
- Data transformation
- Error handling

### Models (`app/models/`)

- Request validation (Pydantic)
- Domain models
- Response models

### Authentication (`app/auth/`)

- OAuth2 token validation
- JWT decoding
- Admin authorization

### Database (`app/db/`)

- MongoDB connection management
- Database initialization
- Connection pooling

## Security Architecture

### Authentication Flow

```
1. Client → POST /admin/login (email, password)
2. Server → Verify credentials in admins collection
3. Server → Generate JWT with claims (sub, email, organization_id)
4. Server → Return access_token
5. Client → Include token in Authorization: Bearer <token>
6. Server → Validate token via get_current_admin()
7. Server → Extract organization_id from token
8. Server → Scope operations to tenant collection
```

### Token Structure

```json
{
  "sub": "admin_id",
  "email": "admin@example.com",
  "organization_id": "org_id",
  "type": "admin",
  "exp": 1234567890
}
```

## Trade-offs and Design Decisions

### Collection-Based vs Database-Based Multi-Tenancy

**Chosen: Collection-Based**

- **Pros**:
  - Simpler to implement
  - Easy data migration per tenant
  - Can scale individual collections
  - Clear data isolation
- **Cons**:
  - Collection limit per database (MongoDB default: ~24,000)
  - Slightly more complex queries (need collection name)

**Alternative: Database-Based**

- **Pros**: Complete isolation, easier backup/restore per tenant
- **Cons**: More complex connection management, harder to scale

### Async Architecture

**Chosen: Async/Await with Motor**

- **Pros**: High concurrency, non-blocking I/O, better performance
- **Cons**: Slightly more complex error handling

### JWT vs Session-Based Auth

**Chosen: JWT**

- **Pros**: Stateless, scalable, works well with microservices
- **Cons**: Token revocation requires additional mechanism

## Scalability Considerations

1. **Horizontal Scaling**: Stateless API servers can be scaled horizontally
2. **Database Sharding**: MongoDB sharding can be applied to tenant collections
3. **Caching**: Redis can be added for token caching and rate limiting
4. **Load Balancing**: Multiple API instances behind a load balancer

## Deployment Architecture

```
┌─────────────┐
│   Load      │
│  Balancer   │
└──────┬──────┘
       │
   ┌───┴───┬─────────┬─────────┐
   │       │         │         │
┌──▼──┐ ┌──▼──┐   ┌──▼──┐   ┌──▼──┐
│ API │ │ API │   │ API │   │ API │
│  1  │ │  2  │   │  3  │   │  N  │
└──┬──┘ └──┬──┘   └──┬──┘   └──┬──┘
   │       │         │         │
   └───────┴─────────┴─────────┘
              │
       ┌──────▼──────┐
       │  MongoDB    │
       │  Replica    │
       │    Set      │
       └─────────────┘
```
