# Signals API

Signal endpoints orchestrate external research cartridges, enrichment, and retrieval of signal intelligence.

## POST `/api/v1/campaigns/{campaign_id}/signals/collect`

Run one or more cartridges to gather fresh signals for a campaign.

### Request Body

```json
{
  "cartridge_names": ["google_serp", "youtube", "meta_ads"],
  "max_queries_per_cartridge": 5
}
```

- `cartridge_names` *(array of strings, optional)* – restrict collection to these cartridges. Omit to run all available cartridges.
- `max_queries_per_cartridge` *(integer, default 10)* – cap queries per cartridge.

### Success Response `200 OK`

```json
{
  "campaign_id": "UUID",
  "cartridges_run": 3,
  "total_signals": 42,
  "deduplicated_urls": 18,
  "errors": [
    {
      "cartridge": "youtube",
      "message": "API quota reached"
    }
  ],
  "timestamp": "ISO-8601 timestamp"
}
```

## POST `/api/v1/campaigns/{campaign_id}/signals/enrich`

Derive advanced metadata (entities, sentiment, topics) for the latest signals.

### Query Parameters

- `limit` *(integer, optional)* – only enrich the most recent *n* signals.

### Success Response `200 OK`

```json
{
  "created": 12,
  "processed": 12,
  "skipped": 3
}
```

## GET `/api/v1/campaigns/{campaign_id}/signals`

List signal records for a campaign with optional filtering.

### Query Parameters

- `min_relevance` *(float, default 0.0)* – minimum relevance score (0–1).
- `source` *(string, optional)* – filter by origin (e.g., `google`, `meta_ads`).
- `limit` *(integer, default 100)* – maximum signals returned.

### Success Response `200 OK`

```json
[
  {
    "id": "UUID",
    "campaign_id": "UUID",
    "source": "google",
    "search_method": "serp_organic",
    "query": "marketing automation platforms 2024",
    "evidence": [
      {
        "url": "https://example.com",
        "timestamp": "2024-04-05T12:00:00Z",
        "snippet": "Analysts rank...",
        "metadata": {
          "position": 1
        }
      }
    ],
    "relevance_score": 0.82,
    "created_at": "ISO-8601 timestamp"
  }
]
```

## GET `/api/v1/campaigns/signals/{signal_id}/enrichments`

Return enrichment records associated with a single signal.

### Success Response `200 OK`

```json
[
  {
    "id": "UUID",
    "signal_id": "UUID",
    "enrichment_type": "entity_extraction",
    "entities": ["automation", "workflow"],
    "sentiment": 0.41,
    "trend_score": 0.76,
    "features": {
      "key_topics": 0.94
    },
    "created_at": "ISO-8601 timestamp"
  }
]
```

## GET `/api/v1/campaigns/cartridges`

List cartridge identifiers that can be supplied to the collect endpoint.

### Success Response `200 OK`

```json
[
  "google_serp",
  "meta_ads",
  "linkedin_ads",
  "reddit_organic",
  "youtube"
]
```
