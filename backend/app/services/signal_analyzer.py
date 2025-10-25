"""Signal Analyzer service for AI-powered analysis of collected signals."""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import Signal, Campaign, SignalAnalysis, SignalAnalysisType, SignalAnalysisStatus
from app.services.llm import get_llm_service, LLMProvider, LLMError


class SignalAnalyzerError(Exception):
    """Base exception for signal analyzer errors."""
    pass


class SignalAnalyzer:
    """
    Analyzes collected signals using LLMs to extract insights.

    Features:
    - Multiple analysis types (comprehensive, competitor, audience, etc.)
    - Structured prompts optimized for marketing insights
    - Automatic response parsing and validation
    - Database persistence with error tracking
    - Token usage tracking
    """

    # Analysis prompts
    COMPREHENSIVE_PROMPT_TEMPLATE = """You are an expert marketing strategist analyzing competitive intelligence data.

**Campaign Brief:**
{brief}

**Collected Signals ({signal_count} total):**
{signals}

Please analyze these signals and provide structured insights in the following JSON format:

{{
  "summary": "2-3 sentence executive summary of key findings",
  "key_insights": [
    "Insight 1",
    "Insight 2",
    "Insight 3"
  ],
  "competitor_strategies": {{
    "common_patterns": ["Pattern 1", "Pattern 2"],
    "positioning": ["How competitors position themselves"],
    "channels": ["Which channels competitors use most effectively"],
    "messaging_themes": ["Key messaging themes across competitors"]
  }},
  "audience_insights": {{
    "pain_points": ["Pain point 1", "Pain point 2"],
    "desires": ["What audience wants"],
    "objections": ["Common objections or concerns"],
    "language": ["How audience talks about the topic"]
  }},
  "messaging_patterns": {{
    "hooks": ["Effective hooks seen in signals"],
    "value_propositions": ["How value is communicated"],
    "proof_elements": ["Types of proof used (testimonials, stats, etc.)"]
  }},
  "creative_recommendations": [
    {{
      "concept": "Creative concept",
      "rationale": "Why this would work based on signals",
      "channels": ["Recommended channels"],
      "supporting_signals": ["Which signals support this"]
    }}
  ],
  "market_trends": [
    {{
      "trend": "Trend name",
      "evidence": "What signals show this trend",
      "opportunity": "How to capitalize on this"
    }}
  ],
  "confidence_score": 0.85
}}

Provide actionable insights based on the actual data. Be specific and cite signal evidence."""

    COMPETITOR_PROMPT_TEMPLATE = """You are an expert competitive analyst examining competitor marketing strategies.

**Campaign Goal:** {goal}
**Competitors:** {competitors}

**Competitor Signals ({signal_count} total):**
{signals}

Analyze competitor strategies and provide insights in JSON format:

{{
  "summary": "Executive summary of competitor landscape",
  "competitor_profiles": [
    {{
      "name": "Competitor name",
      "positioning": "How they position themselves",
      "key_messages": ["Main messages they use"],
      "channels": ["Where they're active"],
      "creative_approach": "Their creative style",
      "strengths": ["What they do well"],
      "weaknesses": ["Gaps or weaknesses"],
      "opportunities": ["How we can differentiate"]
    }}
  ],
  "market_gaps": ["Unaddressed needs or positions"],
  "differentiation_opportunities": ["How to stand out"],
  "confidence_score": 0.85
}}"""

    AUDIENCE_PROMPT_TEMPLATE = """You are an expert audience researcher analyzing organic conversations and signals.

**Target Audiences:** {audiences}
**Offering:** {offer}

**Audience Signals ({signal_count} total):**
{signals}

Provide deep audience insights in JSON format:

{{
  "summary": "Key audience insights summary",
  "pain_points": [
    {{
      "pain": "Specific pain point",
      "severity": "high/medium/low",
      "evidence": "Quotes or data from signals"
    }}
  ],
  "desires": [
    {{
      "desire": "What they want",
      "intensity": "high/medium/low",
      "evidence": "Supporting quotes"
    }}
  ],
  "objections": ["Common objections or barriers"],
  "language_patterns": ["How they describe their problems/solutions"],
  "buying_triggers": ["What makes them take action"],
  "proof_preferences": ["What type of proof they respond to"],
  "channel_preferences": ["Where they seek information"],
  "confidence_score": 0.85
}}"""

    def __init__(
        self,
        db: Session,
        llm_provider: LLMProvider = LLMProvider.CLAUDE
    ):
        """
        Initialize Signal Analyzer.

        Args:
            db: Database session
            llm_provider: LLM provider to use (CLAUDE or OPENAI)
        """
        self.db = db
        self.llm = get_llm_service(provider=llm_provider)
        self.llm_provider = llm_provider

    def analyze(
        self,
        campaign_id: int,
        analysis_type: SignalAnalysisType = SignalAnalysisType.COMPREHENSIVE,
        max_signals: Optional[int] = None,
        min_relevance: float = 0.0
    ) -> SignalAnalysis:
        """
        Analyze signals for a campaign.

        Args:
            campaign_id: Campaign ID to analyze
            analysis_type: Type of analysis to perform
            max_signals: Maximum number of signals to analyze (None = all)
            min_relevance: Minimum relevance score for signals to include

        Returns:
            SignalAnalysis object with insights

        Raises:
            SignalAnalyzerError: If analysis fails
        """
        # Create pending analysis record
        analysis = SignalAnalysis(
            campaign_id=campaign_id,
            analysis_type=analysis_type,
            status=SignalAnalysisStatus.PENDING,
            llm_provider=self.llm_provider.value
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)

        try:
            # Update status to in_progress
            analysis.status = SignalAnalysisStatus.IN_PROGRESS
            self.db.commit()

            # Get campaign and signals
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                raise SignalAnalyzerError(f"Campaign {campaign_id} not found")

            signals = self._get_signals(campaign_id, max_signals, min_relevance)
            if not signals:
                raise SignalAnalyzerError(f"No signals found for campaign {campaign_id}")

            # Generate prompt based on analysis type
            prompt = self._build_prompt(analysis_type, campaign, signals)

            # Call LLM
            response = self.llm.complete(
                prompt=prompt,
                system_prompt="You are an expert marketing strategist and data analyst. Provide insights in valid JSON format only, with no additional text.",
                max_tokens=4096,
                temperature=0.7
            )

            # Parse and validate response
            insights = self._parse_response(response["content"], analysis_type)

            # Add signal count to insights
            insights["signal_count"] = len(signals)

            # Update analysis with results
            analysis.status = SignalAnalysisStatus.COMPLETED
            analysis.insights = insights
            analysis.raw_response = response["content"]
            analysis.llm_model = response["model"]
            analysis.tokens_used = response["usage"]["total_tokens"]
            analysis.completed_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(analysis)

            return analysis

        except Exception as e:
            # Update analysis with error
            analysis.status = SignalAnalysisStatus.FAILED
            analysis.error_message = str(e)
            self.db.commit()

            if isinstance(e, SignalAnalyzerError):
                raise
            raise SignalAnalyzerError(f"Analysis failed: {str(e)}")

    def _get_signals(
        self,
        campaign_id: int,
        max_signals: Optional[int],
        min_relevance: float
    ) -> List[Signal]:
        """Get signals for analysis."""
        query = self.db.query(Signal).filter(
            Signal.campaign_id == campaign_id,
            Signal.relevance_score >= min_relevance
        ).order_by(Signal.relevance_score.desc())

        if max_signals:
            query = query.limit(max_signals)

        return query.all()

    def _build_prompt(
        self,
        analysis_type: SignalAnalysisType,
        campaign: Campaign,
        signals: List[Signal]
    ) -> str:
        """Build prompt based on analysis type."""
        # Format signals
        signals_text = self._format_signals(signals)
        brief = campaign.brief

        if analysis_type == SignalAnalysisType.COMPREHENSIVE:
            return self.COMPREHENSIVE_PROMPT_TEMPLATE.format(
                brief=json.dumps(brief, indent=2),
                signal_count=len(signals),
                signals=signals_text
            )
        elif analysis_type == SignalAnalysisType.COMPETITOR:
            return self.COMPETITOR_PROMPT_TEMPLATE.format(
                goal=brief.get("goal", ""),
                competitors=", ".join(brief.get("competitors", [])),
                signal_count=len(signals),
                signals=signals_text
            )
        elif analysis_type == SignalAnalysisType.AUDIENCE:
            return self.AUDIENCE_PROMPT_TEMPLATE.format(
                audiences=", ".join(brief.get("audiences", [])),
                offer=brief.get("offer", ""),
                signal_count=len(signals),
                signals=signals_text
            )
        else:
            # For other types, use comprehensive as default
            return self.COMPREHENSIVE_PROMPT_TEMPLATE.format(
                brief=json.dumps(brief, indent=2),
                signal_count=len(signals),
                signals=signals_text
            )

    def _format_signals(self, signals: List[Signal]) -> str:
        """Format signals for LLM consumption."""
        formatted = []

        for idx, signal in enumerate(signals, 1):
            signal_text = f"\n## Signal #{idx}\n"
            signal_text += f"**Source:** {signal.source} ({signal.search_method})\n"
            signal_text += f"**Query:** {signal.query}\n"
            signal_text += f"**Relevance:** {signal.relevance_score:.2f}\n\n"

            # Add evidence
            evidence_list = signal.evidence
            if evidence_list:
                signal_text += "**Evidence:**\n"
                for ev_idx, evidence in enumerate(evidence_list[:5], 1):  # Top 5 pieces of evidence
                    signal_text += f"\n{ev_idx}. **{evidence.get('title', 'No title')}**\n"
                    signal_text += f"   URL: {evidence.get('url', 'N/A')}\n"
                    signal_text += f"   {evidence.get('snippet', 'No snippet')[:300]}\n"

                    # Add platform-specific metadata if interesting
                    metadata = evidence.get('metadata', {})
                    if metadata:
                        interesting_fields = ['views', 'likes', 'platforms', 'cta_text', 'estimated_audience']
                        meta_str = ", ".join([f"{k}: {v}" for k, v in metadata.items() if k in interesting_fields and v])
                        if meta_str:
                            signal_text += f"   Metadata: {meta_str}\n"

            signal_text += "\n---\n"
            formatted.append(signal_text)

        return "\n".join(formatted)

    def _parse_response(self, response_text: str, analysis_type: SignalAnalysisType) -> Dict[str, Any]:
        """Parse and validate LLM response."""
        try:
            # Try to extract JSON from markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            insights = json.loads(response_text)

            # Validate required fields based on analysis type
            if analysis_type == SignalAnalysisType.COMPREHENSIVE:
                required = ["summary", "key_insights"]
            elif analysis_type == SignalAnalysisType.COMPETITOR:
                required = ["summary", "competitor_profiles"]
            elif analysis_type == SignalAnalysisType.AUDIENCE:
                required = ["summary", "pain_points"]
            else:
                required = ["summary"]

            for field in required:
                if field not in insights:
                    raise SignalAnalyzerError(f"Missing required field: {field}")

            return insights

        except json.JSONDecodeError as e:
            raise SignalAnalyzerError(f"Failed to parse LLM response as JSON: {str(e)}")
