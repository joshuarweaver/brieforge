# Fieldcraft API - Postman Collection Guide

## Overview

This Postman collection provides complete testing coverage for the Fieldcraft API, an intelligence-driven campaign generation system.

## Features

- **✓ Complete API Coverage**: All endpoints across Auth, Workspaces, Campaigns, Signals, and AI Analysis
- **✓ Automated Authentication**: Token management with auto-save after login
- **✓ Environment Variables**: Pre-configured variables for seamless testing
- **✓ Response Tests**: Automated validation of API responses
- **✓ 7 Signal Sources**: Google, YouTube, Meta Ads, LinkedIn, TikTok, Reddit, Pinterest
- **✓ AI-Powered Analysis**: Claude and OpenAI integration for signal insights

## Quick Start

### 1. Import Collection

1. Open Postman
2. Click **Import** → **Upload Files**
3. Select `Fieldcraft_API.postman_collection.json`
4. Collection will appear in your sidebar

### 2. Configure Variables

The collection includes default variables. Update these if needed:

| Variable | Default Value | Description |
|----------|--------------|-------------|
| `base_url` | `http://localhost:8000` | API base URL |
| `email` | `test@example.com` | Your test account email |
| `password` | `testpassword123` | Your test account password |

**To edit variables:**
- Right-click collection → **Edit**
- Go to **Variables** tab
- Update **Current Value** column

### 3. First Time Setup

Run these requests in order:

1. **Authentication → Register User**
   - Creates new account + workspace
   - Auto-saves `user_id` and `workspace_id`

2. **Authentication → Login**
   - Authenticates user
   - Auto-saves `access_token` (valid for 30 minutes)
   - Token is automatically used in all subsequent requests

3. **Campaigns → Create Campaign**
   - Creates test campaign
   - Auto-saves `campaign_id`

Now you're ready to test all endpoints!

## API Workflow

### Complete Testing Flow

```
1. Register/Login
   └─→ Get auth token

2. Create Campaign
   └─→ Define brief (goal, audience, competitors, etc.)

3. Collect Signals
   ├─→ All cartridges (Google, YouTube, Meta, etc.)
   └─→ Or specific cartridges only

4. Analyze Signals with AI
   ├─→ Comprehensive analysis
   ├─→ Competitor analysis
   ├─→ Audience insights
   └─→ Custom analysis types

5. Review Results
   ├─→ View signals
   └─→ View AI insights
```

## Endpoint Reference

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register new user + workspace |
| `/api/v1/auth/login` | POST | Login and get JWT token |
| `/api/v1/auth/me` | GET | Get current user info |

### Campaigns

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/campaigns` | POST | Create new campaign |
| `/api/v1/campaigns` | GET | List all campaigns |
| `/api/v1/campaigns/{id}` | GET | Get campaign details |
| `/api/v1/campaigns/{id}` | PUT | Update campaign |
| `/api/v1/campaigns/{id}` | DELETE | Delete campaign |

### Signals (Intelligence Collection)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/campaigns/{id}/signals/collect` | POST | Collect signals from platforms |
| `/api/v1/campaigns/{id}/signals` | GET | List campaign signals |
| `/api/v1/signals/{id}` | GET | Get signal details |

**Available Cartridges:**
- `google_serp` - Google organic search
- `youtube` - YouTube videos
- `meta_ads` - Facebook/Instagram ads
- `linkedin_ads` - LinkedIn ads
- `tiktok_ads` - TikTok ads
- `reddit` - Reddit ads
- `pinterest` - Pinterest content (via Google)

### AI Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/campaigns/{id}/analyze` | POST | Analyze signals with AI |
| `/api/v1/campaigns/{id}/signal-analyses` | GET | List analyses |
| `/api/v1/signal-analyses/{id}` | GET | Get analysis details |
| `/api/v1/signal-analyses/{id}` | DELETE | Delete analysis |

**Analysis Types:**
- `comprehensive` - Full analysis across all dimensions
- `competitor` - Competitor strategy analysis
- `audience` - Audience insights and pain points
- `messaging` - Messaging patterns
- `creative` - Creative recommendations
- `trends` - Market trends

**LLM Providers:**
- `claude` - Anthropic Claude (recommended)
- `openai` - OpenAI GPT-4

## Example Requests

### 1. Register and Login

```json
// POST /api/v1/auth/register
{
    "email": "jane@company.com",
    "password": "SecurePass123!",
    "workspace_name": "Acme Marketing"
}

// POST /api/v1/auth/login (form-urlencoded)
username: jane@company.com
password: SecurePass123!
```

### 2. Create Campaign

```json
// POST /api/v1/campaigns
{
    "name": "Q4 Product Launch",
    "brief": {
        "goal": "increase brand awareness",
        "audiences": ["B2B marketers", "startup founders"],
        "offer": "marketing automation platform",
        "competitors": ["HubSpot", "Marketo", "Pardot"],
        "channels": ["linkedin", "google", "youtube"],
        "budget_band": "$10k-50k/month",
        "voice_constraints": "professional, data-driven"
    }
}
```

### 3. Collect Signals

```json
// POST /api/v1/campaigns/{id}/signals/collect

// All cartridges, 3 queries each:
{
    "max_queries_per_cartridge": 3
}

// Specific cartridges only:
{
    "cartridge_names": ["google_serp", "youtube", "meta_ads"],
    "max_queries_per_cartridge": 5
}
```

### 4. Analyze with AI

```json
// POST /api/v1/campaigns/{id}/analyze

// Comprehensive analysis (synchronous):
{
    "analysis_type": "comprehensive",
    "llm_provider": "claude",
    "max_signals": 50,
    "min_relevance": 0.3,
    "async_mode": false
}

// Competitor analysis (background):
{
    "analysis_type": "competitor",
    "llm_provider": "claude",
    "async_mode": true
}
```

## Response Examples

### Signal Collection Response

```json
{
    "campaign_id": 1,
    "cartridges_run": 7,
    "total_signals": 42,
    "errors": [],
    "timestamp": "2025-10-24T23:40:28.234263"
}
```

### Analysis Response

```json
{
    "id": 1,
    "campaign_id": 1,
    "analysis_type": "comprehensive",
    "status": "completed",
    "llm_provider": "claude",
    "llm_model": "claude-3-5-sonnet-20241022",
    "tokens_used": 3542,
    "insights": {
        "summary": "Analysis of 42 signals reveals...",
        "key_insights": [
            "Competitors focus heavily on ease-of-use messaging",
            "B2B buyers prioritize integration capabilities",
            "Video content performs 3x better than text"
        ],
        "competitor_strategies": { ... },
        "audience_insights": { ... },
        "messaging_patterns": { ... },
        "confidence_score": 0.85
    },
    "created_at": "2025-10-24T23:40:00",
    "completed_at": "2025-10-24T23:40:45"
}
```

## Authentication

All endpoints (except `/auth/register`, `/auth/login`, and `/health`) require JWT authentication.

**Token Lifecycle:**
1. Login → Receive `access_token`
2. Token saved automatically in collection variable
3. Token used in `Authorization: Bearer {token}` header
4. Token expires after 30 minutes
5. Re-login to get new token

**Manual Token Override:**
- Collection → Variables → `access_token` → Update value

## Testing Tips

### Sequential Testing
Run folders in order for best results:
1. Authentication
2. Campaigns
3. Signals
4. AI Analysis

### Automated Tests
Each request includes tests that automatically:
- Save response variables (IDs, tokens)
- Validate response structure
- Check response times

### Debugging
- Check **Console** (bottom-left) for logs
- Use **Tests** tab to see test results
- Enable **Postman Console** for detailed request/response inspection

## Troubleshooting

### "Unauthorized" Errors
- Token expired → Re-run **Login** request
- Token missing → Check `access_token` variable
- Wrong workspace → Verify `workspace_id`

### "Not Found" Errors
- Campaign not created → Run **Create Campaign** first
- Wrong ID → Check collection variables
- Deleted resource → Create new one

### Signal Collection Failures
- Invalid API key → Check `.env` file has `SEARCHAPI_KEY`
- Rate limit → Wait and retry
- No signals found → Check campaign brief has valid data

### Analysis Failures
- No signals → Run **Collect Signals** first
- LLM API error → Check `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in `.env`
- Timeout → Use `async_mode: true` for large datasets

## Advanced Usage

### Custom Environments

Create environment for different setups:

**Local:**
```
base_url: http://localhost:8000
email: local@test.com
```

**Staging:**
```
base_url: https://staging-api.fieldcraft.com
email: staging@company.com
```

**Production:**
```
base_url: https://api.fieldcraft.com
email: prod@company.com
```

### Batch Testing

Use **Collection Runner** to:
1. Run all requests sequentially
2. Test with different datasets
3. Generate test reports

### CI/CD Integration

```bash
# Run collection via Newman (Postman CLI)
newman run Fieldcraft_API.postman_collection.json \
  --environment production.json \
  --reporters cli,json
```

## API Rate Limits

- Signal collection: 100ms between requests (handled automatically)
- LLM calls: 500ms between requests (handled automatically)
- Authentication: No limit

## Support

- **API Documentation**: http://localhost:8000/docs
- **Issues**: https://github.com/yourorg/fieldcraft/issues
- **Email**: support@fieldcraft.com

---

**Version**: 1.0.0
**Last Updated**: October 2025
**API Version**: v1
