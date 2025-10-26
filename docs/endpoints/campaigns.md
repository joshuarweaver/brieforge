# Campaigns API

Campaign endpoints manage core campaign records and expose blueprint generation.

## GET `/api/v1/campaigns`

List campaigns in the authenticated workspace.

### Query Parameters

- `skip` *(integer, optional, default 0)* – offset for pagination.
- `limit` *(integer, optional, default 100)* – maximum records to return.

### Success Response `200 OK`

```json
[
  {
    "id": "UUID",
    "workspace_id": "UUID",
    "name": "Marketing Automation Campaign",
    "status": "draft",
    "brief": {
      "goal": "increase brand awareness",
      "audiences": ["B2B marketers", "startup founders"],
      "offer": "automation suite",
      "competitors": ["HubSpot", "Marketo"],
      "channels": ["linkedin", "google", "youtube"],
      "budget_band": "$10k-50k/month",
      "voice_constraints": "professional yet approachable"
    },
    "created_at": "ISO-8601 timestamp",
    "updated_at": "ISO-8601 timestamp"
  }
]
```

## POST `/api/v1/campaigns`

Create a new campaign in the current workspace.

### Request Body

```json
{
  "name": "Marketing Automation Campaign",
  "brief": {
    "goal": "increase brand awareness",
    "audiences": ["B2B marketers", "startup founders", "growth teams"],
    "offer": "marketing automation",
    "competitors": ["HubSpot", "Marketo", "Pardot"],
    "channels": ["linkedin", "google", "youtube"],
    "budget_band": "$10k-50k/month",
    "voice_constraints": "professional yet approachable, data-driven"
  }
}
```

### Success Response `201 Created`

Same shape as the GET response body for a single campaign.

## GET `/api/v1/campaigns/{campaign_id}`

Retrieve a campaign by ID. Returns `404` if not found in workspace.

### Success Response `200 OK`

Campaign JSON object as described above.

## PUT or PATCH `/api/v1/campaigns/{campaign_id}`

Update campaign metadata or brief details. Provide only fields that should change.

### Request Body

```json
{
  "name": "Updated Campaign Name",
  "status": "analyzing",
  "brief": {
    "channels": ["linkedin", "google", "youtube", "meta"],
    "voice_constraints": "keep it data-forward"
  }
}
```

### Success Response `200 OK`

Updated campaign record.

## DELETE `/api/v1/campaigns/{campaign_id}`

Remove a campaign from the workspace.

### Success Response `204 No Content`

Empty body.

---

## POST `/api/v1/campaigns/{campaign_id}/blueprint`

Generate a campaign blueprint using collected signals and analyses.

### Query Parameters

- `persist` *(boolean, default `true`)* – store the generated blueprint artifact.
- `use_llm` *(boolean, optional)* – override the server default for AI-driven generation.

### Success Response `200 OK`

```json
{
  "artifact_id": "UUID | null",
  "campaign_id": "UUID",
  "generated_at": "ISO-8601 timestamp",
  "summary": "High-level summary of the recommended go-to-market approach.",
  "insights": {
    "top_entities": ["automation software", "B2B marketing"],
    "trending_topics": ["workflow orchestration"],
    "sentiment_distribution": {
      "positive": 0.54,
      "neutral": 0.37,
      "negative": 0.09
    }
  },
  "audience_hypotheses": [
    {
      "audience": "Growth-stage B2B marketing leaders",
      "focus_entities": ["automation platforms"],
      "pain_points": ["inefficient lead follow-up"],
      "language_notes": ["ROI, pipeline velocity"],
      "supporting_signals": ["UUID", "UUID"]
    }
  ],
  "value_propositions": [
    {
      "statement": "Launch intelligent workflows that convert pipeline faster.",
      "supporting_entities": ["Automation Leader Report"],
      "trend_score": 0.82,
      "proof_points": ["Case study stat", "Benchmark delta"]
    }
  ],
  "messaging_pillars": [
    {
      "pillar": "Proven Revenue Acceleration",
      "key_messages": [
        "Automate hand-offs across teams",
        "Surface real-time performance insights"
      ],
      "supporting_urls": ["https://example.com"],
      "relevance_score": 0.91
    }
  ],
  "draft_assets": [
    {
      "id": "UUID",
      "platform": "linkedin",
      "objective": "conversion",
      "audience_focus": ["Growth-stage B2B marketing leaders"],
      "headline": "Engage your buyers before competitors do",
      "primary_text": "Automate outreach ...",
      "cta": "Book Demo",
      "supporting_signals": ["UUID"],
      "creative_hooks": ["Automated orchestration for B2B revenue"],
      "variations": [
        {
          "headline": "Engage your buyers before competitors do",
          "primary_text": "Automate outreach ...",
          "cta": "Get Started"
        }
      ]
    }
  ],
  "next_actions": [
    "Schedule executive review",
    "Align offer positioning with sales"
  ],
  "metadata": {
    "generation_method": "llm" ,
    "asset_counts": {
      "linkedin": 5,
      "google": 5,
      "youtube": 5
    },
    "rule_based_preview": { "summary": "..." },
    "llm_used": true
  }
}
```

## GET `/api/v1/campaigns/{campaign_id}/blueprints`

List persisted blueprints for a campaign.

### Success Response `200 OK`

```json
[
  {
    "id": "UUID",
    "campaign_id": "UUID",
    "summary": "Snapshot summary",
    "created_at": "ISO-8601 timestamp"
  }
]
```

## GET `/api/v1/campaigns/{campaign_id}/blueprints/{blueprint_id}`

Fetch a specific stored blueprint artifact.

### Success Response `200 OK`

Same structure as the generation response, with `artifact_id` populated.
