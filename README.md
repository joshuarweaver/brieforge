# Fieldcraft Backend

Intelligence-driven campaign generation system powered by public signal intelligence.

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy
- **Authentication**: API keys with bcrypt-hashed secrets
- **Signals**: Multi-platform search orchestration with deduped evidence
- **Insights**: Signal enrichment, automated blueprinting, export adapters
- **Observability**: Audit logging and compliance hooks
- **LLMs**: Anthropic Claude Sonnet 4.5, OpenAI GPT-4o-mini
- **APIs**: SerpAPI (for omnisearch across platforms)

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis (optional, required for distributed rate limiting)
- Virtual environment (recommended)

### Installation

1. **Create virtual environment**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Environment configuration**:
```bash
cp .env.example .env
# Edit .env with your actual values:
# - DATABASE_URL
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - ANTHROPIC_API_KEY
# - OPENAI_API_KEY
# - SERPAPI_KEY
# - ADMIN_PROVISION_TOKEN (required to provision API keys; sent via `X-Admin-Token`)
# - RATE_LIMIT_REQUESTS_PER_MINUTE (global requests allowed per key)
# - RATE_LIMIT_WINDOW_SECONDS (window size in seconds for the limiter)
# - RATE_LIMIT_REDIS_URL (optional Redis URL to enforce rate limits across instances)
```

4. **Set up database**:
```bash
# Create PostgreSQL database
createdb fieldcraft

# Run migrations (Alembic will auto-create tables for now)
# In production, generate and run migrations:
# alembic revision --autogenerate -m "Initial migration"
# alembic upgrade head
```

5. **Run the application**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access API documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # Dependencies (auth, db)
│   │   └── v1/
│   │       ├── auth.py          # API key auth + account management
│   │       ├── campaigns.py     # Campaign CRUD
│   │       └── workspaces.py    # Workspace CRUD
│   ├── core/
│   │   ├── config.py            # Settings
│   │   ├── database.py          # DB connection
│   │   └── security.py          # API key utilities
│   ├── models/
│   │   ├── user.py              # User, Workspace
│   │   ├── campaign.py          # Campaign
│   │   ├── signal.py            # Signal
│   │   └── asset.py             # Analysis, GeneratedAsset, Learning
│   ├── schemas/
│   │   ├── user.py              # User/Workspace schemas
│   │   └── campaign.py          # Campaign/Signal schemas
│   └── main.py                  # FastAPI app
├── alembic/                     # Database migrations
├── requirements.txt
└── .env.example
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user, create workspace, and issue API key
- `GET /api/v1/auth/me` - Get current user details
- `GET /api/v1/auth/api-keys` - List active API keys
- `POST /api/v1/auth/api-keys` - Create additional API key
- `DELETE /api/v1/auth/api-keys/{id}` - Revoke API key

Provisioning endpoints (`POST /api/v1/auth/register`, `POST /api/v1/auth/api-keys`) require the `X-Admin-Token` header when `ADMIN_PROVISION_TOKEN` is set. All authenticated requests enforce a global rate limit controlled by `RATE_LIMIT_REQUESTS_PER_MINUTE` over `RATE_LIMIT_WINDOW_SECONDS`; exceeding the limit returns HTTP 429 with a `Retry-After` hint. Set `RATE_LIMIT_REDIS_URL` to enable distributed enforcement of those limits; otherwise they apply per process.

Registration payloads must include `email`, `first_name`, `last_name`, `phone`, `password`, and optionally `workspace_name`. Passwords are stored hashed.

### Workspaces
- `GET /api/v1/workspaces` - List user's workspaces
- `POST /api/v1/workspaces` - Create workspace
- `GET /api/v1/workspaces/{id}` - Get workspace
- `PATCH /api/v1/workspaces/{id}` - Update workspace
- `DELETE /api/v1/workspaces/{id}` - Delete workspace

### Campaigns
- `GET /api/v1/campaigns` - List campaigns in workspace
- `POST /api/v1/campaigns` - Create campaign
- `GET /api/v1/campaigns/{id}` - Get campaign
- `PATCH /api/v1/campaigns/{id}` - Update campaign
- `DELETE /api/v1/campaigns/{id}` - Delete campaign
- `POST /api/v1/campaigns/{id}/blueprint` - Generate campaign blueprint (LLM-driven by default, optional persistence)
- `GET /api/v1/campaigns/{id}/blueprints` - List stored blueprint artifacts
- `GET /api/v1/campaigns/{id}/blueprints/{blueprint_id}` - Retrieve a specific blueprint artifact

#### Blueprint Generation
- Blueprints synthesize collected signals, enrichment features, completed analyses, and (when available) strategic briefs.
- The service calls the configured LLM (default Claude) to create the JSON output; if the LLM fails, a deterministic rule-based blueprint is returned instead.
- Query parameters:
  - `persist` (default `true`) — store the generated artifact for later retrieval.
  - `use_llm` (optional) — override the environment default (`true`/`false`).
- The response metadata indicates the generation method, LLM model details, and includes a condensed rule-based preview for comparison.
- Draft assets are aligned to campaign channels, enforcing a minimum of five variants per requested platform (e.g., 5 for Meta, 5 for Google, etc.) with counts reported in `metadata.asset_counts`.

### Signals
- `POST /api/v1/campaigns/{id}/signals/collect` - Collect multi-source signals with deduplication
- `POST /api/v1/campaigns/{id}/signals/enrich` - Run enrichment pipeline on collected signals
- `GET /api/v1/campaigns/{id}/signals` - Retrieve signals with filters
- `GET /api/v1/campaigns/signals/{signal_id}/enrichments` - Inspect enrichment records for a signal

### Exports
- `POST /api/v1/campaigns/{id}/exports/{platform}` - Build export payloads (meta, google, linkedin)

### Observability
- `GET /api/v1/observability/events` - View recent audit/observability events

## Database Schema

### Multi-Tenancy
- `workspaces` - Workspace isolation
- `users` - User accounts

### Core Campaign System
- `campaigns` - Campaign with brief (JSONB)
- `signals` - Intelligence from SerpAPI omnisearch
- `analyses` - Insight Lattice results (strategy, pillars, hooks, KPIs)
- `generated_assets` - Social posts, ads, etc.

### Learning System
- `asset_ratings` - User feedback (1-5 stars)
- `success_patterns` - Learned patterns from high-rated assets

## Brief Schema

When creating a campaign, provide a brief with:

```json
{
  "goal": "Increase B2B SaaS signups by 30%",
  "audiences": ["Marketing Directors", "Growth Teams"],
  "offer": "AI-powered campaign intelligence platform",
  "competitors": ["HubSpot", "Marketo"],
  "channels": ["linkedin", "google_ads"],
  "budget_band": "$10k-$25k/month",
  "voice_constraints": "Professional but approachable, data-driven"
}
```

**Supported channels**:
- `linkedin`
- `facebook`
- `instagram`
- `tiktok`
- `youtube`
- `pinterest`
- `google_ads` (always included)

## Deployment

- See [`docs/deployment/koyeb.md`](docs/deployment/koyeb.md) for end-to-end instructions to deploy the API on Koyeb using the provided Dockerfile and manifest.

## Development

### Running tests
```bash
pytest
```

### Code formatting
```bash
black app/
ruff check app/
```

### Database migrations

**Create new migration**:
```bash
alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations**:
```bash
alembic upgrade head
```

**Rollback migration**:
```bash
alembic downgrade -1
```

## Next Steps (Upcoming Phases)

- **Phase 2**: SerpAPI Omnisearch (15+ search methods)
- **Phase 3**: Insight Lattice (Claude-powered analysis)
- **Phase 4**: Multi-Agent Adversarial Panel (7 agents)
- **Phase 5**: Asset Generation Engine
- **Phase 6**: Simple Learning System
- **Phase 7**: Full Pipeline Orchestration

## License

Proprietary
