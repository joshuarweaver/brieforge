# Fieldcraft - Project Overview

**Intelligence-First Campaign Generation System**

## Vision

Transform campaign strategy from guesswork to evidence-based decision-making by mining public intelligence across all major platforms and synthesizing it into actionable, receipted campaign assets.

## Core Differentiators

1. **Receipts Everywhere** - Every strategic decision, hook, and KPI is linked to public signal sources
2. **Omnisearch Intelligence** - Single API (SerpAPI) searches 15+ sources across all platforms
3. **Multi-Agent Review** - 7 specialized AI agents review and improve all outputs
4. **Learning System** - Gets smarter over time from user ratings and patterns
5. **2-Page Strategy** - Dense, actionable strategy (not bloated reports)
6. **Export-First** - No vendor lock-in, everything portable

## Architecture

### Technology Stack

**Backend**
- Python 3.11+ / FastAPI
- PostgreSQL (multi-tenant)
- SQLAlchemy + Alembic
- JWT authentication

**LLMs**
- **Claude Sonnet 4.5**: Strategy, analysis, compliance, competitive intel
- **GPT-4o-mini**: Channel optimization, buyer skepticism (cost-effective)

**Intelligence Sources** (via SerpAPI)
- Google SERP (organic + PAA + ads)
- Meta Ad Library (Facebook/Instagram)
- LinkedIn Ads + Organic
- TikTok Ads + Trending
- YouTube (videos + metadata)
- Reddit (research only, not content)
- Pinterest (visual trends)

### Data Flow

```
User Brief (goal, audiences, offer, competitors, channels, budget)
    ↓
Omnisearch (SerpAPI) → 15+ search methods across all platforms
    ↓
Signals (scored, stored, attributed)
    ↓
Insight Lattice (Claude) → Score, cluster, analyze
    ↓
Draft Generation:
  - 2-page strategy (positioning, pillars, hooks, objections, KPIs)
  - 8-12 assets per selected channel
  - Google Ads (3-5 variants)
    ↓
7-Agent Panel Review (parallel)
  1. Chief Strategist (coherence, clarity)
  2. Compliance (claims, disclaimers)
  3. Skeptical Buyer (objections, proof)
  4. Channel Expert (platform optimization)
  5. Data Analyst (KPI realism)
  6. Brand Consistency (voice, alignment)
  7. Competitive Intel (differentiation)
    ↓
Apply Diffs (priority: compliance > strategist > others)
    ↓
Final Output:
  - 2-page strategy PDF (all citations inline)
  - Assets by channel (JSON/CSV/MD)
  - Receipts document (full provenance)
  - ZIP bundle
    ↓
User Ratings → Learning Engine → Future Improvements
```

## Implementation Phases

### ✅ Phase 1: Foundation (COMPLETE)
- FastAPI backend with multi-tenant auth
- PostgreSQL with SQLAlchemy models
- Campaign CRUD with Brief schema
- Workspace isolation
- JWT authentication
- Alembic migrations setup

**API Endpoints**: `/auth`, `/workspaces`, `/campaigns`

---

### 🔄 Phase 2: Omnisearch Signal Intelligence (NEXT)
**Deliverables**:
- Single `SerpCartridge` with 15+ search methods
- Signal gathering across all platforms
- Rich metadata storage (JSONB)
- Per-method graceful error handling
- Signal statistics endpoint

**New Endpoints**:
```
POST /api/v1/campaigns/{id}/signals/gather
GET  /api/v1/campaigns/{id}/signals
GET  /api/v1/campaigns/{id}/signals/stats
```

**Search Methods**:
1. Organic SERP (intents, PAA, featured snippets)
2. Google Ads (competitor messaging)
3. Meta Ad Library (FB/IG ads)
4. LinkedIn Ads
5. TikTok Ad Library
6. Reddit Ads
7. Pinterest Ads
8. LinkedIn Organic (posts, articles)
9. Instagram Organic (hashtags, trends)
10. TikTok Organic (viral formats, sounds)
11. YouTube (video titles, descriptions, captions)
12. Reddit Organic (posts, comments - RESEARCH ONLY)
13. Pinterest Organic (pin trends)
14. Facebook Organic (discussions)
15. Trending Hashtags (cross-platform)
16. Viral Formats (platform-specific)

---

### Phase 3: Insight Lattice Engine
**Deliverables**:
- Signal scoring algorithm (recency × corroboration × proximity)
- Claude-powered clustering (pillars, hooks, objections, proof)
- 2-page strategy generation (Markdown)
- KPI ladder with sources
- Receipts/attribution map

**New Endpoints**:
```
POST /api/v1/campaigns/{id}/analyze
GET  /api/v1/campaigns/{id}/analysis
GET  /api/v1/campaigns/{id}/analysis/receipts
```

---

### Phase 4: Multi-Agent Adversarial Panel
**Deliverables**:
- 7 specialized agents (4 Claude, 3 GPT-4o-mini)
- Parallel review execution
- Priority-based diff application
- Concise feedback (diffs + 1-2 sentence rationale)

**New Endpoints**:
```
POST /api/v1/campaigns/{id}/analysis/review
GET  /api/v1/campaigns/{id}/analysis/reviews
```

---

### Phase 5: Asset Generation Engine
**Deliverables**:
- Dynamic generation based on `brief.channels[]`
- Platform-specific optimization
- 8-12 pieces per channel
- Google Ads (always generated, 3-5 variants)
- All assets include receipts + expected KPIs

**Asset Types**:
- **LinkedIn**: feed posts, carousel scripts, video hooks
- **Facebook**: community posts, ad variations
- **Instagram**: feed captions, Reel scripts, Story frameworks
- **TikTok**: video scripts (hook + story + CTA)
- **YouTube**: video descriptions, titles, hooks
- **Pinterest**: pin descriptions, board organization
- **Google Ads**: responsive search ads (headlines, descriptions, extensions)

**New Endpoints**:
```
POST /api/v1/campaigns/{id}/assets/generate
GET  /api/v1/campaigns/{id}/assets
GET  /api/v1/campaigns/{id}/assets/{type}
```

---

### Phase 6: Simple Learning System
**Deliverables**:
- Asset rating system (1-5 stars + notes)
- Pattern extraction from high-rated assets
- Workspace-level insights dashboard
- Signal source reliability tracking

**New Endpoints**:
```
POST /api/v1/assets/{id}/rate
GET  /api/v1/workspaces/{id}/insights
```

**Future Enhancement**: Vector embeddings + semantic similarity for predictive recommendations

---

### Phase 7: Full Pipeline Orchestration
**Deliverables**:
- One-click full generation
- Progress tracking (real-time updates)
- Error handling & rollback
- Status monitoring

**New Endpoints**:
```
POST /api/v1/campaigns/{id}/generate-full
GET  /api/v1/campaigns/{id}/status
```

---

### Phase 8: Export System (Later)
**Deliverables**:
- 2-page strategy PDF
- Assets by channel (JSON/CSV/MD)
- Receipts document (JSON)
- ZIP bundle
- Optional Google Docs integration

---

### Phase 9: Next.js Frontend (Later)
**Deliverables**:
- Campaign builder (multi-step form)
- Generation progress tracker
- Split-pane results viewer (content + citations sidebar)
- Asset rating interface
- Learning insights dashboard

---

## Database Schema

### Multi-Tenancy
```sql
workspaces (id, name, owner_id, settings JSONB, created_at)
users (id, email, hashed_password, workspace_id, role, created_at)
```

### Core Campaign System
```sql
campaigns (id, workspace_id, name, status, brief JSONB, created_at, updated_at)
signals (id, campaign_id, source, search_method, query, evidence JSONB, relevance_score, created_at)
analyses (id, campaign_id, strategy TEXT, pillars JSONB, hooks JSONB, objections JSONB, kpis JSONB, receipts JSONB, panel_reviews JSONB, created_at, updated_at)
generated_assets (id, campaign_id, asset_type, platform, format, content JSONB, receipts JSONB, created_at)
```

### Learning System
```sql
asset_ratings (id, asset_id, user_id, rating, notes, created_at)
success_patterns (id, workspace_id, pattern_type, content JSONB, usage_count, avg_rating, created_at, updated_at)
```

---

## Brief Schema

```json
{
  "goal": "Increase B2B SaaS signups by 30%",
  "audiences": ["Marketing Directors", "Growth Teams"],
  "offer": "AI-powered campaign intelligence platform",
  "competitors": ["HubSpot", "Marketo"],
  "channels": ["linkedin", "google_ads", "facebook"],
  "budget_band": "$10k-$25k/month",
  "voice_constraints": "Professional but approachable, data-driven"
}
```

---

## Example Output Structure

### 2-Page Strategy
**Page 1: Strategy Core**
- Positioning (1 paragraph, cited)
- Pillars (3-5, bullet format with sources)
- Hooks by channel (LinkedIn, Facebook, etc.)
- Top 3 objections + responses + proof requirements

**Page 2: Execution & KPIs**
- Audience matrix (compact table)
- Channel strategy & KPIs (table with sources)
- Budget allocation (if provided)
- Success metrics & timeline

### Generated Asset Example (LinkedIn Post)
```json
{
  "platform": "linkedin",
  "format": "feed_post",
  "copy": "Stop guessing what your audience wants...",
  "visual_guidance": "Screenshot of competitive analysis dashboard",
  "hook_source": "Pillar 2: Evidence-Driven Decisions",
  "persona_target": "Marketing Directors",
  "journey_stage": "awareness",
  "cta": "See how we analyze 1000+ signals →",
  "hashtags": ["#B2BMarketing", "#MarketingIntel"],
  "reasoning": "LinkedIn audiences respond to data-backed claims. 12 competitor posts with 'stop guessing' hook averaged 4.2% engagement.",
  "supporting_signals": [
    {
      "url": "https://linkedin.com/posts/...",
      "timestamp": "2025-01-15",
      "snippet": "Tired of guessing? 73% of marketers...",
      "metadata": {"likes": 342, "comments": 28}
    }
  ],
  "expected_kpis": {
    "engagement_rate": "2.1-3.5%",
    "click_through_rate": "0.8-1.2%"
  }
}
```

---

## Timeline Estimate

- **Phase 1**: ✅ Complete (2-3 days)
- **Phase 2**: 3-4 days
- **Phase 3**: 3-4 days
- **Phase 4**: 4-5 days
- **Phase 5**: 4-5 days
- **Phase 6**: 2-3 days
- **Phase 7**: 2-3 days
- **Phase 8**: 2-3 days (export)
- **Phase 9**: 5-7 days (frontend)

**Total Backend**: ~5-7 weeks
**Full System**: ~6-8 weeks

---

## Current Status

✅ **Phase 1 Complete** - Foundation is ready

**What works now**:
- User registration + login (JWT)
- Workspace creation
- Campaign CRUD with brief validation
- Multi-tenant isolation
- Full API documentation at `/docs`

**Next up**: Phase 2 - Omnisearch Signal Intelligence

---

## Getting Started

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
createdb fieldcraft
./run.sh
```

Access API docs: http://localhost:8000/docs

---

## License

Proprietary
