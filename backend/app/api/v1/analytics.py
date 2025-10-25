"""Analytics API endpoints for dashboard metrics."""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_workspace
from app.models import User, Campaign, Signal, SignalAnalysis, GeneratedAsset, AssetRating

router = APIRouter(prefix="/analytics", tags=["analytics"])


class DashboardStats(BaseModel):
    """Dashboard statistics response."""
    total_campaigns: int
    total_signals: int
    total_analyses: int
    total_briefs: int
    campaigns_growth: float  # Percentage growth vs last period
    signals_growth: float
    analyses_growth: float
    briefs_growth: float


class CampaignTimelinePoint(BaseModel):
    """Single point in campaigns over time chart."""
    period: str
    count: int
    date: str


class SignalSourceBreakdown(BaseModel):
    """Signal source distribution."""
    source: str
    count: int
    percentage: float


class DashboardAnalytics(BaseModel):
    """Complete dashboard analytics."""
    stats: DashboardStats
    campaigns_timeline: List[CampaignTimelinePoint]
    signal_sources: List[SignalSourceBreakdown]


def calculate_growth_rate(current: int, previous: int) -> float:
    """Calculate percentage growth rate."""
    if previous == 0:
        return 0.0 if current == 0 else 100.0
    return round(((current - previous) / previous) * 100, 1)


@router.get("/dashboard", response_model=DashboardAnalytics)
def get_dashboard_analytics(
    workspace_id: UUID = Depends(get_current_workspace),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete dashboard analytics including:
    - Overview stats with growth percentages
    - Campaigns over time (last 4 weeks)
    - Signal source breakdown
    """
    # Get date boundaries
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    # === CURRENT PERIOD STATS (Last 30 days) ===

    # Total campaigns (current period)
    current_campaigns = db.query(func.count(Campaign.id)).filter(
        Campaign.workspace_id == workspace_id,
        Campaign.created_at >= thirty_days_ago
    ).scalar() or 0

    # Total signals (current period)
    current_signals = db.query(func.count(Signal.id)).join(
        Campaign, Signal.campaign_id == Campaign.id
    ).filter(
        Campaign.workspace_id == workspace_id,
        Signal.created_at >= thirty_days_ago
    ).scalar() or 0

    # For now, use campaigns count as proxy for analyses and briefs
    current_analyses = db.query(func.count(Campaign.id)).filter(
        Campaign.workspace_id == workspace_id,
        Campaign.created_at >= thirty_days_ago,
        Campaign.status.in_(['analyzing', 'generating', 'completed'])
    ).scalar() or 0

    current_briefs = db.query(func.count(Campaign.id)).filter(
        Campaign.workspace_id == workspace_id,
        Campaign.created_at >= thirty_days_ago,
        Campaign.status.in_(['completed', 'generating'])
    ).scalar() or 0

    # === PREVIOUS PERIOD STATS (30-60 days ago) ===

    previous_campaigns = db.query(func.count(Campaign.id)).filter(
        Campaign.workspace_id == workspace_id,
        Campaign.created_at >= sixty_days_ago,
        Campaign.created_at < thirty_days_ago
    ).scalar() or 0

    previous_signals = db.query(func.count(Signal.id)).join(
        Campaign, Signal.campaign_id == Campaign.id
    ).filter(
        Campaign.workspace_id == workspace_id,
        Signal.created_at >= sixty_days_ago,
        Signal.created_at < thirty_days_ago
    ).scalar() or 0

    previous_analyses = db.query(func.count(Campaign.id)).filter(
        Campaign.workspace_id == workspace_id,
        Campaign.created_at >= sixty_days_ago,
        Campaign.created_at < thirty_days_ago,
        Campaign.status.in_(['analyzing', 'generating', 'completed'])
    ).scalar() or 0

    previous_briefs = db.query(func.count(Campaign.id)).filter(
        Campaign.workspace_id == workspace_id,
        Campaign.created_at >= sixty_days_ago,
        Campaign.created_at < thirty_days_ago,
        Campaign.status.in_(['completed', 'generating'])
    ).scalar() or 0

    # Calculate growth rates
    stats = DashboardStats(
        total_campaigns=current_campaigns,
        total_signals=current_signals,
        total_analyses=current_analyses,
        total_briefs=current_briefs,
        campaigns_growth=calculate_growth_rate(current_campaigns, previous_campaigns),
        signals_growth=calculate_growth_rate(current_signals, previous_signals),
        analyses_growth=calculate_growth_rate(current_analyses, previous_analyses),
        briefs_growth=calculate_growth_rate(current_briefs, previous_briefs)
    )

    # === CAMPAIGNS TIMELINE (Last 4 weeks) ===

    timeline = []
    for week in range(4):
        week_start = now - timedelta(days=(4 - week) * 7)
        week_end = week_start + timedelta(days=7)

        count = db.query(func.count(Campaign.id)).filter(
            Campaign.workspace_id == workspace_id,
            Campaign.created_at >= week_start,
            Campaign.created_at < week_end
        ).scalar() or 0

        timeline.append(CampaignTimelinePoint(
            period=f"Week {week + 1}",
            count=count,
            date=week_start.strftime("%Y-%m-%d")
        ))

    # === SIGNAL SOURCE BREAKDOWN ===

    # Get total signals count
    total_signals = db.query(func.count(Signal.id)).join(
        Campaign, Signal.campaign_id == Campaign.id
    ).filter(
        Campaign.workspace_id == workspace_id
    ).scalar() or 0

    # Get source breakdown
    source_counts = db.query(
        Signal.source,
        func.count(Signal.id).label('count')
    ).join(
        Campaign, Signal.campaign_id == Campaign.id
    ).filter(
        Campaign.workspace_id == workspace_id
    ).group_by(Signal.source).order_by(desc('count')).limit(10).all()

    # Map source names to display names
    source_display_names = {
        'serp_organic': 'Google',
        'google': 'Google',
        'meta_ads': 'Meta Ads',
        'linkedin_ads': 'LinkedIn',
        'reddit_organic': 'Reddit',
        'youtube': 'YouTube',
        'twitter': 'Twitter',
        'pinterest': 'Pinterest',
        'tiktok': 'TikTok'
    }

    signal_sources = []
    for source, count in source_counts:
        display_name = source_display_names.get(source, source.replace('_', ' ').title())
        percentage = (count / total_signals * 100) if total_signals > 0 else 0
        signal_sources.append(SignalSourceBreakdown(
            source=display_name,
            count=count,
            percentage=round(percentage, 1)
        ))

    return DashboardAnalytics(
        stats=stats,
        campaigns_timeline=timeline,
        signal_sources=signal_sources
    )


# === NEW SIMPLIFIED ANALYTICS ENDPOINTS ===


class CampaignStatusItem(BaseModel):
    """Campaign status distribution item."""
    status: str
    count: int


class CampaignStatusResponse(BaseModel):
    """Campaign status distribution."""
    statuses: List[CampaignStatusItem]


class IntelligenceQualityResponse(BaseModel):
    """Signal quality metrics."""
    avg_relevance: float
    high_quality_percentage: float
    avg_per_campaign: float


class LLMProviderUsage(BaseModel):
    """LLM provider usage."""
    provider: str
    tokens: int
    count: int


class LLMUsageResponse(BaseModel):
    """LLM usage breakdown."""
    providers: List[LLMProviderUsage]
    total_tokens: int


class CompetitorItem(BaseModel):
    """Competitor tracking item."""
    name: str
    count: int


class CompetitorsResponse(BaseModel):
    """Top competitors."""
    competitors: List[CompetitorItem]


class AudienceItem(BaseModel):
    """Audience item."""
    name: str
    count: int


class AudiencesResponse(BaseModel):
    """Top audiences."""
    audiences: List[AudienceItem]


class ChannelItem(BaseModel):
    """Channel distribution item."""
    name: str
    count: int


class ChannelsResponse(BaseModel):
    """Channel distribution."""
    channels: List[ChannelItem]


class AssetRatingItem(BaseModel):
    """Asset rating by platform."""
    platform: str
    avg_rating: float
    count: int


class AssetRatingsResponse(BaseModel):
    """Asset ratings by platform."""
    platforms: List[AssetRatingItem]


@router.get("/campaign-status", response_model=CampaignStatusResponse)
def get_campaign_status(
    workspace_id: UUID = Depends(get_current_workspace),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get campaign count by status."""
    status_counts = db.query(
        Campaign.status,
        func.count(Campaign.id).label('count')
    ).filter(
        Campaign.workspace_id == workspace_id
    ).group_by(Campaign.status).all()

    statuses = [
        CampaignStatusItem(status=status, count=count)
        for status, count in status_counts
    ]

    return CampaignStatusResponse(statuses=statuses)


@router.get("/intelligence-quality", response_model=IntelligenceQualityResponse)
def get_intelligence_quality(
    workspace_id: UUID = Depends(get_current_workspace),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get signal quality metrics."""
    # Get all signals for workspace
    signals = db.query(Signal).join(Campaign).filter(
        Campaign.workspace_id == workspace_id
    ).all()

    if not signals:
        return IntelligenceQualityResponse(
            avg_relevance=0.0,
            high_quality_percentage=0.0,
            avg_per_campaign=0.0
        )

    # Calculate metrics
    total_signals = len(signals)
    avg_relevance = sum(s.relevance_score for s in signals) / total_signals
    high_quality_count = len([s for s in signals if s.relevance_score > 0.7])
    high_quality_pct = (high_quality_count / total_signals) * 100

    # Get campaign count
    campaign_count = db.query(func.count(Campaign.id)).filter(
        Campaign.workspace_id == workspace_id
    ).scalar() or 1

    avg_per_campaign = total_signals / campaign_count

    return IntelligenceQualityResponse(
        avg_relevance=round(avg_relevance, 2),
        high_quality_percentage=round(high_quality_pct, 1),
        avg_per_campaign=round(avg_per_campaign, 0)
    )


@router.get("/llm-usage", response_model=LLMUsageResponse)
def get_llm_usage(
    workspace_id: UUID = Depends(get_current_workspace),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get LLM usage by provider."""
    usage = db.query(
        SignalAnalysis.llm_provider,
        func.sum(SignalAnalysis.tokens_used).label('total_tokens'),
        func.count(SignalAnalysis.id).label('count')
    ).join(Campaign).filter(
        Campaign.workspace_id == workspace_id,
        SignalAnalysis.llm_provider.isnot(None),
        SignalAnalysis.tokens_used.isnot(None)
    ).group_by(SignalAnalysis.llm_provider).all()

    providers = [
        LLMProviderUsage(
            provider=provider.title() if provider else "Unknown",
            tokens=int(tokens or 0),
            count=int(count or 0)
        )
        for provider, tokens, count in usage
    ]

    total_tokens = sum(p.tokens for p in providers)

    return LLMUsageResponse(providers=providers, total_tokens=total_tokens)


@router.get("/competitors", response_model=CompetitorsResponse)
def get_top_competitors(
    workspace_id: UUID = Depends(get_current_workspace),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get most frequently tracked competitors from campaign briefs."""
    campaigns = db.query(Campaign).filter(
        Campaign.workspace_id == workspace_id
    ).all()

    competitor_counts: Dict[str, int] = {}
    for campaign in campaigns:
        if campaign.brief and 'competitors' in campaign.brief:
            competitors = campaign.brief['competitors']
            if isinstance(competitors, list):
                for comp in competitors:
                    if comp and isinstance(comp, str):
                        competitor_counts[comp] = competitor_counts.get(comp, 0) + 1

    sorted_competitors = sorted(
        competitor_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    competitors = [
        CompetitorItem(name=name, count=count)
        for name, count in sorted_competitors
    ]

    return CompetitorsResponse(competitors=competitors)


@router.get("/audiences", response_model=AudiencesResponse)
def get_top_audiences(
    workspace_id: UUID = Depends(get_current_workspace),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get most frequently targeted audiences from campaign briefs."""
    campaigns = db.query(Campaign).filter(
        Campaign.workspace_id == workspace_id
    ).all()

    audience_counts: Dict[str, int] = {}
    for campaign in campaigns:
        if campaign.brief and 'audiences' in campaign.brief:
            audiences = campaign.brief['audiences']
            if isinstance(audiences, list):
                for aud in audiences:
                    if aud and isinstance(aud, str):
                        audience_counts[aud] = audience_counts.get(aud, 0) + 1

    sorted_audiences = sorted(
        audience_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    audiences = [
        AudienceItem(name=name, count=count)
        for name, count in sorted_audiences
    ]

    return AudiencesResponse(audiences=audiences)


@router.get("/channels", response_model=ChannelsResponse)
def get_channel_distribution(
    workspace_id: UUID = Depends(get_current_workspace),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get marketing channel distribution from campaign briefs."""
    campaigns = db.query(Campaign).filter(
        Campaign.workspace_id == workspace_id
    ).all()

    channel_counts: Dict[str, int] = {}
    for campaign in campaigns:
        if campaign.brief and 'channels' in campaign.brief:
            channels = campaign.brief['channels']
            if isinstance(channels, list):
                for ch in channels:
                    if ch and isinstance(ch, str):
                        channel_counts[ch] = channel_counts.get(ch, 0) + 1

    sorted_channels = sorted(
        channel_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )

    channels = [
        ChannelItem(name=name, count=count)
        for name, count in sorted_channels
    ]

    return ChannelsResponse(channels=channels)


@router.get("/asset-ratings", response_model=AssetRatingsResponse)
def get_asset_ratings(
    workspace_id: UUID = Depends(get_current_workspace),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get average asset ratings by platform."""
    # Get assets with ratings
    ratings_by_platform = db.query(
        GeneratedAsset.platform,
        func.avg(AssetRating.rating).label('avg_rating'),
        func.count(GeneratedAsset.id).label('count')
    ).join(
        AssetRating, GeneratedAsset.id == AssetRating.asset_id
    ).join(
        Campaign, GeneratedAsset.campaign_id == Campaign.id
    ).filter(
        Campaign.workspace_id == workspace_id
    ).group_by(GeneratedAsset.platform).all()

    platforms = [
        AssetRatingItem(
            platform=platform.title() if platform else "Unknown",
            avg_rating=round(float(avg_rating), 1),
            count=int(count)
        )
        for platform, avg_rating, count in ratings_by_platform
    ]

    return AssetRatingsResponse(platforms=platforms)
