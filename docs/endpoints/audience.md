# Audience Insights API

Generate deep audience intelligence by combining campaign data, prior analyses, and LLM-driven synthesis.

## POST `/api/v1/campaigns/{campaign_id}/audience-insights`

Produce a structured audience insights bundle.

### Request Body

```json
{
  "llm_provider": "claude",
  "focus_areas": ["pain_points", "motivations", "objections"]
}
```

- `llm_provider` *(string, default `claude`)* – AI provider used for synthesis.
- `focus_areas` *(array of strings, optional)* – limit output to specific sections.

### Success Response `200 OK`

```json
{
  "campaign_id": "UUID",
  "insights": {
    "audience_profiles": [
      {
        "segment": "Growth-stage B2B marketing leaders",
        "demographics": { "...": "..." },
        "pain_points": ["..."],
        "motivations": ["..."],
        "objections": ["..."],
        "media_consumption": ["..."]
      }
    ],
    "recommended_messaging": ["..."]
  },
  "metadata": {
    "analyses_used": 3,
    "llm_provider": "claude",
    "llm_model": "claude-3-sonnet",
    "tokens_used": 21560
  }
}
```

Errors:
- `400 Bad Request` if no completed signal analyses exist for the campaign.
- `404 Not Found` if the campaign is outside the requester’s workspace.
