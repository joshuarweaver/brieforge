# Dashboard Enhancement - Simplified Version
## Using shadcn/ui Charts (Recharts)

Clean, minimal charts that surface actionable insights without overdesigning.

---

## Key Widgets to Add

### 1. **Campaign Status Distribution**
**What it shows**: How many campaigns in each status (draft, gathering_signals, analyzing, generating, completed, failed)

**Chart Type**: Simple Bar Chart (horizontal)

**shadcn Component**: `BarChart` from recharts

```tsx
import { Bar, BarChart, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

const chartData = [
  { status: "Draft", count: 12 },
  { status: "Gathering", count: 8 },
  { status: "Analyzing", count: 6 },
  { status: "Generating", count: 4 },
  { status: "Completed", count: 15 },
  { status: "Failed", count: 2 },
]

const chartConfig = {
  count: {
    label: "Campaigns",
    color: "hsl(var(--chart-1))",
  },
}

<ChartContainer config={chartConfig} className="h-[200px]">
  <BarChart data={chartData} layout="horizontal">
    <XAxis type="number" />
    <YAxis dataKey="status" type="category" />
    <ChartTooltip content={<ChartTooltipContent />} />
    <Bar dataKey="count" fill="var(--color-count)" radius={4} />
  </BarChart>
</ChartContainer>
```

**API**: `/api/v1/analytics/campaign-status-distribution`

---

### 2. **Signal Quality Metrics**
**What it shows**: Average relevance score, high-quality % (>0.7), signals per campaign

**Chart Type**: Simple stat cards (no chart)

**Just clean numbers**:
```tsx
<div className="grid grid-cols-3 gap-4">
  <div className="text-center">
    <div className="text-[32px] font-semibold">0.72</div>
    <div className="text-[13px] text-muted-foreground">Avg Relevance</div>
  </div>
  <div className="text-center">
    <div className="text-[32px] font-semibold">65%</div>
    <div className="text-[13px] text-muted-foreground">High Quality</div>
  </div>
  <div className="text-center">
    <div className="text-[32px] font-semibold">147</div>
    <div className="text-[13px] text-muted-foreground">Avg per Campaign</div>
  </div>
</div>
```

**API**: `/api/v1/analytics/intelligence-quality`

---

### 3. **LLM Usage**
**What it shows**: Token usage by provider (Claude vs OpenAI)

**Chart Type**: Pie Chart or simple progress bars

**shadcn Component**: `PieChart` from recharts (simple, no 3D)

```tsx
import { Pie, PieChart } from "recharts"

const chartData = [
  { provider: "Claude", tokens: 1923847, fill: "hsl(var(--chart-1))" },
  { provider: "OpenAI", tokens: 923446, fill: "hsl(var(--chart-2))" },
]

const chartConfig = {
  tokens: { label: "Tokens" },
  claude: { label: "Claude", color: "hsl(var(--chart-1))" },
  openai: { label: "OpenAI", color: "hsl(var(--chart-2))" },
}

<ChartContainer config={chartConfig} className="h-[200px]">
  <PieChart>
    <ChartTooltip content={<ChartTooltipContent hideLabel />} />
    <Pie data={chartData} dataKey="tokens" nameKey="provider" />
  </PieChart>
</ChartContainer>
```

**API**: `/api/v1/analytics/llm-usage`

---

### 4. **Top Competitors**
**What it shows**: Most frequently tracked competitors from campaign briefs

**Chart Type**: Simple list (no chart needed)

```tsx
<div className="space-y-2">
  {competitors.map((comp, i) => (
    <div key={i} className="flex justify-between p-3 rounded-lg border border-slate-200">
      <span className="text-[13px] font-medium">{comp.name}</span>
      <span className="text-[12px] text-muted-foreground">{comp.count} campaigns</span>
    </div>
  ))}
</div>
```

**API**: `/api/v1/analytics/competitors`

---

### 5. **Top Audiences**
**What it shows**: Most frequently targeted audience segments

**Chart Type**: Horizontal bar chart

**shadcn Component**: `BarChart`

```tsx
const chartData = [
  { audience: "B2B Marketing Managers", count: 12 },
  { audience: "Software Developers", count: 9 },
  { audience: "Sales Leaders", count: 7 },
]

<ChartContainer config={chartConfig} className="h-[200px]">
  <BarChart data={chartData} layout="horizontal">
    <XAxis type="number" />
    <YAxis dataKey="audience" type="category" width={150} />
    <ChartTooltip content={<ChartTooltipContent />} />
    <Bar dataKey="count" fill="hsl(var(--chart-1))" radius={4} />
  </BarChart>
</ChartContainer>
```

**API**: `/api/v1/analytics/audiences`

---

### 6. **Channel Distribution**
**What it shows**: Which marketing channels are selected in campaign briefs

**Chart Type**: Simple bar chart or list

**shadcn Component**: `BarChart`

```tsx
const chartData = [
  { channel: "LinkedIn", count: 18 },
  { channel: "Facebook", count: 14 },
  { channel: "Instagram", count: 11 },
  { channel: "YouTube", count: 8 },
]

<ChartContainer config={chartConfig} className="h-[200px]">
  <BarChart data={chartData}>
    <XAxis dataKey="channel" />
    <YAxis />
    <ChartTooltip content={<ChartTooltipContent />} />
    <Bar dataKey="count" fill="hsl(var(--chart-1))" radius={4} />
  </BarChart>
</ChartContainer>
```

**API**: `/api/v1/analytics/channels`

---

### 7. **Asset Ratings** (if data exists)
**What it shows**: Average rating by platform

**Chart Type**: Simple bar chart

```tsx
const chartData = [
  { platform: "LinkedIn", rating: 4.2 },
  { platform: "Facebook", rating: 3.8 },
  { platform: "Instagram", rating: 4.5 },
]

<ChartContainer config={chartConfig} className="h-[200px]">
  <BarChart data={chartData}>
    <XAxis dataKey="platform" />
    <YAxis domain={[0, 5]} />
    <ChartTooltip content={<ChartTooltipContent />} />
    <Bar dataKey="rating" fill="hsl(var(--chart-1))" radius={4} />
  </BarChart>
</ChartContainer>
```

**API**: `/api/v1/analytics/asset-ratings`

---

## Simplified Layout

```
┌─────────────────────────────────────────┐
│ Stats (4 cards - existing, enhanced)    │
└─────────────────────────────────────────┘

┌──────────────────┐ ┌──────────────────┐
│ Campaigns Over   │ │ Signal Sources   │
│ Time (existing)  │ │ (existing)       │
└──────────────────┘ └──────────────────┘

┌──────────────────┐ ┌──────────────────┐
│ Campaign Status  │ │ LLM Usage        │
│ Distribution     │ │ (Pie Chart)      │
└──────────────────┘ └──────────────────┘

┌──────────────────┐ ┌──────────────────┐
│ Top Competitors  │ │ Top Audiences    │
│ (List)           │ │ (Bar Chart)      │
└──────────────────┘ └──────────────────┘

┌──────────────────┐ ┌──────────────────┐
│ Channel Mix      │ │ Signal Quality   │
│ (Bar Chart)      │ │ (Stats)          │
└──────────────────┘ └──────────────────┘

┌─────────────────────────────────────────┐
│ Your Campaigns (existing)                │
└─────────────────────────────────────────┘
```

---

## Required Backend Endpoints

### 1. `/api/v1/analytics/campaign-status`
```python
@router.get("/campaign-status")
def get_campaign_status(workspace_id: UUID, db: Session):
    """Get campaign count by status."""
    status_counts = db.query(
        Campaign.status,
        func.count(Campaign.id).label('count')
    ).filter(
        Campaign.workspace_id == workspace_id
    ).group_by(Campaign.status).all()

    return {"statuses": [{"status": s, "count": c} for s, c in status_counts]}
```

### 2. `/api/v1/analytics/intelligence-quality`
```python
@router.get("/intelligence-quality")
def get_intelligence_quality(workspace_id: UUID, db: Session):
    """Get signal quality metrics."""
    signals = db.query(Signal).join(Campaign).filter(
        Campaign.workspace_id == workspace_id
    ).all()

    avg_relevance = sum(s.relevance_score for s in signals) / len(signals) if signals else 0
    high_quality_pct = len([s for s in signals if s.relevance_score > 0.7]) / len(signals) * 100 if signals else 0

    campaign_count = db.query(func.count(Campaign.id)).filter(
        Campaign.workspace_id == workspace_id
    ).scalar()

    avg_per_campaign = len(signals) / campaign_count if campaign_count else 0

    return {
        "avg_relevance": round(avg_relevance, 2),
        "high_quality_percentage": round(high_quality_pct, 1),
        "avg_per_campaign": round(avg_per_campaign, 0)
    }
```

### 3. `/api/v1/analytics/llm-usage`
```python
@router.get("/llm-usage")
def get_llm_usage(workspace_id: UUID, db: Session):
    """Get LLM usage by provider."""
    usage = db.query(
        SignalAnalysis.llm_provider,
        func.sum(SignalAnalysis.tokens_used).label('total_tokens')
    ).join(Campaign).filter(
        Campaign.workspace_id == workspace_id
    ).group_by(SignalAnalysis.llm_provider).all()

    return {"providers": [{"provider": p, "tokens": t} for p, t in usage]}
```

### 4. `/api/v1/analytics/competitors`
```python
@router.get("/competitors")
def get_top_competitors(workspace_id: UUID, db: Session):
    """Get most frequently tracked competitors."""
    campaigns = db.query(Campaign).filter(
        Campaign.workspace_id == workspace_id
    ).all()

    competitor_counts = {}
    for campaign in campaigns:
        if 'competitors' in campaign.brief:
            for comp in campaign.brief['competitors']:
                competitor_counts[comp] = competitor_counts.get(comp, 0) + 1

    sorted_competitors = sorted(competitor_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return {"competitors": [{"name": name, "count": count} for name, count in sorted_competitors]}
```

### 5. `/api/v1/analytics/audiences`
```python
@router.get("/audiences")
def get_top_audiences(workspace_id: UUID, db: Session):
    """Get most frequently targeted audiences."""
    campaigns = db.query(Campaign).filter(
        Campaign.workspace_id == workspace_id
    ).all()

    audience_counts = {}
    for campaign in campaigns:
        if 'audiences' in campaign.brief:
            for aud in campaign.brief['audiences']:
                audience_counts[aud] = audience_counts.get(aud, 0) + 1

    sorted_audiences = sorted(audience_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return {"audiences": [{"name": name, "count": count} for name, count in sorted_audiences]}
```

### 6. `/api/v1/analytics/channels`
```python
@router.get("/channels")
def get_channel_distribution(workspace_id: UUID, db: Session):
    """Get marketing channel distribution."""
    campaigns = db.query(Campaign).filter(
        Campaign.workspace_id == workspace_id
    ).all()

    channel_counts = {}
    for campaign in campaigns:
        if 'channels' in campaign.brief:
            for ch in campaign.brief['channels']:
                channel_counts[ch] = channel_counts.get(ch, 0) + 1

    sorted_channels = sorted(channel_counts.items(), key=lambda x: x[1], reverse=True)

    return {"channels": [{"name": name, "count": count} for name, count in sorted_channels]}
```

---

## Design Principles

1. **Use shadcn/ui default colors**: `hsl(var(--chart-1))`, `hsl(var(--chart-2))`, etc.
2. **Minimal styling**: Let Recharts handle it, don't override
3. **Clean tooltips**: Use `ChartTooltipContent` as-is
4. **Simple legends**: Only when necessary
5. **No gradients on charts**: Solid colors only
6. **Standard chart heights**: `h-[200px]` or `h-[250px]`
7. **Consistent card padding**: `p-8`

---

## Next Steps

1. Create backend analytics endpoints (simple queries)
2. Add TypeScript types for responses
3. Build widgets using shadcn chart components
4. Test with real data
5. Add to dashboard page in 2-column grid
