# Signal Analysis API

Analyze collected signals with AI to generate insights and strategy artifacts.

## POST `/api/v1/campaigns/{campaign_id}/analyze`

Trigger a new analysis run for a campaign.

### Request Body

```json
{
  "analysis_type": "comprehensive",
  "llm_provider": "claude",
  "max_signals": 50,
  "min_relevance": 0.3,
  "async_mode": false
}
```

- `analysis_type` *(string, default `comprehensive`)* – one of `comprehensive`, `competitor`, `audience`, `messaging`, `creative`, `trends`.
- `llm_provider` *(string, default `claude`)* – currently supports `claude` or `openai`.
- `max_signals` *(integer, optional)* – cap the number of signals analyzed.
- `min_relevance` *(float, default 0.0)* – filter out lower-scoring signals.
- `async_mode` *(boolean, default `false`)* – run in background; returns immediately in `pending` status.

### Success Response `200 OK`

```json
{
  "id": "UUID",
  "campaign_id": "UUID",
  "analysis_type": "comprehensive",
  "status": "completed",
  "llm_provider": "claude",
  "llm_model": "claude-3-sonnet",
  "tokens_used": 28194,
  "insights": {
    "audience_insights": { "...": "..." },
    "competitor_strategies": [],
    "messaging_patterns": []
  },
  "error_message": null,
  "created_at": "ISO-8601 timestamp",
  "completed_at": "ISO-8601 timestamp | null"
}
```

When `async_mode` is `true`, `status` is `pending` and `completed_at` is `null` until background processing finishes.

## GET `/api/v1/campaigns/{campaign_id}/signal-analyses`

List analyses for a campaign, optionally filtered.

### Query Parameters

- `analysis_type` *(string, optional)* – same enum values as above.
- `status_filter` *(string, optional)* – one of `pending`, `in_progress`, `completed`, `failed`.
- `limit` *(integer, default 10)* – maximum analyses to return.

### Success Response `200 OK`

```json
[
  {
    "id": "UUID",
    "campaign_id": "UUID",
    "analysis_type": "competitor",
    "status": "completed",
    "llm_provider": "claude",
    "llm_model": "claude-3-sonnet",
    "tokens_used": 14560,
    "insights": { "...": "..." },
    "error_message": null,
    "created_at": "ISO-8601 timestamp",
    "completed_at": "ISO-8601 timestamp"
  }
]
```

## GET `/api/v1/signal-analyses/{analysis_id}`

Retrieve a specific analysis record.

### Success Response `200 OK`

Same structure as a single analysis entry above.

## DELETE `/api/v1/signal-analyses/{analysis_id}`

Remove an analysis record from history.

### Success Response `204 No Content`

Empty body.
