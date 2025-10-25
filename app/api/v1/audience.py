"""Audience Insights API endpoints."""
from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, Campaign, SignalAnalysis
from app.services.llm import LLMService, LLMProvider

router = APIRouter()


# Request/Response models
class AudienceInsightsRequest(BaseModel):
    """Request for audience insights."""
    llm_provider: LLMProvider = LLMProvider.CLAUDE
    focus_areas: Optional[list[str]] = None  # e.g., ["pain_points", "motivations", "objections"]


class AudienceInsightsResponse(BaseModel):
    """Audience insights response."""
    campaign_id: UUID
    insights: Dict[str, Any]
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


@router.post(
    "/campaigns/{campaign_id}/audience-insights",
    response_model=AudienceInsightsResponse,
    status_code=status.HTTP_200_OK
)
def get_audience_insights(
    campaign_id: UUID,
    request: AudienceInsightsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate detailed audience insights from campaign data and signal analysis.

    This endpoint provides deep audience intelligence including:
    - **Demographic & Psychographic Profiles**: Who they are
    - **Pain Points & Challenges**: What problems they face
    - **Motivations & Goals**: What drives their decisions
    - **Objections & Concerns**: What holds them back
    - **Decision-Making Process**: How they evaluate solutions
    - **Media Consumption Habits**: Where to reach them
    - **Language & Messaging Preferences**: How to speak to them

    **Parameters:**
    - `llm_provider`: LLM provider (claude or openai)
    - `focus_areas`: Optional list of specific areas to focus on

    **Prerequisites:**
    - Campaign must have completed signal analyses
    """
    # Check campaign exists and belongs to user's workspace
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.workspace_id == current_user.workspace_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found"
        )

    # Get completed analyses
    analyses = db.query(SignalAnalysis).filter(
        SignalAnalysis.campaign_id == campaign_id,
        SignalAnalysis.status == "completed"
    ).order_by(SignalAnalysis.created_at.desc()).all()

    if not analyses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No completed signal analyses found. Please run signal analysis first."
        )

    try:
        # Build context from campaign and analyses
        context = _build_audience_context(campaign, analyses)

        # Generate insights using LLM
        llm = LLMService(provider=request.llm_provider)
        insights = _generate_audience_insights(
            llm,
            context,
            campaign.brief.get('audiences', []),
            request.focus_areas
        )

        return AudienceInsightsResponse(
            campaign_id=campaign_id,
            insights=insights['content'],
            metadata={
                "analyses_used": len(analyses),
                "llm_provider": request.llm_provider.value,
                "llm_model": llm.get_model_name(),
                "tokens_used": insights.get('tokens_used', 0)
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audience insights generation failed: {str(e)}"
        )


def _build_audience_context(campaign: Campaign, analyses: list[SignalAnalysis]) -> str:
    """Build context string for audience insights."""
    context_parts = []

    # Campaign info
    context_parts.append("# CAMPAIGN INFORMATION\n")
    context_parts.append(f"**Goal:** {campaign.brief.get('goal', 'N/A')}\n")
    context_parts.append(f"**Offer/Product:** {campaign.brief.get('offer', 'N/A')}\n")
    context_parts.append(f"**Target Audiences:** {', '.join(campaign.brief.get('audiences', []))}\n")
    context_parts.append(f"**Budget Band:** {campaign.brief.get('budget_band', 'N/A')}\n\n")

    # Analysis insights
    context_parts.append("# MARKET INTELLIGENCE\n\n")

    for analysis in analyses:
        if not analysis.insights:
            continue

        insights = analysis.insights

        # Add audience-specific insights
        if insights.get('audience_insights'):
            context_parts.append(f"## Audience Insights ({analysis.analysis_type.value})\n")
            if isinstance(insights['audience_insights'], dict):
                for key, value in insights['audience_insights'].items():
                    context_parts.append(f"**{key}:** {value}\n\n")
            else:
                context_parts.append(f"{insights['audience_insights']}\n\n")

        # Add relevant competitor insights
        if insights.get('competitor_strategies'):
            context_parts.append("## Competitor Audience Targeting\n")
            if isinstance(insights['competitor_strategies'], dict):
                for key, value in insights['competitor_strategies'].items():
                    context_parts.append(f"**{key}:** {value}\n\n")
            else:
                context_parts.append(f"{insights['competitor_strategies']}\n\n")

        # Add messaging patterns
        if insights.get('messaging_patterns'):
            context_parts.append("## Messaging Patterns\n")
            if isinstance(insights['messaging_patterns'], dict):
                for key, value in insights['messaging_patterns'].items():
                    context_parts.append(f"**{key}:** {value}\n\n")
            else:
                context_parts.append(f"{insights['messaging_patterns']}\n\n")

    return "".join(context_parts)


def _generate_audience_insights(
    llm: LLMService,
    context: str,
    target_audiences: list[str],
    focus_areas: Optional[list[str]] = None
) -> Dict[str, Any]:
    """Generate audience insights using LLM."""

    focus_instruction = ""
    if focus_areas:
        focus_instruction = f"\nFocus especially on these areas: {', '.join(focus_areas)}"

    system_prompt = f"""You are an expert audience researcher and marketing strategist specializing in audience intelligence.

Analyze the provided campaign data and market intelligence to create a comprehensive audience profile.

Generate detailed insights in the following structure:

# AUDIENCE PROFILES

For each target audience segment, provide:

## Segment: [Audience Name]

### Demographics & Firmographics
- Age range, location, job titles, company size (B2B), income levels, etc.

### Psychographics
- Values, beliefs, lifestyle
- Professional identity and aspirations
- Behavioral traits

### Pain Points & Challenges
- Top 3-5 pain points they experience
- Impact of these pain points on their business/life
- Current unsatisfactory solutions they're using

### Motivations & Goals
- What they're trying to achieve
- Success metrics they care about
- Underlying emotional drivers

### Decision-Making Process
- How they research solutions
- Who influences their decisions
- Typical buying journey stages
- Timeline from awareness to purchase

### Objections & Concerns
- Common barriers to purchase
- Risk factors they consider
- Competitive alternatives they evaluate

### Media Consumption
- Where they spend time online
- Content formats they prefer
- Trusted information sources
- Social media usage patterns

### Language & Communication
- Terminology they use
- Tone preferences (formal vs. casual)
- Messaging that resonates
- Phrases to avoid

{focus_instruction}

Format as structured JSON with clear sections for each audience segment. Be specific and actionable."""

    user_prompt = f"""Based on the following campaign and market intelligence, generate comprehensive audience insights for: {', '.join(target_audiences)}

{context}

Provide detailed, actionable audience intelligence now."""

    response = llm.generate(
        prompt=user_prompt,
        system_prompt=system_prompt,
        max_tokens=3000
    )

    # Try to parse as JSON, fallback to structured text
    try:
        import json
        insights_content = json.loads(response['content'])
    except:
        # If not JSON, structure as dict with full text
        insights_content = {
            "full_analysis": response['content'],
            "format": "markdown"
        }

    return {
        "content": insights_content,
        "tokens_used": response.get('tokens_used', 0),
        "model": response.get('model', llm.get_model_name())
    }
