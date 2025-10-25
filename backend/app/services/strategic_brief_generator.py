"""Strategic Brief Generator service.

Generates comprehensive 2-page strategic briefs from campaign data and signal analysis.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Campaign, Signal, SignalAnalysis
from app.services.llm import LLMService, LLMProvider


class StrategicBriefError(Exception):
    """Raised when strategic brief generation fails."""
    pass


class StrategicBriefGenerator:
    """
    Generates strategic briefs from campaign data and signal analysis.

    A strategic brief is a 2-page document that synthesizes:
    - Market landscape and competitive positioning
    - Audience insights and pain points
    - Messaging strategy and creative direction
    - Channel recommendations and budget allocation
    - Success metrics and KPIs
    """

    def __init__(self, db: Session, llm_provider: LLMProvider = LLMProvider.CLAUDE):
        """Initialize strategic brief generator.

        Args:
            db: Database session
            llm_provider: LLM provider to use
        """
        self.db = db
        self.llm = LLMService(provider=llm_provider)

    def generate_brief(
        self,
        campaign_id: str,
        include_analysis_ids: Optional[List[str]] = None,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a strategic brief for a campaign.

        Args:
            campaign_id: Campaign UUID
            include_analysis_ids: Optional list of specific analysis IDs to include
            custom_instructions: Optional custom instructions for the brief

        Returns:
            Strategic brief data structure

        Raises:
            StrategicBriefError: If brief generation fails
        """
        # Get campaign
        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise StrategicBriefError(f"Campaign {campaign_id} not found")

        # Get signal stats
        signal_stats = self._get_signal_stats(campaign_id)

        # Get completed analyses
        analyses = self._get_analyses(campaign_id, include_analysis_ids)

        if not analyses:
            raise StrategicBriefError(
                "No completed signal analyses found. Please run signal analysis first."
            )

        # Build context for LLM
        context = self._build_context(campaign, signal_stats, analyses)

        # Generate brief using LLM
        brief_content = self._generate_with_llm(context, custom_instructions)

        return {
            "campaign_id": campaign_id,
            "brief_content": brief_content,
            "metadata": {
                "signal_count": signal_stats["total_signals"],
                "analyses_used": len(analyses),
                "generated_at": datetime.utcnow().isoformat(),
                "llm_provider": self.llm.provider.value,
                "llm_model": self.llm.get_model_name()
            }
        }

    def _get_signal_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get signal statistics for campaign."""
        signals = self.db.query(Signal).filter(Signal.campaign_id == campaign_id).all()

        if not signals:
            return {
                "total_signals": 0,
                "avg_relevance": 0.0,
                "sources": [],
                "top_queries": []
            }

        # Calculate stats
        total = len(signals)
        avg_relevance = sum(s.relevance_score for s in signals) / total

        # Get source breakdown
        sources = {}
        for signal in signals:
            sources[signal.source] = sources.get(signal.source, 0) + 1

        # Get top queries
        query_counts = {}
        for signal in signals:
            query_counts[signal.query] = query_counts.get(signal.query, 0) + 1

        top_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_signals": total,
            "avg_relevance": round(avg_relevance, 2),
            "sources": sources,
            "top_queries": [q[0] for q in top_queries]
        }

    def _get_analyses(
        self,
        campaign_id: str,
        include_ids: Optional[List[str]] = None
    ) -> List[SignalAnalysis]:
        """Get completed signal analyses for campaign."""
        query = self.db.query(SignalAnalysis).filter(
            SignalAnalysis.campaign_id == campaign_id,
            SignalAnalysis.status == "completed"
        )

        if include_ids:
            query = query.filter(SignalAnalysis.id.in_(include_ids))

        return query.order_by(SignalAnalysis.created_at.desc()).all()

    def _build_context(
        self,
        campaign: Campaign,
        signal_stats: Dict[str, Any],
        analyses: List[SignalAnalysis]
    ) -> str:
        """Build context string for LLM."""
        context_parts = []

        # Campaign brief
        context_parts.append("# CAMPAIGN BRIEF\n")
        context_parts.append(f"**Campaign Name:** {campaign.name}\n")
        context_parts.append(f"**Goal:** {campaign.brief.get('goal', 'N/A')}\n")
        context_parts.append(f"**Offer:** {campaign.brief.get('offer', 'N/A')}\n")
        context_parts.append(f"**Target Audiences:** {', '.join(campaign.brief.get('audiences', []))}\n")
        context_parts.append(f"**Competitors:** {', '.join(campaign.brief.get('competitors', []))}\n")
        context_parts.append(f"**Channels:** {', '.join(campaign.brief.get('channels', []))}\n")
        context_parts.append(f"**Budget Band:** {campaign.brief.get('budget_band', 'N/A')}\n")

        if campaign.brief.get('voice_constraints'):
            context_parts.append(f"**Voice/Brand Constraints:** {campaign.brief['voice_constraints']}\n")

        # Signal stats
        context_parts.append("\n# SIGNAL INTELLIGENCE\n")
        context_parts.append(f"- **Total Signals Collected:** {signal_stats['total_signals']}\n")
        context_parts.append(f"- **Average Relevance Score:** {signal_stats['avg_relevance']}\n")

        if signal_stats['sources']:
            context_parts.append("- **Sources:**\n")
            for source, count in signal_stats['sources'].items():
                context_parts.append(f"  - {source}: {count} signals\n")

        # Analyses insights
        context_parts.append("\n# ANALYSIS INSIGHTS\n\n")

        for analysis in analyses:
            context_parts.append(f"## {analysis.analysis_type.value.title()} Analysis\n")

            if analysis.insights:
                # Extract key insights
                insights = analysis.insights

                if insights.get('summary'):
                    context_parts.append(f"**Summary:** {insights['summary']}\n\n")

                if insights.get('key_insights'):
                    context_parts.append("**Key Insights:**\n")
                    for insight in insights['key_insights']:
                        context_parts.append(f"- {insight}\n")
                    context_parts.append("\n")

                if insights.get('competitor_strategies'):
                    context_parts.append("**Competitor Strategies:**\n")
                    context_parts.append(f"{insights['competitor_strategies']}\n\n")

                if insights.get('audience_insights'):
                    context_parts.append("**Audience Insights:**\n")
                    context_parts.append(f"{insights['audience_insights']}\n\n")

                if insights.get('messaging_patterns'):
                    context_parts.append("**Messaging Patterns:**\n")
                    context_parts.append(f"{insights['messaging_patterns']}\n\n")

                if insights.get('creative_recommendations'):
                    context_parts.append("**Creative Recommendations:**\n")
                    for rec in insights['creative_recommendations']:
                        if isinstance(rec, dict):
                            context_parts.append(f"- {rec.get('recommendation', rec)}\n")
                        else:
                            context_parts.append(f"- {rec}\n")
                    context_parts.append("\n")

        return "".join(context_parts)

    def _generate_with_llm(
        self,
        context: str,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate strategic brief using LLM."""

        system_prompt = """You are an expert marketing strategist who creates comprehensive strategic briefs.

Generate a detailed 2-page strategic brief based on the provided campaign data and market intelligence.

The brief should be structured as follows:

# PAGE 1: MARKET LANDSCAPE & STRATEGIC POSITIONING

## Executive Summary
A concise overview (3-4 sentences) of the opportunity, target market, and strategic approach.

## Market Context
- Current market conditions and trends
- Competitive landscape analysis
- Market gaps and opportunities
- Unique positioning angle

## Target Audience Deep Dive
- Primary audience segments (with psychographic and demographic details)
- Pain points and motivations
- Decision-making factors
- Media consumption habits

# PAGE 2: STRATEGIC EXECUTION PLAN

## Messaging Strategy
- Core value proposition
- Key messages by audience segment
- Proof points and supporting evidence
- Brand voice and tone guidelines

## Channel Strategy & Tactics
- Recommended channels with rationale
- Channel-specific tactics
- Budget allocation recommendations
- Integration approach

## Creative Direction
- Visual and conceptual themes
- Ad formats and content types
- Creative testing approach
- Example hooks/angles

## Success Metrics
- Primary KPIs
- Secondary metrics
- Benchmarks and targets
- Measurement approach

Make the brief actionable, data-driven, and specific. Use insights from the provided analysis to support recommendations.
Format the output as structured markdown with clear sections."""

        user_prompt = f"""Based on the following campaign intelligence, generate a comprehensive 2-page strategic brief:

{context}

{f"Additional instructions: {custom_instructions}" if custom_instructions else ""}

Generate the strategic brief now, following the structure exactly as specified."""

        response = self.llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=4000
        )

        # Parse the response into structured sections
        brief_sections = self._parse_brief_sections(response['content'])

        return {
            "full_text": response['content'],
            "sections": brief_sections,
            "tokens_used": response.get('tokens_used', 0),
            "model": response.get('model', self.llm.get_model_name())
        }

    def _parse_brief_sections(self, content: str) -> Dict[str, str]:
        """Parse brief content into sections."""
        sections = {}
        current_section = None
        current_content = []

        for line in content.split('\n'):
            # Check for main section headers (# PAGE or ## Section)
            if line.startswith('# PAGE') or line.startswith('## '):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                # Start new section
                current_section = line.lstrip('#').strip()
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections
