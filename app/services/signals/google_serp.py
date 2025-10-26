"""Google SERP signal cartridge."""
from typing import List, Dict, Any
from datetime import datetime

from app.services.signals.base import SignalCartridge, SignalEvidence, CartridgeRegistry


@CartridgeRegistry.register
class GoogleSERPCartridge(SignalCartridge):
    """
    Google organic search results cartridge.

    Searches Google for:
    - Competitor mentions
    - Industry trends
    - Target audience discussions
    - Product/service keywords
    """

    @property
    def name(self) -> str:
        return "google_serp"

    @property
    def platform(self) -> str:
        return "google"

    def generate_queries(self, brief: Dict[str, Any]) -> List[str]:
        """Generate search queries from campaign brief using AI."""
        fallback = self._default_queries(brief)
        return self.ai_generate_queries(
            brief=brief,
            intent=(
                "Surface high-value competitor, audience, and trend insights "
                "via Google search results."
            ),
            limit=10,
            fallback=fallback,
        )

    def _default_queries(self, brief: Dict[str, Any]) -> List[str]:
        """Static query strategy retained as a fallback."""
        queries = []

        goal = brief.get("goal", "")
        offer = brief.get("offer", "")
        competitors = brief.get("competitors", [])
        audiences = brief.get("audiences", [])

        # Query 1: Direct offer search
        if offer:
            queries.append(offer)

        # Query 2: Goal + offer combination
        if goal and offer:
            queries.append(f"{goal} {offer}")

        # Query 3-5: Competitor analysis
        for competitor in competitors[:3]:
            queries.append(f"{competitor} review")

        # Query 6-8: Audience + offer
        for audience in audiences[:3]:
            queries.append(f"{audience} {offer}")

        # Query 9: Industry trends
        if goal:
            queries.append(f"{goal} trends 2024")

        # Query 10: Best practices
        if offer:
            queries.append(f"best {offer} 2024")

        return queries[:10]  # Limit to 10 queries

    def extract_evidence(self, raw_results: Dict[str, Any], query: str) -> List[SignalEvidence]:
        """Extract evidence from Google SERP results."""
        evidence_list = []

        # Extract organic results
        organic_results = raw_results.get("organic_results", [])
        for result in organic_results[:5]:  # Top 5 results
            evidence = SignalEvidence(
                title=result.get("title", ""),
                snippet=result.get("snippet", ""),
                url=result.get("link", ""),
                platform=self.platform,
                published_date=self._parse_date(result.get("date")),
                metadata={
                    "position": result.get("position"),
                    "source": result.get("source"),
                    "rich_snippet": result.get("rich_snippet"),
                }
            )
            evidence_list.append(evidence)

        # Extract "People Also Ask" questions
        related_questions = raw_results.get("related_questions", [])
        for question in related_questions[:3]:
            evidence = SignalEvidence(
                title=question.get("question", ""),
                snippet=question.get("snippet", ""),
                url=question.get("link", ""),
                platform=self.platform,
                metadata={
                    "type": "related_question",
                    "source": question.get("source"),
                }
            )
            evidence_list.append(evidence)

        # Extract related searches
        related_searches = raw_results.get("related_searches", [])
        for search in related_searches[:3]:
            evidence = SignalEvidence(
                title=f"Related: {search.get('query', '')}",
                snippet=f"Related search query: {search.get('query', '')}",
                url=f"https://www.google.com/search?q={search.get('query', '')}",
                platform=self.platform,
                metadata={
                    "type": "related_search",
                    "query": search.get("query"),
                }
            )
            evidence_list.append(evidence)

        return evidence_list

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string from Google results."""
        if not date_str:
            return None

        try:
            # Try parsing common Google date formats
            # This is a simplified version - could be more sophisticated
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
