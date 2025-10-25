"""Campaign blueprint generation service."""
from __future__ import annotations

import copy
import json
import logging
import re
import uuid
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import (
    Campaign,
    CampaignBlueprintArtifact,
    Signal,
    SignalEnrichment,
    SignalAnalysis,
    StrategicBrief,
)
from app.models.signal_analysis import SignalAnalysisStatus
from app.services.compliance import ComplianceService
from app.services.llm import get_llm_service, LLMProvider
from app.services.observability import ObservabilityService

logger = logging.getLogger(__name__)


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
        use_llm: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Create a structured campaign blueprint and optionally persist it."""
        use_llm = settings.BLUEPRINT_USE_LLM if use_llm is None else use_llm

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

        analyses = self._get_completed_analyses(campaign.id)
        strategic_brief = self._get_latest_strategic_brief(campaign.id)

        self.compliance.ensure_allowed(
            workspace_id=workspace_id,
            event_type="campaign.generate_blueprint",
            context={"campaign_id": str(campaign.id)},
        )

        generated_at = datetime.utcnow().isoformat()
        rule_based = self._build_rule_based_blueprint(
            campaign, signals, enrichments, generated_at
        )
        fallback_preview = self._build_fallback_preview(rule_based)

        final_blueprint = copy.deepcopy(rule_based)
        final_metadata = final_blueprint.setdefault("metadata", {})
        final_metadata.update(
            {
                "generation_method": "rule_based",
                "llm_used": False,
                "rule_based_preview": fallback_preview,
            }
        )

        if use_llm:
            try:
                llm_blueprint, llm_meta = self._generate_llm_blueprint(
                    campaign=campaign,
                    signals=signals,
                    enrichments=enrichments,
                    analyses=analyses,
                    strategic_brief=strategic_brief,
                    rule_based=rule_based,
                )
                final_blueprint = self._normalize_blueprint(llm_blueprint, rule_based)
                metadata = final_blueprint.setdefault("metadata", {})
                metadata.update(
                    {
                        "generation_method": "llm",
                        "llm_used": True,
                        **llm_meta,
                        "rule_based_preview": fallback_preview,
                    }
                )
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning(
                    "LLM blueprint generation failed for campaign %s: %s",
                    campaign.id,
                    exc,
                    exc_info=True,
                )
                final_blueprint = rule_based
                final_blueprint.setdefault("metadata", {}).update(
                    {
                        "generation_method": "rule_based",
                        "llm_used": False,
                        "llm_error": str(exc),
                        "rule_based_preview": fallback_preview,
                    }
                )

        final_blueprint["artifact_id"] = None
        final_blueprint["campaign_id"] = str(campaign.id)

        artifact: Optional[CampaignBlueprintArtifact] = None
        if persist:
            artifact = CampaignBlueprintArtifact(
                campaign_id=campaign.id,
                summary=final_blueprint["summary"],
                blueprint=final_blueprint,
            )
            self.db.add(artifact)
            self.db.commit()
            self.db.refresh(artifact)
            final_blueprint["artifact_id"] = str(artifact.id)
            final_blueprint.setdefault("metadata", {})["persisted"] = True
        else:
            final_blueprint.setdefault("metadata", {})["persisted"] = False

        self.observability.log_event(
            workspace_id=workspace_id,
            user_id=user_id,
            event_type="campaign.blueprint_generated",
            source="campaign_blueprint_service",
            details={
                "campaign_id": str(campaign.id),
                "artifact_id": str(artifact.id) if artifact else None,
                "generation_method": final_blueprint.get("metadata", {}).get(
                    "generation_method", "rule_based"
                ),
            },
        )

        return final_blueprint

    # ------------------------------------------------------------------
    # Data fetch helpers
    # ------------------------------------------------------------------
    def _get_completed_analyses(self, campaign_id) -> List[SignalAnalysis]:
        return (
            self.db.query(SignalAnalysis)
            .filter(
                SignalAnalysis.campaign_id == campaign_id,
                SignalAnalysis.status == SignalAnalysisStatus.COMPLETED,
            )
            .order_by(SignalAnalysis.created_at.desc())
            .limit(5)
            .all()
        )

    def _get_latest_strategic_brief(self, campaign_id) -> Optional[StrategicBrief]:
        return (
            self.db.query(StrategicBrief)
            .filter(StrategicBrief.campaign_id == campaign_id)
            .order_by(StrategicBrief.created_at.desc())
            .first()
        )

    # ------------------------------------------------------------------
    # Rule-based blueprint
    # ------------------------------------------------------------------
    def _build_rule_based_blueprint(
        self,
        campaign: Campaign,
        signals: Sequence[Signal],
        enrichments: Sequence[SignalEnrichment],
        generated_at: str,
    ) -> Dict[str, Any]:
        insights = self._build_insights(signals, enrichments)
        audience_hypotheses = self._build_audience_hypotheses(campaign, enrichments, signals)
        value_props = self._build_value_props(campaign, enrichments, signals)
        messaging_pillars = self._build_messaging(signals)
        draft_assets = self._build_assets(signals, audience_hypotheses)
        next_actions = self._build_next_actions(signals, enrichments)

        return {
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
            "metadata": {
                "generation_method": "rule_based",
                "llm_used": False,
            },
        }

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
        trending_topics: List[str] = []
        seen_queries = set()
        for signal in signals:
            query = (signal.query or "").strip()
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
                    "language_notes": self._collect_from_features(
                        enrichments, "language_patterns"
                    ),
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
                    "supporting_entities": (enrichment.entities or [])[:3],
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
            hooks = [e.get("title", signal.query) for e in (signal.evidence or [])[:3]]
            supporting_urls = [
                e.get("url") for e in signal.evidence or [] if e.get("url")
            ][:4]
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
            primary_evidence = (signal.evidence or [{}])[0] if signal.evidence else {}
            snippets = self._clean_snippets(signal)
            headline = (
                primary_evidence.get("title")
                or signal.query
                or f"Campaign Asset {asset_id[:8]}"
            ).strip()
            headline = headline[:90]
            primary_text = snippets[0] if snippets else signal.query
            primary_text = (primary_text or headline)[:240]
            creative_hooks = [
                e.get("title", signal.query) for e in (signal.evidence or [])[:3]
            ]
            supporting_signals = [str(signal.id)]
            audience_focus = self._match_audiences_to_signal(signal, hypotheses)
            variations = self._build_variations(headline, primary_text)

            assets.append(
                {
                    "id": asset_id,
                    "platform": signal.source,
                    "objective": "awareness"
                    if signal.source in {"youtube", "pinterest"}
                    else "conversion",
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
    # LLM blueprint helpers
    # ------------------------------------------------------------------
    def _generate_llm_blueprint(
        self,
        *,
        campaign: Campaign,
        signals: Sequence[Signal],
        enrichments: Sequence[SignalEnrichment],
        analyses: Sequence[SignalAnalysis],
        strategic_brief: Optional[StrategicBrief],
        rule_based: Dict[str, Any],
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        provider_name = (settings.BLUEPRINT_LLM_PROVIDER or "claude").lower()
        try:
            provider = LLMProvider(provider_name)
        except ValueError:
            provider = LLMProvider.CLAUDE

        llm = get_llm_service(provider)

        context = self._build_llm_context(
            campaign=campaign,
            signals=signals,
            enrichments=enrichments,
            analyses=analyses,
            strategic_brief=strategic_brief,
        )
        schema_template = self._schema_template()
        baseline = json.dumps(self._strip_metadata(rule_based), indent=2)

        prompt = (
            "You are a senior marketing strategist tasked with producing a campaign blueprint."
            "\n\n# DATA CONTEXT\n"
            f"{context}"
            "\n\n# BASELINE RULE-BASED BLUEPRINT (REFERENCE)\n"
            f"{baseline}"
            "\n\n# INSTRUCTIONS\n"
            "Using the context and baseline above, craft an improved campaign blueprint.\n"
            "Respond with valid JSON matching the exact schema provided below. "
            "Ensure draft assets include an `id` (UUID), `headline`, `primary_text`, `cta`, "
            "`audience_focus`, `supporting_signals`, `creative_hooks`, and at least one variation. "
            "Ground every recommendation in the provided signals and analyses.\n"
            "Schema:\n"
            f"{schema_template}\n"
            "Return JSON only—no prose, markdown, or additional commentary."
        )

        result = llm.generate(
            prompt=prompt,
            system_prompt=(
                "You are an expert campaign strategist. Produce precise JSON, adhering strictly to the schema."
            ),
            max_tokens=settings.BLUEPRINT_LLM_MAX_TOKENS,
            temperature=0.7,
        )

        content = self._extract_json(result["content"])
        blueprint = json.loads(content)

        metadata = {
            "llm_provider": result.get("provider"),
            "llm_model": result.get("model"),
            "tokens_used": result.get("usage", {}).get("total_tokens"),
        }
        return blueprint, metadata

    def _normalize_blueprint(
        self,
        llm_blueprint: Dict[str, Any],
        fallback: Dict[str, Any],
    ) -> Dict[str, Any]:
        normalized = {
            "artifact_id": None,
            "campaign_id": fallback["campaign_id"],
            "generated_at": llm_blueprint.get("generated_at") or fallback["generated_at"],
            "summary": llm_blueprint.get("summary") or fallback["summary"],
            "insights": self._merge_dicts(fallback["insights"], llm_blueprint.get("insights")),
            "audience_hypotheses": self._ensure_list_of_dicts(
                llm_blueprint.get("audience_hypotheses"), fallback["audience_hypotheses"]
            ),
            "value_propositions": self._ensure_list_of_dicts(
                llm_blueprint.get("value_propositions"), fallback["value_propositions"]
            ),
            "messaging_pillars": self._ensure_list_of_dicts(
                llm_blueprint.get("messaging_pillars"), fallback["messaging_pillars"]
            ),
            "draft_assets": self._normalize_assets(
                llm_blueprint.get("draft_assets"), fallback["draft_assets"]
            ),
            "next_actions": self._ensure_list(
                llm_blueprint.get("next_actions"), fallback["next_actions"]
            ),
            "metadata": llm_blueprint.get("metadata", {}),
        }
        return normalized

    def _merge_dicts(self, base: Dict[str, Any], override: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        base_copy = copy.deepcopy(base)
        if override:
            for key, value in override.items():
                if value is not None:
                    base_copy[key] = value
        return base_copy

    def _ensure_list(self, value: Optional[Sequence[Any]], fallback: Sequence[Any]) -> List[Any]:
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return list(value)
        return list(fallback)

    def _ensure_list_of_dicts(
        self,
        value: Optional[Sequence[Dict[str, Any]]],
        fallback: Sequence[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        if isinstance(value, Sequence):
            return [dict(item) for item in value if isinstance(item, dict)] or list(fallback)
        return [dict(item) for item in fallback]

    def _normalize_assets(
        self,
        assets: Optional[Sequence[Dict[str, Any]]],
        fallback: Sequence[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        source_assets = assets if assets else fallback
        normalized: List[Dict[str, Any]] = []
        for asset in source_assets:
            if not isinstance(asset, dict):
                continue
            asset_copy = dict(asset)
            asset_id = asset_copy.get("id") or str(uuid.uuid4())
            variations = asset_copy.get("variations") or []
            if not isinstance(variations, list) or not variations:
                variations = [
                    {
                        "headline": asset_copy.get("headline"),
                        "primary_text": asset_copy.get("primary_text"),
                        "cta": asset_copy.get("cta", "Learn More"),
                    }
                ]
            asset_copy.update(
                {
                    "id": asset_id,
                    "variations": variations,
                    "audience_focus": asset_copy.get("audience_focus", []),
                    "supporting_signals": asset_copy.get("supporting_signals", []),
                    "creative_hooks": asset_copy.get("creative_hooks", []),
                    "cta": asset_copy.get("cta", "Learn More"),
                }
            )
            normalized.append(asset_copy)
        return normalized

    def _build_llm_context(
        self,
        *,
        campaign: Campaign,
        signals: Sequence[Signal],
        enrichments: Sequence[SignalEnrichment],
        analyses: Sequence[SignalAnalysis],
        strategic_brief: Optional[StrategicBrief],
    ) -> str:
        parts: List[str] = []
        parts.append("## Campaign Brief\n")
        parts.append(json.dumps(campaign.brief, indent=2))
        parts.append("\n\n## Signals (Top 10)\n")
        for idx, signal in enumerate(signals[:10], start=1):
            snippet = ""
            if signal.evidence:
                snippet = signal.evidence[0].get("snippet", "")
            parts.append(
                f"{idx}. [{signal.source}] query='{signal.query}' "
                f"(relevance={round(signal.relevance_score or 0.0, 2)})\n"
            )
            if snippet:
                parts.append(f"   snippet: {snippet[:300]}\n")

        parts.append("\n## Enrichment Highlights\n")
        pain_points = self._collect_flat_features(enrichments, "pain_points")
        language_patterns = self._collect_flat_features(enrichments, "language_patterns")
        key_topics = self._collect_flat_features(enrichments, "key_topics")
        parts.append(f"- Pain points: {', '.join(pain_points[:6]) or 'n/a'}\n")
        parts.append(f"- Language patterns: {', '.join(language_patterns[:6]) or 'n/a'}\n")
        parts.append(f"- Key topics: {', '.join(key_topics[:8]) or 'n/a'}\n")

        if analyses:
            parts.append("\n## Completed Analyses\n")
            for analysis in analyses[:3]:
                summary = ""
                if analysis.insights:
                    summary = analysis.insights.get("summary") or ""
                parts.append(
                    f"- {analysis.analysis_type.value.title()} analysis "
                    f"(confidence={analysis.insights.get('confidence_score') if analysis.insights else 'n/a'}): "
                    f"{summary[:400]}\n"
                )

        if strategic_brief and strategic_brief.content:
            parts.append("\n## Strategic Brief Snapshot\n")
            sections = strategic_brief.content.get("sections", {})
            exec_summary = sections.get("Executive Summary") or strategic_brief.content.get(
                "full_text", ""
            )
            parts.append(exec_summary[:800])

        return "".join(parts)

    def _schema_template(self) -> str:
        sample = {
            "artifact_id": None,
            "campaign_id": "string UUID",
            "generated_at": "ISO-8601 timestamp",
            "summary": "string",
            "insights": {
                "top_entities": ["string"],
                "trending_topics": ["string"],
                "sentiment_distribution": {"positive": 0.4, "neutral": 0.4, "negative": 0.2},
            },
            "audience_hypotheses": [
                {
                    "audience": "string",
                    "focus_entities": ["string"],
                    "pain_points": ["string"],
                    "language_notes": ["string"],
                    "supporting_signals": ["uuid-string"],
                }
            ],
            "value_propositions": [
                {
                    "statement": "string",
                    "supporting_entities": ["string"],
                    "trend_score": 0.75,
                    "proof_points": ["string"],
                }
            ],
            "messaging_pillars": [
                {
                    "pillar": "string",
                    "key_messages": ["string"],
                    "supporting_urls": ["https://example.com"],
                    "relevance_score": 0.8,
                }
            ],
            "draft_assets": [
                {
                    "id": "uuid-string",
                    "platform": "meta",
                    "objective": "conversion",
                    "audience_focus": ["Audience A"],
                    "headline": "string",
                    "primary_text": "string",
                    "cta": "Learn More",
                    "supporting_signals": ["uuid-string"],
                    "creative_hooks": ["string"],
                    "variations": [
                        {
                            "headline": "string",
                            "primary_text": "string",
                            "cta": "Get Started",
                        }
                    ],
                }
            ],
            "next_actions": ["string"],
            "metadata": {"generation_method": "llm"},
        }
        return json.dumps(sample, indent=2)

    def _extract_json(self, content: str) -> str:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*", "", cleaned, count=1).strip()
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()
        return cleaned

    def _strip_metadata(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        stripped = copy.deepcopy(blueprint)
        stripped.pop("metadata", None)
        stripped["artifact_id"] = None
        return stripped

    def _build_fallback_preview(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        preview = {
            "summary": blueprint.get("summary"),
            "messaging_pillars": (blueprint.get("messaging_pillars") or [])[:3],
            "draft_assets": [
                {
                    "platform": asset.get("platform"),
                    "headline": asset.get("headline"),
                    "audience_focus": asset.get("audience_focus"),
                }
                for asset in (blueprint.get("draft_assets") or [])[:3]
            ],
        }
        return preview

    # ------------------------------------------------------------------
    # Shared helper utilities
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

    def _collect_flat_features(
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
        return list(dict.fromkeys(values))

    def _clean_snippets(self, signal: Signal) -> List[str]:
        snippets: List[str] = []
        for evidence in signal.evidence or []:
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
            haystack_parts = [signal.query.lower() if signal.query else ""]
            haystack_parts.extend(
                self._clean_text(e.get("snippet", "")) for e in signal.evidence or []
            )
            haystack = " ".join(haystack_parts)
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
        haystack = self._clean_text(signal.query or "") + " " + " ".join(
            self._clean_text(e.get("snippet", "")) for e in signal.evidence or []
        )
        for hypothesis in hypotheses:
            audience = hypothesis.get("audience", "")
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
