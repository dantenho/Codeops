# CodeAgents Functions by Workspace

## agents/ (Agents Workspace)

### Agent Orchestration
- Agent lifecycle management
- Task distribution
- Workflow execution
- Agent communication

### Memory Integration
- Memory store integration
- Context management
- State persistence
- Cache management

### Vector Store
- Embedding generation
- Vector indexing
- Semantic search
- Similarity retrieval

**Branch**: `workspace/agents`  
**Dependencies**: `shared/database`, `shared/api-calls`

---

## backend/ (Backend Workspace)

### API Endpoints
- REST API routes
- Request handlers
- Response formatting
- Error handling

### Data Processing
- Data validation
- Transformation
- Aggregation
- Analytics

### Service Integration
- Third-party APIs
- Database queries
- Cache operations
- Message queues

**Branch**: `workspace/backend`  
**Dependencies**: `shared/database`, `shared/api-calls`

---

## frontend/ (Frontend Workspace)

### UI Components
- React/Vue components
- Component library
- Styling
- Accessibility

### State Management
- Store management
- State persistence
- Context providers
- Redux/Pinia

### API Integration
- API client
- Request handling
- Response parsing
- Error handling

**Branch**: `workspace/frontend`  
**Dependencies**: `shared/api-calls`

---

## database/ (Shared - Database)

### Schema Management
- Table definitions
- Column constraints
- Indexes
- Foreign keys

### Migrations
- Schema versions
- Upgrade scripts
- Rollback procedures
- Data migrations

### Data Models
- ORM definitions
- Entity relationships
- Validation rules
- Serialization

**Branch**: `shared/database`  
**Syncs To**: `workspace/agents`, `workspace/backend`

---

## hub/ (Shared - API Calls)

### Endpoint Definitions
- Route specifications
- HTTP methods
- Request/response schemas
- Status codes

### Authentication
- JWT tokens
- OAuth2
- API keys
- Session management

### Request Validation
- Input validation
- Type checking
- Business logic validation
- Rate limiting

**Branch**: `shared/api-calls`  
**Syncs To**: `workspace/agents`, `workspace/backend`, `workspace/frontend`

---

## Other Directories

### nodes/
**Part of**: `workspace/agents`  
Node definitions and implementations for agent workflows

### packages/
**Part of**: `workspace/backend`  
Shared packages and utilities

### docs/
**Independent**, merged to all  
Documentation and specifications

### config/
**Independent**, merged to all  
Configuration files and environment setup

### bin/
**Independent**, merged to all  
Scripts and command-line tools

### workflows/
**Part of**: `workspace/agents`  
Workflow definitions and orchestration

### organizator/
**Part of**: `workspace/backend`  
Organization and data management

### market_analysis/
**Specialized**, merged to relevant workspaces  
Market analysis tools and data processing

---

## Function Dependencies

```
frontend/
  └─ shared/api-calls

backend/
  ├─ shared/database
  └─ shared/api-calls

agents/
  ├─ shared/database
  └─ shared/api-calls

main/ (production)
  ├─ agents
  ├─ backend
  └─ frontend
```

## Adding New Functions

### To workspace/agents
1. Create in `agents/` or `nodes/`
2. Test on `workspace/agents`
3. If needs DB: update `shared/database`
4. If needs API: update `shared/api-calls`
5. Merge to `workspace/agents`
6. Release to main

### To workspace/backend
1. Create in `backend/` or `packages/`
2. Test on `workspace/backend`
3. If needs DB: update `shared/database`
4. If needs API: update `shared/api-calls`
5. Merge to `workspace/backend`
6. Release to main

### To workspace/frontend
1. Create in `frontend/` or `frontend_prototype/`
2. Test on `workspace/frontend`
3. If needs API: update `shared/api-calls`
4. Merge to `workspace/frontend`
5. Release to main

### To shared/database
1. Create schema in `database/`
2. Create migration file
3. Update ORM definitions
4. Test on `shared/database`
5. Merge
6. Sync to `workspace/agents` and `workspace/backend`

### To shared/api-calls
1. Define endpoint in `hub/`
2. Add validation rules
3. Document contract
4. Test on `shared/api-calls`
5. Merge
6. Sync to all workspaces
