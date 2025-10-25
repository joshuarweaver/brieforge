"""Signal enrichment pipeline."""
import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.models import Signal, SignalEnrichment, SignalEnrichmentType
from app.services.observability import ObservabilityService
from app.services.compliance import ComplianceService

POSITIVE_WORDS = {"win", "growth", "increase", "success", "love", "best", "improve"}
NEGATIVE_WORDS = {"problem", "pain", "struggle", "issue", "hate", "decline", "risk", "friction", "bottleneck"}


class SignalEnrichmentService:
    """Derives structured metadata from raw signals."""

    ENTITY_PATTERN = re.compile(r"\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*)\b")

    def __init__(self, db: Session, observability: Optional[ObservabilityService] = None):
        self.db = db
        self.observability = observability or ObservabilityService(db)
        self.compliance = ComplianceService(db)

    def enrich_campaign(
        self,
        *,
        campaign_id,
        workspace_id,
        user_id: int,
        limit: Optional[int] = None,
    ) -> Dict[str, int]:
        """Enrich signals for a given campaign."""
        query = (
            self.db.query(Signal)
            .filter(Signal.campaign_id == campaign_id)
            .order_by(Signal.created_at.desc())
        )
        if limit:
            query = query.limit(limit)
        signals = query.all()

        self.compliance.ensure_allowed(
            workspace_id=workspace_id,
            event_type="signals.enrich",
            context={"campaign_id": str(campaign_id), "limit": limit},
        )

        created = 0
        skipped = 0
        for signal in signals:
            existing = next((en for en in signal.enrichments if en.enrichment_type == SignalEnrichmentType.SEMANTIC), None)
            if existing:
                skipped += 1
                continue

            enrichment = SignalEnrichment(
                signal_id=signal.id,
                enrichment_type=SignalEnrichmentType.SEMANTIC,
                entities=self._extract_entities(signal),
                sentiment=self._score_sentiment(signal),
                trend_score=self._compute_trend_score(signal),
                features=self._derive_features(signal),
                created_at=datetime.utcnow(),
            )
            self.db.add(enrichment)
            created += 1

        self.db.commit()

        summary = {"created": created, "skipped": skipped, "processed": len(signals)}

        self.observability.log_event(
            workspace_id=workspace_id,
            user_id=user_id,
            event_type="signals.enriched",
            source="signal_enrichment_service",
            details={"campaign_id": str(campaign_id), **summary},
        )

        return summary

    def _extract_entities(self, signal: Signal) -> List[str]:
        """Crude entity extraction from evidence snippets."""
        text = " ".join(
            f"{evidence.get('title', '')} {evidence.get('snippet', '')}"
            for evidence in signal.evidence
        )
        entities = {match.strip() for match in self.ENTITY_PATTERN.findall(text)}
        # Filter out very short words/entities
        return [entity for entity in entities if len(entity) > 3][:15]

    def _score_sentiment(self, signal: Signal) -> float:
        """Approximate sentiment on a -1..1 scale."""
        text = " ".join(
            f"{evidence.get('title', '')} {evidence.get('snippet', '')}"
            for evidence in signal.evidence
        ).lower()

        positive_hits = sum(1 for word in POSITIVE_WORDS if word in text)
        negative_hits = sum(1 for word in NEGATIVE_WORDS if word in text)

        if positive_hits == negative_hits == 0:
            return 0.0

        score = (positive_hits - negative_hits) / max(positive_hits + negative_hits, 1)
        return max(-1.0, min(1.0, score))

    def _compute_trend_score(self, signal: Signal) -> float:
        """Score based on recency and relevance."""
        base = signal.relevance_score or 0.0
        provenance = signal.provenance or {}
        collected_at = provenance.get("collected_at")
        if not collected_at:
            return base

        try:
            collected_time = datetime.fromisoformat(collected_at)
        except ValueError:
            return base

        age_hours = (datetime.utcnow() - collected_time).total_seconds() / 3600
        freshness = max(0.0, 1.0 - min(age_hours / 168.0, 1.0))  # degrade over a week
        return round((base * 0.7) + (freshness * 0.3), 4)

    def _derive_features(self, signal: Signal) -> Dict[str, object]:
        """Additional derived metrics for downstream use."""
        evidence = signal.evidence or []
        snippets = [self._clean_text(item.get("snippet", "")) for item in evidence if item.get("snippet")]
        combined_text = " ".join(snippets)
        words = re.findall(r"[a-zA-Z]{4,}", combined_text.lower())
        word_counts = Counter(words)
        key_topics = [word for word, _ in word_counts.most_common(8)]

        pain_points = self._extract_pain_points(snippets)
        language_patterns = self._extract_language_patterns(snippets)

        avg_snippet_length = 0.0
        if evidence:
            lengths = [len(item.get("snippet", "")) for item in evidence]
            avg_snippet_length = sum(lengths) / max(len(lengths), 1)

        return {
            "avg_snippet_length": round(avg_snippet_length, 2),
            "evidence_count": len(evidence),
            "relevance_score": signal.relevance_score or 0.0,
            "primary_pain": pain_points[0] if pain_points else "efficiency",
            "pain_points": pain_points[:5],
            "language_patterns": language_patterns[:5],
            "key_topics": key_topics[:6],
        }

    def _clean_text(self, text: str) -> str:
        return " ".join(text.split())

    def _extract_pain_points(self, snippets: List[str]) -> List[str]:
        pains: List[str] = []
        for snippet in snippets:
            lowered = snippet.lower()
            if any(word in lowered for word in NEGATIVE_WORDS):
                pains.append(snippet)
        return list(dict.fromkeys(pains))

    def _extract_language_patterns(self, snippets: List[str]) -> List[str]:
        patterns: List[str] = []
        for snippet in snippets:
            words = snippet.split()
            for start in range(0, len(words) - 2, 3):
                phrase = " ".join(words[start : start + 3])
                if len(phrase) > 10:
                    patterns.append(phrase)
        # surface most common patterns
        counter = Counter(patterns)
        return [phrase for phrase, _ in counter.most_common(10)]
