"""Campaign blueprint generation service."""
from __future__ import annotations

import uuid
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Sequence

from sqlalchemy.orm import Session

from app.models import (
    Campaign,
    CampaignBlueprintArtifact,
    Signal,
    SignalEnrichment,
)
from app.services.observability import ObservabilityService
from app.services.compliance import ComplianceService


class CampaignBlueprintService:
    """Transforms signals and enrichments into persisted campaign blueprints."""

    def __init__(self, db: Session, observability: ObservabilityService | None = None):
        self.db = db
        self.observability = observability or ObservabilityService(db)
        self.compliance = ComplianceService(db)

    def generate_blueprint(
        self,
        *,
        campaign: Campaign,
        workspace_id,
        user_id: int,
        persist: bool = True,
    ) -> Dict[str, Any]:
        """Create a structured campaign blueprint and optionally persist it."""
        signals = (
            self.db.query(Signal)
            .filter(Signal.campaign_id == campaign.id)
            .order_by(Signal.relevance_score.desc())
            .limit(75)
            .all()
        )

        enrichments = (
            self.db.query(SignalEnrichment)
            .join(Signal, SignalEnrichment.signal_id == Signal.id)
            .filter(Signal.campaign_id == campaign.id)
            .all()
        )

        self.compliance.ensure_allowed(
            workspace_id=workspace_id,
            event_type="campaign.generate_blueprint",
            context={"campaign_id": str(campaign.id)},
        )

        generated_at = datetime.utcnow().isoformat()

        insights = self._build_insights(signals, enrichments)
        audience_hypotheses = self._build_audience_hypotheses(campaign, enrichments, signals)
        value_props = self._build_value_props(campaign, enrichments, signals)
        messaging_pillars = self._build_messaging(signals)
        draft_assets = self._build_assets(signals, audience_hypotheses)
        next_actions = self._build_next_actions(signals, enrichments)

        blueprint: Dict[str, Any] = {
            "artifact_id": None,
            "campaign_id": str(campaign.id),
            "generated_at": generated_at,
            "summary": self._build_summary(campaign, signals),
            "insights": insights,
            "audience_hypotheses": audience_hypotheses,
            "value_propositions": value_props,
            "messaging_pillars": messaging_pillars,
            "draft_assets": draft_assets,
            "next_actions": next_actions,
        }

        artifact: CampaignBlueprintArtifact | None = None
        if persist:
            artifact = CampaignBlueprintArtifact(
                campaign_id=campaign.id,
                summary=blueprint["summary"],
                blueprint=blueprint,
            )
            self.db.add(artifact)
            self.db.commit()
            self.db.refresh(artifact)
            blueprint["artifact_id"] = str(artifact.id)
            artifact.blueprint = blueprint
            self.db.add(artifact)
            self.db.commit()
            self.db.refresh(artifact)

        self.observability.log_event(
            workspace_id=workspace_id,
            user_id=user_id,
            event_type="campaign.blueprint_generated",
            source="campaign_blueprint_service",
            details={
                "campaign_id": str(campaign.id),
                "artifact_id": str(artifact.id) if artifact else None,
            },
        )

        return blueprint

    def list_blueprints(self, campaign_id) -> List[CampaignBlueprintArtifact]:
        """Retrieve blueprint artifacts for a campaign."""
        return (
            self.db.query(CampaignBlueprintArtifact)
            .filter(CampaignBlueprintArtifact.campaign_id == campaign_id)
            .order_by(CampaignBlueprintArtifact.created_at.desc())
            .all()
        )

    def get_blueprint(self, blueprint_id) -> CampaignBlueprintArtifact | None:
        """Fetch a single blueprint artifact by ID."""
        return (
            self.db.query(CampaignBlueprintArtifact)
            .filter(CampaignBlueprintArtifact.id == blueprint_id)
            .first()
        )

    # ---------------------------------------------------------------------
    # Blueprint assembly helpers
    # ---------------------------------------------------------------------
    def _build_summary(self, campaign: Campaign, signals: Sequence[Signal]) -> str:
        if not signals:
            return (
                f"No signals collected yet for {campaign.name}. "
                "Run signal collection to populate blueprint."
            )
        top_sources = {signal.source for signal in signals[:5]}
        goal = campaign.brief.get("goal", "the campaign objective")
        return (
            f"Synthesized {len(signals)} signals across {', '.join(sorted(top_sources))} "
            f"to accelerate work on {goal}."
        )

    def _build_insights(
        self,
        signals: Sequence[Signal],
        enrichments: Sequence[SignalEnrichment],
    ) -> Dict[str, Any]:
        entities = self._top_entities(enrichments, limit=8)
        trending_topics = []
        seen_queries = set()
        for signal in signals:
            query = signal.query.strip()
            if query and query.lower() not in seen_queries:
                trending_topics.append(query)
                seen_queries.add(query.lower())
            if len(trending_topics) >= 8:
                break

        sentiment_counts = Counter({"positive": 0, "neutral": 0, "negative": 0})
        for enrichment in enrichments:
            sentiment = enrichment.sentiment or 0.0
            if sentiment > 0.1:
                sentiment_counts["positive"] += 1
            elif sentiment < -0.1:
                sentiment_counts["negative"] += 1
            else:
                sentiment_counts["neutral"] += 1

        total = sum(sentiment_counts.values()) or 1
        sentiment_distribution = {
            bucket: round(count / total, 3)
            for bucket, count in sentiment_counts.items()
        }

        return {
            "top_entities": entities,
            "trending_topics": trending_topics,
            "sentiment_distribution": sentiment_distribution,
        }

    def _build_audience_hypotheses(
        self,
        campaign: Campaign,
        enrichments: Sequence[SignalEnrichment],
        signals: Sequence[Signal],
    ) -> List[Dict[str, Any]]:
        audiences = campaign.brief.get("audiences") or []
        hypotheses: List[Dict[str, Any]] = []
        for audience in audiences:
            supporting_signals = self._find_signals_for_audience(audience, signals)
            focus_entities = self._find_focus_entities(audience, enrichments)
            hypotheses.append(
                {
                    "audience": audience,
                    "focus_entities": focus_entities,
                    "pain_points": self._collect_from_features(enrichments, "pain_points"),
                    "language_notes": self._collect_from_features(enrichments, "language_patterns"),
                    "supporting_signals": supporting_signals,
                }
            )
        return hypotheses

    def _build_value_props(
        self,
        campaign: Campaign,
        enrichments: Sequence[SignalEnrichment],
        signals: Sequence[Signal],
    ) -> List[Dict[str, Any]]:
        offer = campaign.brief.get("offer", "the product")
        value_props: List[Dict[str, Any]] = []
        for enrichment in enrichments[:5]:
            features = enrichment.features or {}
            proof_points = self._extract_proof_points(enrichment, signals)
            value_props.append(
                {
                    "statement": (
                        f"{offer} addresses {features.get('primary_pain', 'key pains')} "
                        "with evidence-backed messaging."
                    ),
                    "supporting_entities": enrichment.entities[:3],
                    "trend_score": enrichment.trend_score,
                    "proof_points": proof_points,
                }
            )

        if not value_props:
            value_props.append(
                {
                    "statement": f"{offer} delivers measurable outcomes against the campaign goal.",
                    "supporting_entities": [],
                    "trend_score": None,
                    "proof_points": [],
                }
            )
        return value_props

    def _build_messaging(self, signals: Sequence[Signal]) -> List[Dict[str, Any]]:
        pillars: List[Dict[str, Any]] = []
        for signal in signals[:6]:
            hooks = [e.get("title", signal.query) for e in signal.evidence[:3]]
            supporting_urls = [e.get("url") for e in signal.evidence if e.get("url")][:4]
            key_messages = [snippet for snippet in self._clean_snippets(signal)][:3]
            pillars.append(
                {
                    "pillar": signal.query,
                    "key_messages": key_messages,
                    "supporting_urls": supporting_urls,
                    "relevance_score": signal.relevance_score,
                }
            )
        return pillars

    def _build_assets(
        self,
        signals: Sequence[Signal],
        hypotheses: Sequence[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        assets: List[Dict[str, Any]] = []
        for signal in signals[:6]:
            asset_id = str(uuid.uuid4())
            primary_evidence = signal.evidence[0] if signal.evidence else {}
            snippets = self._clean_snippets(signal)
            headline = (primary_evidence.get("title") or signal.query or "Campaign Asset").strip()
            headline = headline[:90]
            primary_text = snippets[0] if snippets else signal.query
            primary_text = primary_text[:240]
            creative_hooks = [e.get("title", signal.query) for e in signal.evidence[:3]]
            supporting_signals = [str(signal.id)]
            audience_focus = self._match_audiences_to_signal(signal, hypotheses)
            variations = self._build_variations(headline, primary_text)

            assets.append(
                {
                    "id": asset_id,
                    "platform": signal.source,
                    "objective": "awareness" if signal.source in {"youtube", "pinterest"} else "conversion",
                    "audience_focus": audience_focus,
                    "headline": headline,
                    "primary_text": primary_text,
                    "cta": "Learn More",
                    "supporting_signals": supporting_signals,
                    "creative_hooks": creative_hooks,
                    "variations": variations,
                }
            )
        return assets

    def _build_next_actions(
        self,
        signals: Sequence[Signal],
        enrichments: Sequence[SignalEnrichment],
    ) -> List[str]:
        actions: List[str] = []
        if not signals:
            actions.append("Run signal collection to gather competitive and audience intelligence.")
        if not enrichments:
            actions.append("Enrich signals to unlock audience hypotheses and messaging themes.")
        else:
            actions.append("Review enriched entities to align creative briefs with audience language.")
        actions.append("Select two priority pillars and produce long-form copy drafts.")
        actions.append("Validate asset hooks with stakeholders before export.")
        return actions

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _top_entities(
        self,
        enrichments: Sequence[SignalEnrichment],
        *,
        limit: int = 10,
    ) -> List[str]:
        counter: Counter[str] = Counter()
        for enrichment in enrichments:
            counter.update(enrichment.entities or [])
        return [entity for entity, _ in counter.most_common(limit)]

    def _collect_from_features(
        self,
        enrichments: Sequence[SignalEnrichment],
        key: str,
    ) -> List[str]:
        values: List[str] = []
        for enrichment in enrichments:
            features = enrichment.features or {}
            value = features.get(key)
            if isinstance(value, list):
                values.extend(value)
            elif isinstance(value, str):
                values.append(value)
        return list(dict.fromkeys(values))[:6]

    def _clean_snippets(self, signal: Signal) -> List[str]:
        snippets = []
        for evidence in signal.evidence:
            snippet = evidence.get("snippet") or ""
            snippet = " ".join(snippet.split())
            if snippet:
                snippets.append(snippet)
        return snippets

    def _find_focus_entities(
        self,
        audience: str,
        enrichments: Sequence[SignalEnrichment],
    ) -> List[str]:
        audience_tokens = {token.lower() for token in audience.split() if len(token) > 3}
        entities: List[str] = []
        for enrichment in enrichments:
            for entity in enrichment.entities or []:
                if any(token in entity.lower() for token in audience_tokens):
                    entities.append(entity)
        return list(dict.fromkeys(entities))[:5]

    def _find_signals_for_audience(
        self,
        audience: str,
        signals: Sequence[Signal],
    ) -> List[str]:
        tokens = [token for token in audience.lower().split() if len(token) > 3]
        supporting: List[str] = []
        for signal in signals:
            haystack = " ".join(
                [signal.query.lower()]
                + [self._clean_text(e.get("snippet", "")) for e in signal.evidence]
            )
            if any(token in haystack for token in tokens):
                supporting.append(str(signal.id))
            if len(supporting) >= 5:
                break
        return supporting

    def _clean_text(self, text: str) -> str:
        return " ".join(text.split()).lower()

    def _extract_proof_points(
        self,
        enrichment: SignalEnrichment,
        signals: Sequence[Signal],
    ) -> List[str]:
        proof_points: List[str] = []
        for signal in signals:
            if signal.id == enrichment.signal_id:
                proof_points.extend(self._clean_snippets(signal)[:2])
        features = enrichment.features or {}
        if isinstance(features.get("key_topics"), list):
            proof_points.extend(features["key_topics"][:2])
        return proof_points[:4]

    def _match_audiences_to_signal(
        self,
        signal: Signal,
        hypotheses: Sequence[Dict[str, Any]],
    ) -> List[str]:
        matches: List[str] = []
        haystack = self._clean_text(signal.query) + " " + " ".join(
            self._clean_text(e.get("snippet", "")) for e in signal.evidence
        )
        for hypothesis in hypotheses:
            audience = hypothesis["audience"]
            tokens = [token for token in audience.lower().split() if len(token) > 3]
            if any(token in haystack for token in tokens):
                matches.append(audience)
        return matches[:3]

    def _build_variations(self, headline: str, primary_text: str) -> List[Dict[str, str]]:
        variations: List[Dict[str, str]] = []
        variations.append(
            {
                "headline": headline,
                "primary_text": primary_text,
                "cta": "Get Started",
            }
        )
        truncated = primary_text[:200]
        if len(primary_text) > 200:
            truncated = f"{truncated}..."
        variations.append(
            {
                "headline": f"{headline[:70]} | Limited Offer",
                "primary_text": f"{truncated} Act today to stay ahead.",
                "cta": "See How",
            }
        )
        return variations
