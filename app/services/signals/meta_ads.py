"""Meta (Facebook/Instagram) Ads Library signal cartridge."""
from typing import List, Dict, Any
from datetime import datetime

from app.services.signals.base import SignalCartridge, SignalEvidence, CartridgeRegistry


@CartridgeRegistry.register
class MetaAdsCartridge(SignalCartridge):
    """
    Meta Ads Library cartridge.

    Searches the Facebook/Instagram Ads Library for:
    - Competitor ad campaigns
    - Creative approaches
    - Messaging strategies
    - Ad formats and hooks
    """

    @property
    def name(self) -> str:
        return "meta_ads"

    @property
    def platform(self) -> str:
        return "meta"

    def generate_queries(self, brief: Dict[str, Any]) -> List[str]:
        """Generate search queries for Meta Ads Library using AI."""
        fallback = self._default_queries(brief)
        return self.ai_generate_queries(
            brief=brief,
            intent=(
                "Find compelling creative, messaging themes, and competitive "
                "angles in the Meta Ads Library."
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

        # Query 6-8: Audience + offer
        for audience in audiences[:3]:
            queries.append(f"{audience} {offer}")

        # Query 9-10: Category searches
        if offer:
            queries.append(f"best {offer}")
            queries.append(f"buy {offer}")

        return queries[:10]

    def extract_evidence(self, raw_results: Dict[str, Any], query: str) -> List[SignalEvidence]:
        """Extract evidence from Meta Ads Library results (SearchAPI.io format)."""
        evidence_list = []

        # SearchAPI.io returns 'ads' array with nested 'snapshot' structure
        ads = raw_results.get("ads", [])
        for ad in ads[:10]:  # Top 10 ads
            snapshot = ad.get("snapshot", {})

            # Build snippet from body text
            body = snapshot.get("body", {})
            snippet = body.get("text", "No description") if isinstance(body, dict) else str(body)

            # Get page name from snapshot
            page_name = snapshot.get("page_name", "Unknown Advertiser")

            # Build ad archive URL
            ad_archive_id = ad.get("ad_archive_id", "")
            url = f"https://facebook.com/ads/library/?id={ad_archive_id}" if ad_archive_id else ""

            evidence = SignalEvidence(
                title=page_name,
                snippet=snippet[:500],  # Limit snippet length
                url=url,
                platform=self.platform,
                published_date=self._parse_date(ad.get("start_date")),
                metadata={
                    "ad_archive_id": ad_archive_id,
                    "page_id": ad.get("page_id"),
                    "page_name": page_name,
                    "platforms": snapshot.get("platforms", []),
                    "cta_text": snapshot.get("cta_text"),
                    "cards": snapshot.get("cards", []),
                    "link_url": snapshot.get("link_url"),
                    "link_description": snapshot.get("link_description"),
                }
            )
            evidence_list.append(evidence)

        return evidence_list

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string from Meta results."""
        if not date_str:
            return None

        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
