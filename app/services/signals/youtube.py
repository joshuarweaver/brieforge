"""YouTube signal cartridge."""
from typing import List, Dict, Any
from datetime import datetime

from app.services.signals.base import SignalCartridge, SignalEvidence, CartridgeRegistry


@CartridgeRegistry.register
class YouTubeCartridge(SignalCartridge):
    """
    YouTube search cartridge.

    Searches YouTube for:
    - Product reviews and comparisons
    - How-to and educational content
    - Competitor video marketing
    - Influencer partnerships
    - Customer testimonials
    """

    @property
    def name(self) -> str:
        return "youtube"

    @property
    def platform(self) -> str:
        return "youtube"

    def generate_queries(self, brief: Dict[str, Any]) -> List[str]:
        """Generate search queries for YouTube using AI."""
        fallback = self._default_queries(brief)
        return self.ai_generate_queries(
            brief=brief,
            intent=(
                "Identify influential videos, creators, and customer proof on "
                "YouTube relevant to the campaign."
            ),
            limit=10,
            fallback=fallback,
        )

    def _default_queries(self, brief: Dict[str, Any]) -> List[str]:
        """Static query strategy retained as fallback."""
        queries = []

        offer = brief.get("offer", "")
        competitors = brief.get("competitors", [])
        goal = brief.get("goal", "")

        # Query 1: Product/service review
        if offer:
            queries.append(f"{offer} review")

        # Query 2-4: Competitor reviews
        for competitor in competitors[:3]:
            queries.append(f"{competitor} review")

        # Query 5: Comparison
        if competitors:
            comp = competitors[0]
            queries.append(f"{offer} vs {comp}")

        # Query 6: How-to
        if offer:
            queries.append(f"how to {offer}")

        # Query 7: Best of
        if offer:
            queries.append(f"best {offer} 2024")

        # Query 8: Tutorial
        if goal:
            queries.append(f"{goal} tutorial")

        # Query 9-10: Category exploration
        if offer:
            queries.append(f"{offer} explained")
            queries.append(f"{offer} guide")

        return queries[:10]

    def extract_evidence(self, raw_results: Dict[str, Any], query: str) -> List[SignalEvidence]:
        """Extract evidence from YouTube search results (SearchAPI.io format)."""
        evidence_list = []

        # SearchAPI.io returns 'videos' array
        videos = raw_results.get("videos", [])
        for video in videos[:10]:  # Top 10 videos
            channel = video.get("channel", {})
            evidence = SignalEvidence(
                title=video.get("title", ""),
                snippet=video.get("description", "")[:500],
                url=video.get("link", ""),
                platform=self.platform,
                published_date=self._parse_date(video.get("published_time")),
                metadata={
                    "channel": channel.get("title", channel.get("name", "")),
                    "channel_link": channel.get("link"),
                    "views": video.get("views"),
                    "extracted_views": video.get("extracted_views"),
                    "length": video.get("length"),
                    "published": video.get("published_time"),
                    "date": video.get("date"),
                }
            )
            evidence_list.append(evidence)

        return evidence_list

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string from YouTube results."""
        if not date_str:
            return None

        try:
            # YouTube often uses relative dates like "2 days ago"
            # For now, just try ISO format
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
