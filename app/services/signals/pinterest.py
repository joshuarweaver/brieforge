"""Pinterest signal cartridge."""
from typing import List, Dict, Any
from datetime import datetime

from app.services.signals.base import SignalCartridge, SignalEvidence, CartridgeRegistry


@CartridgeRegistry.register
class PinterestCartridge(SignalCartridge):
    """
    Pinterest search cartridge (via Google site:pinterest.com).

    Searches Pinterest for:
    - Visual trends and aesthetics
    - Product photography styles
    - Lifestyle and inspiration content
    - Shopping behavior insights

    Note: Uses Google search with site:pinterest.com since SearchAPI.io
    doesn't have a dedicated Pinterest engine.
    """

    @property
    def name(self) -> str:
        return "pinterest"

    @property
    def platform(self) -> str:
        return "pinterest"

    def generate_queries(self, brief: Dict[str, Any]) -> List[str]:
        """Generate search queries for Pinterest."""
        queries = []

        offer = brief.get("offer", "")
        audiences = brief.get("audiences", [])

        # Query 1: Direct offer search
        if offer:
            queries.append(offer)

        # Query 2-4: Audience + offer
        for audience in audiences[:3]:
            queries.append(f"{audience} {offer}")

        # Query 5-7: Visual/aesthetic searches
        if offer:
            queries.append(f"{offer} ideas")
            queries.append(f"{offer} inspiration")
            queries.append(f"best {offer}")

        # Query 8-10: Lifestyle contexts
        if offer:
            queries.append(f"{offer} aesthetic")
            queries.append(f"{offer} style")
            queries.append(f"{offer} design")

        return queries[:10]

    def extract_evidence(self, raw_results: Dict[str, Any], query: str) -> List[SignalEvidence]:
        """Extract evidence from Pinterest search results (via Google SERP)."""
        evidence_list = []

        # Extract organic results (which are Pinterest pins)
        organic_results = raw_results.get("organic_results", [])
        for result in organic_results[:10]:  # Top 10 results
            evidence = SignalEvidence(
                title=result.get("title", "Untitled Pin"),
                snippet=result.get("snippet", "No description")[:500],
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

        return evidence_list

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string from Pinterest results."""
        if not date_str:
            return None

        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
