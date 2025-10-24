"""LinkedIn Ads Library signal cartridge."""
from typing import List, Dict, Any
from datetime import datetime

from app.services.signals.base import SignalCartridge, SignalEvidence, CartridgeRegistry


@CartridgeRegistry.register
class LinkedInAdsCartridge(SignalCartridge):
    """
    LinkedIn Ads Library cartridge.

    Searches LinkedIn Ads Library for:
    - B2B competitor campaigns
    - Professional messaging
    - Industry-specific approaches
    - Lead gen strategies
    """

    @property
    def name(self) -> str:
        return "linkedin_ads"

    @property
    def platform(self) -> str:
        return "linkedin"

    def generate_queries(self, brief: Dict[str, Any]) -> List[str]:
        """Generate search queries for LinkedIn Ads Library."""
        queries = []

        offer = brief.get("offer", "")
        competitors = brief.get("competitors", [])

        # Query 1: Direct offer search
        if offer:
            queries.append(offer)

        # Query 2-6: Competitor brand searches
        for competitor in competitors[:5]:
            queries.append(competitor)

        # Query 7-10: Industry/category searches
        if offer:
            queries.append(f"{offer} solution")
            queries.append(f"{offer} platform")
            queries.append(f"{offer} software")
            queries.append(f"enterprise {offer}")

        return queries[:10]

    def extract_evidence(self, raw_results: Dict[str, Any], query: str) -> List[SignalEvidence]:
        """Extract evidence from LinkedIn Ads Library results (SearchAPI.io format)."""
        evidence_list = []

        # SearchAPI.io returns 'ads' array with advertiser and content objects
        ads = raw_results.get("ads", [])
        for ad in ads[:10]:  # Top 10 ads
            advertiser = ad.get("advertiser", {})
            content = ad.get("content", {})

            # Get advertiser name
            advertiser_name = advertiser.get("name", "Unknown Advertiser")

            # Get headline/text from content
            headline = content.get("headline", "")
            text = content.get("text", "")
            snippet = headline if headline else text if text else "No description"

            # Build ad URL if available
            ad_url = content.get("url", "")

            evidence = SignalEvidence(
                title=advertiser_name,
                snippet=snippet[:500],
                url=ad_url,
                platform=self.platform,
                published_date=self._parse_date(ad.get("first_shown_date")),
                metadata={
                    "advertiser_name": advertiser_name,
                    "advertiser_thumbnail": advertiser.get("thumbnail"),
                    "ad_type": ad.get("ad_type"),
                    "headline": headline,
                    "image": content.get("image"),
                    "cta": content.get("cta"),
                    "first_shown_date": ad.get("first_shown_date"),
                    "last_shown_date": ad.get("last_shown_date"),
                }
            )
            evidence_list.append(evidence)

        return evidence_list

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string from LinkedIn results."""
        if not date_str:
            return None

        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
