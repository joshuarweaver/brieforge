# Exports API

Build export-ready payloads for ads platforms using the latest blueprint data.

## POST `/api/v1/campaigns/{campaign_id}/exports/{platform}`

Generate an export payload for the specified ad platform.

### Path Parameters

- `campaign_id` – target campaign UUID.
- `platform` – export adapter (e.g., `meta`, `google`, `linkedin`).

### Query Parameters

- `dry_run` *(boolean, default `true`)* – if `true`, no external API calls are made. Set to `false` to perform live delivery (when implemented).

### Success Response `200 OK`

```json
{
  "platform": "meta",
  "dry_run": true,
  "payload": {
    "campaign": { "...": "..." },
    "ad_sets": [],
    "ads": []
  },
  "blueprint": {
    "artifact_id": "UUID",
    "summary": "Key recommendations",
    "draft_assets": [
      {
        "platform": "meta",
        "headline": "Inspire buyers to act faster",
        "primary_text": "Capture demand with...",
        "cta": "Learn More"
      }
    ]
  }
}
```

Errors:
- `404 Not Found` if the campaign does not exist in the workspace.
- `400 Bad Request` if the platform is unsupported.
