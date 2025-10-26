# Analytics API

Provides aggregated metrics and trends for dashboards.

## GET `/api/v1/analytics/dashboard`

Return workspace-level KPIs, weekly timelines, and signal source distribution.

### Success Response `200 OK`

```json
{
  "stats": {
    "total_campaigns": 12,
    "total_signals": 438,
    "total_analyses": 9,
    "total_briefs": 6,
    "campaigns_growth": 18.5,
    "signals_growth": 22.1,
    "analyses_growth": 5.3,
    "briefs_growth": 12.0
  },
  "campaigns_timeline": [
    {
      "period": "Week 1",
      "count": 3,
      "date": "2024-03-18"
    },
    {
      "period": "Week 2",
      "count": 2,
      "date": "2024-03-25"
    }
  ],
  "signal_sources": [
    {
      "source": "Google",
      "count": 210,
      "percentage": 47.9
    },
    {
      "source": "Meta Ads",
      "count": 90,
      "percentage": 20.5
    }
  ]
}
```

- `stats` – totals for the last 30 days with growth vs. the prior 30 days.
- `campaigns_timeline` – four data points (one per recent week).
- `signal_sources` – top sources ranked by volume with relative percentages.
