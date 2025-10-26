"""Reddit Ads Library signal cartridge."""
from typing import List, Dict, Any
from datetime import datetime

from app.services.signals.base import SignalCartridge, SignalEvidence, CartridgeRegistry


@CartridgeRegistry.register
class RedditCartridge(SignalCartridge):
    """
    Reddit Ads Library cartridge.

    Searches Reddit Ads Library for:
    - Competitor ad campaigns on Reddit
    - Ad creative strategies
    - Industry targeting approaches
    - Budget and reach insights
    """

    @property
    def name(self) -> str:
        return "reddit"

    @property
    def platform(self) -> str:
        return "reddit"

    def generate_queries(self, brief: Dict[str, Any]) -> List[str]:
        """Generate search queries for Reddit Ads Library using AI."""
        fallback = self._default_queries(brief)
        return self.ai_generate_queries(
            brief=brief,
            intent=(
                "Surface competitive messaging, offers, and audience strategies "
                "from the Reddit Ads Library."
            ),
            limit=10,
            fallback=fallback,
        )

    def _default_queries(self, brief: Dict[str, Any]) -> List[str]:
        """Static query strategy retained as fallback."""
        queries = []

        offer = brief.get("offer", "")
        competitors = brief.get("competitors", [])

        # Query 1: Direct offer search
        if offer:
            queries.append(offer)

        # Query 2-6: Competitor brand searches
        for competitor in competitors[:5]:
            queries.append(competitor)

        # Query 7-10: Category searches
        if offer:
            queries.append(f"best {offer}")
            queries.append(f"{offer} deals")
            queries.append(f"{offer} sale")
            queries.append(f"buy {offer}")

        return queries[:10]

    def extract_evidence(self, raw_results: Dict[str, Any], query: str) -> List[SignalEvidence]:
        """Extract evidence from Reddit Ads Library results (SearchAPI.io format)."""
        evidence_list = []

        # SearchAPI.io returns 'ads' array
        ads = raw_results.get("ads", [])
        for ad in ads[:10]:  # Top 10 ads
            creative = ad.get("creative", {})

            # Get headline from creative
            headline = creative.get("headline", "No headline")

            # Get creative type and content
            creative_type = creative.get("type", "UNKNOWN")
            content = creative.get("content", [])

            # Build snippet from content if available
            snippet = headline
            if content and isinstance(content, list) and len(content) > 0:
                first_content = content[0]
                if isinstance(first_content, dict) and "text" in first_content:
                    snippet = first_content.get("text", headline)

            evidence = SignalEvidence(
                title=headline,
                snippet=snippet[:500],
                url=ad.get("url", ""),
                platform=self.platform,
                published_date=self._parse_date(ad.get("created_date")),
                metadata={
                    "ad_id": ad.get("id"),
                    "budget_category": ad.get("budget_category"),
                    "industry": ad.get("industry"),
                    "creative_type": creative_type,
                    "creative_content": content,
                    "subreddits": ad.get("subreddits", []),
                    "devices": ad.get("devices", []),
                }
            )
            evidence_list.append(evidence)

        return evidence_list

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string from Google results."""
        if not date_str:
            return None

        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
