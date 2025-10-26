# Strategic Brief API

Generate and manage long-form strategic briefs that synthesize campaign intelligence.

## POST `/api/v1/campaigns/{campaign_id}/strategic-brief`

Create a new brief using AI. Supports synchronous or background generation.

### Request Body

```json
{
  "llm_provider": "claude",
  "include_analysis_ids": ["UUID", "UUID"],
  "custom_instructions": "Focus on enterprise SaaS buyers",
  "async_mode": false
}
```

- `llm_provider` *(string, default `claude`)* – AI provider to use.
- `include_analysis_ids` *(array of UUIDs, optional)* – restrict the analyses considered.
- `custom_instructions` *(string, optional)* – additional creative or strategic guidance.
- `async_mode` *(boolean, default `false`)* – if `true`, queues a background job and returns a `pending` record.

### Success Response `200 OK`

```json
{
  "id": "UUID",
  "campaign_id": "UUID",
  "status": "completed",
  "version": 1,
  "content": {
    "executive_summary": "...",
    "market_context": "...",
    "audience_deep_dive": { "...": "..." },
    "channel_strategy": [],
    "creative_direction": [],
    "success_metrics": []
  },
  "custom_instructions": "Focus on enterprise SaaS buyers",
  "llm_provider": "claude",
  "llm_model": "claude-3-sonnet",
  "tokens_used": 41230,
  "error_message": null,
  "created_at": "ISO-8601 timestamp",
  "updated_at": "ISO-8601 timestamp"
}
```

If background generation fails, `status` becomes `failed` and `error_message` is populated.

## GET `/api/v1/campaigns/{campaign_id}/strategic-briefs`

List briefs for a campaign (newest first).

### Query Parameters

- `limit` *(integer, default 10)* – maximum briefs to return.

### Success Response `200 OK`

```json
[
  {
    "id": "UUID",
    "campaign_id": "UUID",
    "status": "completed",
    "version": 1,
    "content": {
      "executive_summary": "...",
      "channel_strategy": []
    },
    "custom_instructions": null,
    "llm_provider": "claude",
    "llm_model": "claude-3-sonnet",
    "tokens_used": 38920,
    "error_message": null,
    "created_at": "ISO-8601 timestamp",
    "updated_at": "ISO-8601 timestamp"
  }
]
```

## GET `/api/v1/strategic-briefs/{brief_id}`

Retrieve a brief by ID after verifying workspace ownership.

### Success Response `200 OK`

Same structure as a single entry above.

## DELETE `/api/v1/strategic-briefs/{brief_id}`

Delete a stored brief.

### Success Response `204 No Content`

Empty body.
