"""TikTok Ads Library signal cartridge."""
from typing import List, Dict, Any
from datetime import datetime

from app.services.signals.base import SignalCartridge, SignalEvidence, CartridgeRegistry


@CartridgeRegistry.register
class TikTokAdsCartridge(SignalCartridge):
    """
    TikTok Ads Library cartridge.

    Searches TikTok Ads Library for:
    - Short-form video ad trends
    - Creator partnerships
    - Viral campaign strategies
    - Gen Z/millennial messaging
    """

    @property
    def name(self) -> str:
        return "tiktok_ads"

    @property
    def platform(self) -> str:
        return "tiktok"

    def generate_queries(self, brief: Dict[str, Any]) -> List[str]:
        """Generate search queries for TikTok Ads Library using AI."""
        fallback = self._default_queries(brief)
        return self.ai_generate_queries(
            brief=brief,
            intent=(
                "Discover viral hooks, creator collaborations, and performance "
                "themes in the TikTok Ads Library."
            ),
            limit=10,
            fallback=fallback,
        )

    def _default_queries(self, brief: Dict[str, Any]) -> List[str]:
        """Static query strategy retained as fallback."""
        queries = []

        offer = brief.get("offer", "")
        competitors = brief.get("competitors", [])
        audiences = brief.get("audiences", [])

        # Query 1: Direct offer search
        if offer:
            queries.append(offer)

        # Query 2-5: Competitor brand searches
        for competitor in competitors[:4]:
            queries.append(competitor)

        # Query 6-8: Trend-focused searches
        if offer:
            queries.append(f"{offer} viral")
            queries.append(f"best {offer}")
            queries.append(f"{offer} challenge")

        # Query 9-10: Audience + offer
        for audience in audiences[:2]:
            queries.append(f"{audience} {offer}")

        return queries[:10]

    def extract_evidence(self, raw_results: Dict[str, Any], query: str) -> List[SignalEvidence]:
        """Extract evidence from TikTok Ads Library results (SearchAPI.io format)."""
        evidence_list = []

        # SearchAPI.io returns 'ads' array
        ads = raw_results.get("ads", [])
        for ad in ads[:10]:  # Top 10 ads
            # Get advertiser info
            advertiser = ad.get("advertiser", "Unknown Advertiser")

            # Get video link
            video_link = ad.get("video_link", "")

            # Get caption/description if available
            caption = ad.get("caption", ad.get("description", "No description"))

            evidence = SignalEvidence(
                title=advertiser,
                snippet=caption[:500] if caption else "No description",
                url=video_link,
                platform=self.platform,
                published_date=self._parse_date(ad.get("first_shown_datetime")),
                metadata={
                    "ad_id": ad.get("id"),
                    "advertiser": advertiser,
                    "video_link": video_link,
                    "cover_image": ad.get("cover_image"),
                    "estimated_audience": ad.get("estimated_audience"),
                    "first_shown_datetime": ad.get("first_shown_datetime"),
                    "last_shown_datetime": ad.get("last_shown_datetime"),
                    "reach": ad.get("reach"),
                }
            )
            evidence_list.append(evidence)

        return evidence_list

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string from TikTok results."""
        if not date_str:
            return None

        try:
            # Handle Unix timestamp
            if isinstance(date_str, (int, float)):
                return datetime.fromtimestamp(date_str)
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError, TypeError):
            return None
