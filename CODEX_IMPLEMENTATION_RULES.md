# ClaimPilot Engineering Handbook
## Codex Implementation Rules & Architecture Guide

**Version:** 1.0  
**Last Updated:** June 29, 2026  
**Status:** Architecture Frozen — Implementation Phase

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Current Project Status](#2-current-project-status)
3. [Technology Stack](#3-technology-stack)
4. [Folder Structure](#4-folder-structure)
5. [Architecture Rules](#5-architecture-rules)
6. [Dependency Injection Rules](#6-dependency-injection-rules)
7. [Database Clients](#7-database-clients)
8. [Security Rules](#8-security-rules)
9. [Coding Standards](#9-coding-standards)
10. [API Standards](#10-api-standards)
11. [Error Handling](#11-error-handling)
12. [Service Layer Rules](#12-service-layer-rules)
13. [Router Rules](#13-router-rules)
14. [AI Agent Architecture](#14-ai-agent-architecture)
15. [OCR Pipeline](#15-ocr-pipeline)
16. [Storage Architecture](#16-storage-architecture)
17. [Future Modules](#17-future-modules)
18. [Testing Standards](#18-testing-standards)
19. [Git Workflow](#19-git-workflow)
20. [Codex Rules](#20-codex-rules)
21. [Development Workflow](#21-development-workflow)
22. [Feature Roadmap](#22-feature-roadmap)
23. [Definition of Done](#23-definition-of-done)
24. [Final Engineering Principles](#24-final-engineering-principles)

---

## 1. Project Overview

### What is ClaimPilot?

ClaimPilot is an **AI-powered insurance and warranty claims processing platform** designed to automate and accelerate the claims submission workflow for both insurers and customers.

### Business Problem Solved

Manual claims processing is slow, error-prone, and resource-intensive. ClaimPilot uses AI agents to intelligently extract claim information, validate policy eligibility, gather required evidence, and generate submission-ready packets—reducing processing time from weeks to hours.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│               Flutter Mobile Frontend                    │
│         (Authentication, Claim Creation, Upload)         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼ (REST API)
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                    │
│         (Business Logic, AI Orchestration, RLS)          │
└──────┬──────────────────────────────┬───────────────────┘
       │                              │
       ▼                              ▼
┌──────────────────┐      ┌──────────────────────┐
│  Supabase Auth   │      │  PostgreSQL + RLS    │
│   (JWT Tokens)   │      │   (Data Persistence) │
└──────────────────┘      └──────────────────────┘
       │                              │
       └──────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  Supabase Storage (Document Repository)                 │
└─────────────────────────────────────────────────────────┘
              │
              ▼
┌──────────────────────────────┬──────────────────────────┐
│  Groq API (AI Processing)    │  Google ADK (Agents)     │
│  (LLM Inference)             │  (Orchestration)         │
└──────────────────────────────┴──────────────────────────┘
```

### Business Workflow

1. **Claim Creation** - User registers, logs in, initiates new claim
2. **Document Upload** - User uploads policy, receipts, photos, evidence
3. **OCR Processing** - System extracts text from images and documents
4. **AI Intake Agent** - Asks clarifying questions, gathers missing information
5. **AI Policy Agent** - Validates claim eligibility against policy document
6. **AI Evidence Agent** - Evaluates supporting documentation
7. **AI Submission Agent** - Assembles final submission packet
8. **PDF Generation** - Creates submission-ready document
9. **Submission** - User downloads or auto-submits to insurance company

### Technology Enablers

| Component | Purpose |
|-----------|---------|
| **Groq API** | Fast LLM inference for intelligent claim analysis |
| **Google ADK** | Orchestrates multi-agent AI workflow |
| **OCR** | Extracts text from documents and images |
| **PDF Generation** | Creates submission-ready documents |
| **Supabase RLS** | Row-level security ensures user data isolation |

---

## 2. Current Project Status

### ✅ Infrastructure Complete

The backend is **production-ready** in terms of architecture. All foundational systems are in place and frozen.

#### Completed Components

- ✅ **FastAPI Framework** - API server, routing, middleware
- ✅ **Project Structure** - Organized, modular, scalable layout
- ✅ **Configuration System** - Environment variables, settings management
- ✅ **Dependency Injection** - FastAPI Depends() throughout application
- ✅ **Service Layer** - Business logic encapsulated in services
- ✅ **Thin Routers** - Routes only validate, inject, call services, return responses
- ✅ **Middleware** - JWT extraction, authentication validation
- ✅ **JWT Authentication** - Supabase Auth integration
- ✅ **Supabase Integration** - Database and auth clients
- ✅ **PostgreSQL Schema** - Database structure with RLS
- ✅ **Storage Setup** - Document repository infrastructure
- ✅ **Row Level Security** - User data isolation enforced at DB level
- ✅ **Admin Client** - `get_admin_client()` for system operations
- ✅ **User Client** - `get_user_client(jwt)` for RLS-protected operations
- ✅ **Exception Hierarchy** - Custom exception types for proper error handling
- ✅ **Response Wrapper** - Standardized API response format

### 🔒 Architecture Frozen

**The backend architecture is frozen.** Do not redesign, refactor, or restructure without explicit approval. All future work is feature implementation only.

---

## 3. Technology Stack

### Core Framework
- **Python 3.14** - Language runtime
- **FastAPI 0.138+** - Web framework, REST API
- **Uvicorn** - ASGI application server

### Database & Auth
- **Supabase** - Backend-as-a-Service platform
- **PostgreSQL 15+** - Primary data store
- **Supabase Auth** - User authentication, JWT management
- **Row Level Security (RLS)** - Fine-grained access control

### Data & Validation
- **Pydantic** - Data validation, serialization
- **SQLAlchemy** (future) - Optional ORM for complex queries

### AI & Processing
- **Groq** - Fast LLM API for claim analysis
- **Google Agent Development Kit (ADK)** - Multi-agent orchestration
- **Python-OCR** (future) - Document text extraction

### Frontend
- **Flutter** - Mobile-first cross-platform client
- **REST API** - Communication protocol

### Development & DevOps
- **GitHub Actions** (future) - CI/CD pipeline
- **Docker** (future) - Containerization

### Libraries
- **python-dotenv** - Environment configuration
- **passlib** - Password hashing
- **bcrypt** - Cryptographic operations
- **httpx** - Async HTTP client
- **email-validator** - Email validation

---

## 4. Folder Structure

### Root-Level Organization

```
claimiac/backend/
├── app/                           # Main application package
│   ├── __init__.py
│   ├── config.py                  # Configuration loading
│   ├── main.py                    # FastAPI app initialization
│   ├── api/                       # API routes
│   ├── core/                      # Core infrastructure
│   ├── database/                  # Database clients & dependencies
│   ├── middleware/                # Request/response middleware
│   ├── schemas/                   # Pydantic models
│   ├── services/                  # Business logic layer
│   ├── agents/                    # AI agents (Groq + ADK)
│   ├── skills/                    # Agent skills/tools
│   ├── tools/                     # Utility tools & helpers
│   ├── exceptions/                # Custom exception classes
│   ├── models/                    # Domain models (ORM ready)
│   ├── constants/                 # Application constants
│   ├── utils/                     # Utility functions
│   └── tests/                     # Unit tests
├── migrations/                    # SQL schema migrations
├── requirements.txt               # Python dependencies
└── CODEX_IMPLEMENTATION_RULES.md # This engineering guide
```

### Folder Responsibilities

| Folder | Owner | Responsibility |
|--------|-------|-----------------|
| `api/` | Routes | HTTP endpoints, parameter validation, response formatting |
| `services/` | Business Logic | Claims, users, documents, AI orchestration |
| `database/` | Data Access | Supabase clients, connection management, dependencies |
| `middleware/` | Infrastructure | JWT validation, request/response processing |
| `schemas/` | Contracts | Request/response models, validation rules |
| `agents/` | AI | Groq-powered agents, ADK orchestration |
| `core/` | Infrastructure | Settings, security, CORS, logging |
| `exceptions/` | Error Handling | Custom exception types |
| `utils/` | Helpers | Shared utilities, response wrappers |

---

## 5. Architecture Rules

### The Golden Rule

```
Router → Service → Database Client → Supabase
```

Every request follows this path. No exceptions.

### Layer Responsibilities

#### Router Layer (Thin)
- Accept HTTP requests
- Validate input (Pydantic)
- Inject dependencies via `Depends()`
- Call appropriate service method
- Return standardized response

**Forbidden in routers:**
- Database queries
- Business logic
- Direct Supabase calls
- Service instantiation without DI

#### Service Layer (Business Logic)
- Implement business rules
- Coordinate between repositories/other services
- Throw custom exceptions
- Never import global clients
- Always receive database client via constructor

**Example:**
```python
class ClaimService:
    def __init__(self, db_client: Client):
        self.db_client = db_client
    
    def create_claim(self, user_id: str, data: dict) -> dict:
        # Business logic here
        return self.db_client.table("claims").insert(...).execute()
```

#### Database Layer (Client Management)
- Create database clients
- Manage client lifecycle
- Expose via FastAPI dependencies

**Two clients always:**
- `get_admin_client()` - System operations
- `get_user_client(jwt_token)` - User-scoped with RLS

#### Supabase Layer (External)
- Data persistence
- Authentication
- Storage
- RLS enforcement

---

## 6. Dependency Injection Rules

### Core Principle

**No global mutable state.** Ever.

Every dependency must be injected.

### Constructor Injection

Services receive dependencies via constructor:

```python
# ✅ CORRECT
class ClaimService:
    def __init__(self, db_client: Client):
        self.db_client = db_client

# ❌ WRONG
class ClaimService:
    def __init__(self):
        from app.database.client import supabase
        self.db_client = supabase
```

### FastAPI Dependency Injection

Routes receive dependencies via `Depends()`:

```python
# ✅ CORRECT
@router.get("/claims")
async def get_claims(
    current_user = Depends(get_current_user),
    db_client: Client = Depends(get_user_client)
):
    service = ClaimService(db_client)
    return service.get_user_claims(current_user.id)

# ❌ WRONG
@router.get("/claims")
async def get_claims():
    from app.database.client import supabase
    return supabase.table("claims").select("*").execute()
```

### Why No Global State?

1. **Testability** - Inject mock clients for unit tests
2. **Flexibility** - Swap clients (dev, staging, prod)
3. **Thread Safety** - Each request gets its own instance
4. **Maintainability** - Dependencies are explicit, not hidden

---

## 7. Database Clients

### Two Clients, Two Purposes

#### Admin Client: `get_admin_client()`

**Configuration:**
- Uses: `SUPABASE_SERVICE_ROLE_KEY`
- Scope: Full database access
- RLS: Bypassed (no row-level restriction)

**Use Cases:**
- AI agent processing (reads all claims)
- OCR pipeline (processes documents)
- Audit logging (writes system events)
- Storage administration
- Background jobs
- PDF generation
- User creation during registration
- JWT validation during authentication

**Example:**
```python
@router.post("/admin/claims/{id}/process")
async def process_claim_with_ai(
    claim_id: str,
    db_client: Client = Depends(get_admin_client)
):
    agent = AICoordinatorAgent(db_client)
    result = await agent.process(claim_id)
    return success_response(data=result)
```

#### User Client: `get_user_client(jwt_token: str)`

**Configuration:**
- Uses: `SUPABASE_ANON_KEY` + user's JWT
- Scope: Only user's own data
- RLS: Fully enforced (database policies restrict access)

**Use Cases:**
- Reading/writing user's own claims
- Uploading documents
- Viewing profile information
- Accessing own submission history

**Example:**
```python
@router.post("/claims")
async def create_claim(
    request: CreateClaimRequest,
    current_user = Depends(get_current_user),
    db_client: Client = Depends(get_user_client)
):
    service = ClaimService(db_client)
    claim = service.create_claim(current_user.id, request.dict())
    return success_response(data=claim)
```

### Row Level Security (RLS)

**RLS is the database-level access control.** It is never bypassed.

When a user makes a request:
1. Route calls `get_current_user()` to validate JWT
2. Route injects `get_user_client()` with that JWT
3. User client passes JWT to Supabase
4. Database RLS policies evaluate JWT claims
5. Only rows matching user's ID are accessible

**Critical Rule:** Never use `get_admin_client()` for user CRUD operations. Always use `get_user_client()` to let RLS enforce access control.

---

## 8. Security Rules

### Authentication

- **Provider:** Supabase Auth (managed service)
- **Method:** Email + Password or OAuth
- **Token:** JWT stored by frontend
- **Validation:** `get_current_user()` middleware validates JWT on protected routes

### Authorization

- **Mechanism:** Row Level Security (RLS) at database level
- **Enforcement:** Every user-scoped query respects `user_id` claims in JWT
- **No Exceptions:** RLS policies are always applied for user clients

### Secrets Management

All sensitive values stored in `.env`:
```
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SECRET_KEY=your_secret_here
GROQ_API_KEY=gsk_...
```

**Rules:**
- Never commit `.env` to version control
- Never log secrets
- Rotate keys regularly
- Use strong, random SECRET_KEY

### JWT Claims

JWT tokens from Supabase contain:
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "role": "authenticated",
  "iat": 1234567890,
  "exp": 1234571490
}
```

**Never trust frontend claims.** Always validate JWT server-side.

### Storage Security

Documents stored in Supabase Storage with RLS:
```
claim-files/{user_id}/{claim_id}/...
```

RLS policies ensure users can only access their own documents.

---

## 9. Coding Standards

### PEP 8 Compliance

All Python code follows PEP 8 style guide:
- 4-space indentation (never tabs)
- Maximum line length: 100 characters
- Two blank lines between functions/classes
- Import organization: stdlib, third-party, local

### Type Hints (Required)

Every function must have type hints:

```python
# ✅ CORRECT
def create_claim(
    self,
    user_id: str,
    claim_data: dict,
    db_client: Client
) -> dict:
    """Create a new claim for a user."""
    return db_client.table("claims").insert(...).execute()

# ❌ WRONG
def create_claim(self, user_id, claim_data, db_client):
    return db_client.table("claims").insert(...).execute()
```

### Docstrings (Required)

All public functions must have docstrings:

```python
def create_claim(self, user_id: str, claim_data: dict) -> dict:
    """
    Create a new insurance claim for the authenticated user.
    
    Args:
        user_id: The UUID of the claim owner
        claim_data: Dictionary containing claim details
        
    Returns:
        Dictionary with created claim ID and metadata
        
    Raises:
        ValidationError: If claim_data is invalid
        DatabaseError: If database operation fails
    """
```

### SOLID Principles

- **S**ingle Responsibility - Each class does one thing
- **O**pen/Closed - Open for extension, closed for modification
- **L**iskov Substitution - Derived classes are substitutable
- **I**nterface Segregation - Many specific interfaces vs few general ones
- **D**ependency Inversion - Depend on abstractions, not concrete classes

### DRY (Don't Repeat Yourself)

Extract common logic into utilities:

```python
# ❌ Repeated logic
success_response(message="Login successful", data=session)
success_response(message="Profile retrieved", data=profile)

# ✅ Use utility function
from app.utils.responses import success_response
```

### Code Organization

- Small functions (typically <20 lines)
- Single responsibility per function
- Readable variable names (no `x`, `y`, `temp`)
- No magic strings/numbers - use constants
- No circular imports

---

## 10. API Standards

### Response Wrapper (Always)

Every API response uses the standard wrapper:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { /* actual data */ },
  "errors": null
}
```

Implement via `success_response()` and `error_response()` utilities.

### HTTP Status Codes

| Status | Use Case |
|--------|----------|
| 200 | Successful GET, successful operation |
| 201 | Resource created (POST) |
| 204 | Successful operation, no content |
| 400 | Bad request, validation error |
| 401 | Unauthenticated (missing/invalid JWT) |
| 403 | Forbidden (authenticated but unauthorized) |
| 404 | Resource not found |
| 409 | Conflict (duplicate email, etc.) |
| 500 | Server error |

### API Naming

Use RESTful conventions:

```
POST   /claims              # Create claim
GET    /claims              # List user's claims
GET    /claims/{id}         # Get specific claim
PATCH  /claims/{id}         # Update claim
DELETE /claims/{id}         # Delete claim

POST   /claims/{id}/documents   # Upload document
GET    /claims/{id}/documents   # List documents
DELETE /documents/{id}          # Delete document

POST   /admin/claims/{id}/process  # Admin operation
```

### Input Validation

Use Pydantic models for all inputs:

```python
class CreateClaimRequest(BaseModel):
    policy_number: str
    claim_date: datetime
    incident_description: str
    
    class Config:
        # Validation settings
        validate_assignment = True
```

---

## 11. Error Handling

### Exception Hierarchy

```
ClaimPilotException (base)
├── AuthenticationError
├── AuthorizationError
├── ValidationError
├── DatabaseError
├── NotFoundError
└── ConflictError
```

### Business Exceptions (Services)

Services throw custom exceptions:

```python
# In service
class ClaimService:
    def get_claim(self, claim_id: str):
        claim = self.db_client.table("claims").select("*").eq("id", claim_id).single().execute()
        if not claim.data:
            raise NotFoundError(f"Claim {claim_id} not found")
        return claim.data
```

### HTTP Exceptions (Routers)

Routes catch and convert to HTTP:

```python
# In router
@router.get("/claims/{id}")
async def get_claim(claim_id: str, db = Depends(get_user_client)):
    try:
        service = ClaimService(db)
        return success_response(data=service.get_claim(claim_id))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log unexpected errors, never expose internals
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Logging

Never log sensitive data:
- ❌ Passwords, tokens, API keys
- ❌ Full stack traces to clients
- ✅ Error type, message, context
- ✅ Request ID, timestamp, user ID

---

## 12. Service Layer Rules

### What Belongs in Services

✅ Business logic (claim validation, eligibility checking)  
✅ Coordination between multiple operations  
✅ Data transformation  
✅ Custom validation rules  
✅ Exception throwing  

### What Does NOT Belong in Services

❌ HTTP request handling  
❌ Response formatting  
❌ Route parameters  
❌ Status code selection  
❌ Global mutable state  

### Service Interaction

Services can call other services:

```python
class ClaimService:
    def __init__(self, db_client: Client):
        self.db_client = db_client
    
    def create_claim_with_profile(self, user_id: str, data: dict) -> dict:
        # Use another service
        profile_service = ProfileService(self.db_client)
        profile = profile_service.get_profile(user_id)
        
        # Create claim with profile validation
        return self._create_claim(user_id, data, profile)
```

---

## 13. Router Rules

### Routers Must Be Thin

A good route does exactly 4 things:

```python
@router.post("/claims")
async def create_claim(
    request: CreateClaimRequest,                    # 1. Validate input
    current_user = Depends(get_current_user),       # 2. Inject dependency
    db = Depends(get_user_client)
):
    service = ClaimService(db)                      # 3. Call service
    claim = service.create_claim(current_user.id, request.dict())
    return success_response(data=claim)             # 4. Return response
```

### Forbidden in Routes

- ❌ Database queries
- ❌ Business logic
- ❌ Nested if/else (>2 levels)
- ❌ Direct service instantiation (always use DI)
- ❌ Exception handling details (delegate to services)

---

## 14. AI Agent Architecture

### Multi-Agent Orchestration

The AI system uses a coordinator pattern:

```
┌─────────────────────────┐
│  Coordinator Agent      │ (Groq + ADK)
│  (Orchestrates flow)    │
└────────────┬────────────┘
             │
    ┌────────┼────────┬──────────┬──────────┐
    ▼        ▼        ▼          ▼          ▼
┌────────┐┌─────┐┌──────┐┌────────┐┌──────────┐
│ Intake ││Policy│Evidence│Submission│Reviewer │
│ Agent  ││Agent ││ Agent  ││ Agent    ││ Agent  │
└────────┘└─────┘└──────┘└────────┘└──────────┘
    │        │        │          │          │
    └────────┴────────┴──────────┴──────────┘
             │
             ▼
      Supabase (RLS-protected)
```

### Agent Responsibilities

| Agent | Responsibility | Input | Output |
|-------|-----------------|-------|--------|
| **Intake** | Gather claim details | Claim, documents | Structured data |
| **Policy** | Validate eligibility | Policy doc, claim | Approval, gaps |
| **Evidence** | Evaluate documents | Upload docs | Quality score |
| **Submission** | Assemble packet | All above | PDF submission |
| **Reviewer** | Final QA | Complete packet | Approval/rejection |

### Implementation with Groq + ADK

Each agent is a service with Groq client:

```python
class IntakeAgent:
    def __init__(self, db_client: Client, groq_client):
        self.db_client = db_client
        self.groq_client = groq_client
    
    async def interview_user(self, claim_id: str) -> dict:
        # Use Groq to generate questions based on claim
        questions = await self.groq_client.generate_questions(claim_id)
        return questions
```

Google ADK orchestrates the workflow:

```python
coordinator = ClaimCoordinatorAgent(db_client, groq_client, adk_runtime)
result = await coordinator.process_claim(claim_id)
# ADK calls intake → policy → evidence → submission
```

---

## 15. OCR Pipeline

### Document Processing Workflow

```
Upload Document
    ↓
OCR Processing (Extract Text)
    ↓
Text Validation (Check quality)
    ↓
Entity Extraction (Policy #, dates, amounts)
    ↓
Update Claim Data
    ↓
Store Result in Supabase
```

### Implementation

```python
class OCRService:
    def __init__(self, db_client: Client, ocr_engine):
        self.db_client = db_client
        self.ocr_engine = ocr_engine
    
    async def process_document(self, claim_id: str, file_path: str) -> dict:
        # Extract text from image/PDF
        extracted_text = await self.ocr_engine.extract(file_path)
        
        # Validate quality
        if len(extracted_text) < 50:
            raise ValidationError("OCR confidence too low")
        
        # Extract entities
        entities = self._extract_entities(extracted_text)
        
        # Update claim
        self.db_client.table("claims").update({
            "extracted_text": extracted_text,
            "entities": entities,
            "ocr_processed": True
        }).eq("id", claim_id).execute()
        
        return entities
```

---

## 16. Storage Architecture

### Folder Structure

```
claim-files/
├── {user_id}/
│   ├── {claim_id}/
│   │   ├── documents/
│   │   │   ├── policy.pdf
│   │   │   ├── receipt_001.jpg
│   │   │   └── receipt_002.jpg
│   │   ├── ocr_results/
│   │   │   ├── policy_extracted.txt
│   │   │   └── receipt_001_extracted.txt
│   │   └── submission_packet.pdf
│   └── {claim_id}/
│       └── ...
```

### Upload Lifecycle

1. **Validation** - Check file type, size, permissions
2. **Upload** - Push to Supabase Storage
3. **OCR** - Process if image/PDF
4. **Reference** - Store path in database
5. **Cleanup** - Delete after submission (if applicable)

### RLS Policies

Storage has RLS enforced:
```sql
CREATE POLICY "Users can upload to own folder"
ON storage.objects
FOR INSERT
TO authenticated
USING (bucket_id = 'claim-files' AND auth.uid()::text = (storage.foldername(name))[1]);
```

---

## 17. Future Modules

### Claims Module
**Status:** Implementation next  
**Responsibility:** Claim CRUD, status tracking, lifecycle management  
**Routes:** POST /claims, GET /claims, PATCH /claims/{id}, DELETE /claims/{id}

### Documents Module
**Status:** Implementation phase 2  
**Responsibility:** Document upload, storage, retrieval  
**Routes:** POST /documents, GET /documents, DELETE /documents/{id}

### OCR Module
**Status:** Implementation phase 3  
**Responsibility:** Text extraction, entity recognition, validation  
**Routes:** POST /ocr/process, GET /ocr/results/{id}

### AI Orchestration Module
**Status:** Implementation phase 4  
**Responsibility:** Coordinate Groq agents, manage workflow  
**Routes:** POST /admin/claims/{id}/process, GET /admin/jobs/{id}

### PDF Generation Module
**Status:** Implementation phase 5  
**Responsibility:** Create submission packets  
**Routes:** GET /claims/{id}/submission-packet (download PDF)

### Notifications Module
**Status:** Future consideration  
**Responsibility:** Email/SMS alerts on claim status  

### Analytics Module
**Status:** Future consideration  
**Responsibility:** Aggregate metrics, reporting  

### Admin Dashboard
**Status:** Future consideration  
**Responsibility:** System monitoring, user management  

---

## 18. Testing Standards

### Unit Testing Philosophy

All testable code must have unit tests. Use dependency injection to make code testable.

### Mock Database Clients

```python
from unittest.mock import Mock

def test_create_claim():
    # Mock database client
    mock_db = Mock()
    mock_db.table().insert().execute.return_value = Mock(data={"id": "123"})
    
    # Create service with mock
    service = ClaimService(mock_db)
    
    # Test
    result = service.create_claim("user-123", {"amount": 100})
    
    # Verify
    assert result["id"] == "123"
    mock_db.table.assert_called_with("claims")
```

### Mock Groq Client

```python
def test_intake_agent():
    mock_groq = Mock()
    mock_groq.invoke.return_value = "What is your claim amount?"
    
    agent = IntakeAgent(mock_db, mock_groq)
    questions = agent.generate_questions(claim_id)
    
    assert "claim amount" in questions
```

### Test Organization

```
tests/
├── unit/
│   ├── services/
│   │   ├── test_claim_service.py
│   │   ├── test_auth_service.py
│   │   └── ...
│   ├── agents/
│   │   └── test_intake_agent.py
│   └── ...
├── integration/
│   ├── test_api_claims.py
│   └── ...
└── fixtures/
    ├── mock_db.py
    ├── mock_groq.py
    └── ...
```

---

## 19. Git Workflow

### Branch Strategy

- **main** - Production code, always deployable
- **develop** - Integration branch for features
- **feature/xyz** - Individual features, cut from develop

### Commit Messages

Follow conventional commits:

```
type(scope): subject

body

footer
```

Examples:
```
feat(claims): implement claim creation endpoint

Add POST /claims endpoint with claim validation
and OCR trigger. Uses ClaimService for business logic.

Closes #42

fix(auth): handle expired JWT tokens correctly

refactor(database): extract query builder

docs(codex): update API standards section
```

### Code Review

- All PRs require review before merge
- At least one approval required
- CI/CD pipeline must pass
- No commits directly to main

### Secrets

**NEVER commit:**
- `.env` files
- API keys
- Database credentials
- JWT secrets
- User data

Use `.env.example` as template:
```
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

---

## 20. Codex Rules

### What Codex Is Allowed To Do

✅ Implement requested features (following specifications)  
✅ Add new services, routes, schemas (using established patterns)  
✅ Write unit tests  
✅ Improve code clarity  
✅ Add documentation  
✅ Fix bugs  
✅ Analyze requirements before implementing  
✅ Ask for clarification  

### What Codex Is FORBIDDEN To Do

❌ Redesign the architecture without explicit approval  
❌ Modify SQL migrations or schema  
❌ Rename or reorganize folders  
❌ Perform unsolicited refactors  
❌ Invent APIs that weren't requested  
❌ Change dependency injection patterns  
❌ Introduce global mutable state  
❌ Bypass Row Level Security  
❌ Skip error handling  
❌ Create undocumented features  

### Codex Workflow

1. **Analyze** - Examine requirements, ask clarifying questions
2. **Plan** - List affected files, sketch changes
3. **Wait** - Request approval before implementing
4. **Implement** - Follow established patterns
5. **Verify** - Check for syntax errors, test basic flows
6. **Document** - Provide summary of changes

### Code Review by Codex

Before implementing, Codex must:
- List all files to be modified
- Explain each change
- Identify potential issues
- Estimate impact
- Wait for approval

---

## 21. Development Workflow

### Feature Implementation Process

```
1. Requirements Received
   ↓
2. Analysis Phase
   - Understand requirements
   - Ask clarifying questions
   - Sketch architecture
   ↓
3. Planning Phase
   - List affected files
   - Document changes
   - Identify dependencies
   ↓
4. Approval Gate
   - Wait for explicit approval
   - Address feedback
   ↓
5. Implementation Phase
   - Follow code standards
   - Use established patterns
   - Write unit tests
   ↓
6. Testing Phase
   - Unit tests pass
   - Integration with existing code
   - Error handling verified
   ↓
7. Review Phase
   - Code review
   - Security review
   - Documentation check
   ↓
8. Deployment Phase
   - Merge to develop
   - Run CI/CD pipeline
   - Verify in staging
   - Merge to main
   ↓
9. Documentation
   - Update Codex if needed
   - Update API docs
   - Create release notes
```

---

## 22. Feature Roadmap

### Phase 1: Claims CRUD (Next)
- POST /claims - Create claim
- GET /claims - List user's claims
- GET /claims/{id} - Get claim details
- PATCH /claims/{id} - Update claim
- DELETE /claims/{id} - Delete claim

### Phase 2: Document Management
- Upload documents to claims
- List documents
- Delete documents
- Store in Supabase Storage

### Phase 3: OCR Processing
- Extract text from uploads
- Validate OCR quality
- Extract entities
- Update claim with results

### Phase 4: Coordinator Agent
- Orchestrate AI workflow
- Call intake, policy, evidence agents
- Aggregate results

### Phase 5: Intake Agent
- Ask clarifying questions
- Validate responses
- Store answers

### Phase 6: Policy Agent
- Validate policy eligibility
- Check coverage
- Identify gaps

### Phase 7: Evidence Agent
- Evaluate document quality
- Score evidence
- Flag missing evidence

### Phase 8: Submission Agent
- Assemble submission packet
- Final validation
- Ready for review

### Phase 9: PDF Generator
- Create submission PDFs
- Include all documents
- Professional formatting

### Phase 10: Flutter Integration
- Real-time API sync
- Document upload UI
- Status tracking
- PDF download

### Future: Notifications, Analytics, Admin Dashboard

---

## 23. Definition of Done

Every completed feature must satisfy all criteria:

### Code Quality
- ✅ Type hints on all functions
- ✅ Docstrings on all public functions
- ✅ Follows PEP 8 style guide
- ✅ No global mutable state
- ✅ Proper error handling
- ✅ No hardcoded secrets

### Architecture
- ✅ Dependency injection throughout
- ✅ Business logic in services
- ✅ Thin routers
- ✅ Custom exceptions where appropriate
- ✅ Follows established patterns

### Testing
- ✅ Unit tests written
- ✅ Mock clients for DB/external calls
- ✅ >80% code coverage
- ✅ Tests run and pass

### Security
- ✅ JWT validation on protected routes
- ✅ RLS policies enforced
- ✅ No secrets in code
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (use ORM)

### Documentation
- ✅ API documented (docstrings)
- ✅ Complex logic explained
- ✅ Examples provided
- ✅ Codex updated if needed

### API Standards
- ✅ Response wrapper consistent
- ✅ Error responses standardized
- ✅ HTTP status codes correct
- ✅ RESTful naming conventions

---

## 24. Final Engineering Principles

### Core Philosophy

These principles guide every decision:

1. **Architecture Over Shortcuts**
   - Invest in clean architecture
   - Short-term hacks create long-term pain
   - Maintainability beats speed

2. **Readability Over Cleverness**
   - Code is read more than written
   - Explicit beats implicit
   - Avoid magic, be obvious

3. **Security By Default**
   - Assume nothing is secure
   - Validate all inputs
   - Enforce RLS at database level
   - Never trust the client

4. **Keep Routers Thin**
   - Routes: validate, inject, call, return
   - Services: contain logic
   - This separation is non-negotiable

5. **Services Own Business Logic**
   - Business rules belong in services
   - Services are testable in isolation
   - Route handlers are thin wrappers

6. **RLS Is Never Bypassed For User Ops**
   - Use user client for user CRUD
   - Admin client only for system operations
   - Let database enforce access control

7. **Do Not Optimize Prematurely**
   - Get it right first
   - Measure before optimizing
   - Profile actual bottlenecks

8. **Prefer Maintainability Over Abstraction**
   - Simple code beats clever code
   - Three copies before abstracting
   - YAGNI (You Aren't Gonna Need It)

9. **Implement Only What Was Requested**
   - Scope creep kills projects
   - Extra features cause bugs
   - Stay focused on the specification

10. **Never Redesign Without Approval**
    - Architecture is frozen
    - All changes are feature additions
    - Refactoring requires explicit permission

11. **Ask Before Implementing**
    - Clarify requirements
    - Propose solution
    - Wait for approval
    - Then implement

12. **Test With Real Scenarios**
    - Write tests that match user behavior
    - Test error cases
    - Test edge cases
    - Think like a user

13. **Document as You Go**
    - Docstrings as you code
    - Update Codex if you change architecture
    - Comments explain why, not what

14. **Security Is Everyone's Responsibility**
    - Think about attack vectors
    - Validate inputs
    - Sanitize outputs
    - Assume breach

15. **Consistent Patterns Across Codebase**
    - Use the same patterns everywhere
    - New team members can read and understand
    - Predictability reduces bugs

---

## Conclusion

This handbook defines how ClaimPilot is built. It is the source of truth for every implementation decision.

**Remember:**
- The architecture is frozen.
- Services encapsulate logic.
- Routers are thin wrappers.
- Dependencies are injected.
- Security is enforced at every layer.
- RLS protects user data.

When in doubt, refer back to these principles. When implementing a feature, follow the established patterns. When adding code, ask yourself:

- "Does this follow the architecture?"
- "Is this code testable?"
- "Is this secure?"
- "Can another engineer understand this?"
- "Is this the simplest solution?"

**If the answer to all five is yes, you're ready to commit.**

---

**Engineering Excellence is not a destination—it's a journey. Let's build ClaimPilot right.**

---

**Document Revision History**

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | June 29, 2026 | Initial codex created after Phase 4 refactor |

