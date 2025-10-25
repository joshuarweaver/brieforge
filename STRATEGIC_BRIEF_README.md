# Strategic Brief & Audience Insights API

## Overview

The Fieldcraft API now includes two powerful new endpoints for AI-driven strategic planning:

1. **Strategic Brief Generation** - Creates comprehensive 2-page marketing strategy documents
2. **Audience Insights** - Provides deep audience intelligence and profiling

---

## 1. Strategic Brief Generation

### Endpoint
`POST /api/v1/campaigns/{campaign_id}/strategic-brief`

### Description
Generates a comprehensive 2-page strategic brief that synthesizes campaign data, signal intelligence, and AI analysis into a professional marketing strategy document.

### Prerequisites
- Campaign must have completed signal analyses
- At least one signal analysis with status "completed"

### Request Body
```json
{
  "llm_provider": "claude",  // or "openai"
  "include_analysis_ids": ["uuid1", "uuid2"],  // Optional: specific analyses to include
  "custom_instructions": "Focus on B2B SaaS positioning",  // Optional
  "async_mode": false  // true = background processing
}
```

### Response
```json
{
  "id": "brief-uuid",
  "campaign_id": "campaign-uuid",
  "status": "completed",  // or "pending", "failed"
  "version": 1,
  "content": {
    "full_text": "# PAGE 1: MARKET LANDSCAPE...",
    "sections": {
      "Executive Summary": "...",
      "Market Context": "...",
      "Target Audience Deep Dive": "...",
      "Messaging Strategy": "...",
      "Channel Strategy & Tactics": "...",
      "Creative Direction": "...",
      "Success Metrics": "..."
    },
    "metadata": {
      "signal_count": 45,
      "analyses_used": 3,
      "generated_at": "2025-10-25T00:00:00"
    }
  },
  "llm_provider": "claude",
  "llm_model": "claude-3-5-sonnet-20241022",
  "tokens_used": 3500,
  "created_at": "2025-10-25T00:00:00",
  "updated_at": "2025-10-25T00:00:00"
}
```

### Strategic Brief Structure

#### PAGE 1: Market Landscape & Strategic Positioning
- **Executive Summary**: Concise overview (3-4 sentences)
- **Market Context**: Trends, competitive landscape, opportunities
- **Target Audience Deep Dive**: Segments, pain points, motivations, decision factors

#### PAGE 2: Strategic Execution Plan
- **Messaging Strategy**: Value prop, key messages, proof points
- **Channel Strategy & Tactics**: Recommended channels, budget allocation
- **Creative Direction**: Visual themes, ad formats, creative testing
- **Success Metrics**: KPIs, benchmarks, measurement approach

### Additional Endpoints

**List Briefs**
```
GET /api/v1/campaigns/{campaign_id}/strategic-briefs?limit=10
```

**Get Specific Brief**
```
GET /api/v1/strategic-briefs/{brief_id}
```

**Delete Brief**
```
DELETE /api/v1/strategic-briefs/{brief_id}
```

---

## 2. Audience Insights

### Endpoint
`POST /api/v1/campaigns/{campaign_id}/audience-insights`

### Description
Generates detailed audience intelligence including demographics, psychographics, pain points, motivations, objections, decision-making process, media habits, and messaging preferences.

### Prerequisites
- Campaign must have completed signal analyses

### Request Body
```json
{
  "llm_provider": "claude",  // or "openai"
  "focus_areas": ["pain_points", "motivations", "objections"]  // Optional
}
```

### Response
```json
{
  "campaign_id": "campaign-uuid",
  "insights": {
    "B2B marketers": {
      "demographics_firmographics": {
        "age_range": "28-45",
        "job_titles": ["Marketing Manager", "CMO", "Growth Lead"],
        "company_size": "50-500 employees",
        "location": "North America, Western Europe"
      },
      "psychographics": {
        "values": ["Innovation", "ROI-driven", "Efficiency"],
        "professional_identity": "Strategic thinkers who value data",
        "behavioral_traits": ["Early adopters", "Tech-savvy", "Collaborative"]
      },
      "pain_points": [
        {
          "pain": "Difficulty proving marketing ROI",
          "impact": "Budget cuts and lack of executive support",
          "current_solutions": "Spreadsheets, disconnected analytics tools"
        },
        {
          "pain": "Too many disparate tools in martech stack",
          "impact": "Wasted time, data silos, team frustration",
          "current_solutions": "Manual data consolidation"
        }
      ],
      "motivations": {
        "goals": ["Increase pipeline contribution", "Demonstrate clear ROI"],
        "success_metrics": ["MQL-to-SQL conversion", "Attribution accuracy"],
        "emotional_drivers": ["Career advancement", "Team recognition"]
      },
      "decision_making_process": {
        "research_methods": ["Peer recommendations", "G2/Capterra reviews"],
        "influencers": ["Marketing ops team", "CFO", "Sales leadership"],
        "buying_journey": "3-6 months from awareness to purchase",
        "stages": ["Problem awareness", "Solution education", "Vendor comparison", "Trial"]
      },
      "objections_concerns": {
        "barriers": ["Implementation complexity", "Change management"],
        "risk_factors": ["Data security", "Integration challenges"],
        "alternatives": ["In-house solution", "Incumbent vendor"]
      },
      "media_consumption": {
        "platforms": ["LinkedIn", "Marketing blogs", "Industry podcasts"],
        "content_formats": ["Case studies", "Webinars", "Short-form video"],
        "trusted_sources": ["Industry thought leaders", "Peer communities"],
        "social_usage": "Professional networking, content sharing"
      },
      "language_communication": {
        "terminology": ["Attribution", "Pipeline", "CAC", "LTV"],
        "tone": "Professional but approachable, data-driven",
        "resonates": "Efficiency gains, ROI proof, competitive advantage",
        "avoid": "Overly technical jargon, empty promises"
      }
    }
  },
  "metadata": {
    "analyses_used": 2,
    "llm_provider": "claude",
    "llm_model": "claude-3-5-sonnet-20241022",
    "tokens_used": 2500
  }
}
```

### Use Cases

1. **Campaign Planning**: Deep understanding before creating campaigns
2. **Messaging Development**: Craft resonant value propositions
3. **Channel Selection**: Choose channels where audience is active
4. **Creative Briefing**: Inform designers and copywriters
5. **Sales Enablement**: Equip sales teams with objection handling
6. **Product Marketing**: Inform positioning and packaging

---

## Workflow Example

### Complete Campaign Intelligence Workflow

1. **Create Campaign**
   ```bash
   POST /api/v1/campaigns
   ```

2. **Collect Signals**
   ```bash
   POST /api/v1/campaigns/{id}/signals/collect
   ```

3. **Run Signal Analysis**
   ```bash
   POST /api/v1/campaigns/{id}/analyze
   ```

4. **Get Audience Insights** (NEW)
   ```bash
   POST /api/v1/campaigns/{id}/audience-insights
   ```

5. **Generate Strategic Brief** (NEW)
   ```bash
   POST /api/v1/campaigns/{id}/strategic-brief
   ```

6. **Review & Export**
   - Download brief as PDF/Word
   - Share with team
   - Use insights for campaign execution

---

## Tips & Best Practices

### Strategic Brief Generation

- **Run multiple analyses first**: Brief quality improves with more analysis data
- **Use custom instructions**: Guide the AI toward specific industry/use case focus
- **Version control**: Keep multiple versions as strategy evolves
- **Async mode for production**: Use background processing for better UX

### Audience Insights

- **Focus areas**: Narrow scope for specific intelligence needs
- **Cross-reference with brief**: Use insights to validate brief recommendations
- **Update periodically**: Re-run as you collect more signals
- **Export for teams**: Share with creative, sales, and product teams

---

## Error Handling

### Common Errors

**400 Bad Request**
```json
{
  "detail": "No completed signal analyses found. Please run signal analysis first."
}
```
Solution: Run `/analyze` endpoint first

**404 Not Found**
```json
{
  "detail": "Campaign {id} not found"
}
```
Solution: Verify campaign ID and workspace access

**500 Internal Server Error**
```json
{
  "detail": "Brief generation failed: [error details]"
}
```
Solution: Check LLM API keys and rate limits

---

## API Keys Required

Ensure these environment variables are set:

```bash
ANTHROPIC_API_KEY=sk-ant-...  # For Claude
OPENAI_API_KEY=sk-...         # For OpenAI/GPT
```

---

## Rate Limits & Costs

- **Strategic Brief**: ~3000-4000 tokens per generation
- **Audience Insights**: ~2000-3000 tokens per generation
- Async mode recommended for production to avoid timeouts
- Consider caching results to minimize API costs

---

## Next Steps

1. Test endpoints in Postman
2. Review generated strategic briefs
3. Validate audience insights accuracy
4. Integrate into your workflow
5. Provide feedback for improvements
