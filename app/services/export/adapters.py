"""Ad platform export adapters."""
from abc import ABC, abstractmethod
from typing import Dict, Any

from app.models import Campaign


class BaseExportAdapter(ABC):
    """Base adapter for transforming blueprints into platform payloads."""

    platform: str

    @abstractmethod
    def build_payload(self, campaign: Campaign, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Transform blueprint into platform-specific payload."""
        raise NotImplementedError


class MetaExportAdapter(BaseExportAdapter):
    platform = "meta"

    def build_payload(self, campaign: Campaign, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        assets = blueprint.get("draft_assets", [])
        audience_hypotheses = blueprint.get("audience_hypotheses", [])
        return {
            "name": f"{campaign.name} - Meta Campaign",
            "objective": campaign.brief.get("goal"),
            "target_audiences": [hypothesis.get("audience") for hypothesis in audience_hypotheses],
            "creative_briefs": [
                {
                    "pillar": pillar.get("pillar"),
                    "key_messages": pillar.get("key_messages", []),
                    "supporting_urls": pillar.get("supporting_urls", []),
                }
                for pillar in blueprint.get("messaging_pillars", [])
            ],
            "assets": [
                {
                    "headline": asset.get("headline"),
                    "primary_text": asset.get("primary_text"),
                    "cta": asset.get("cta"),
                    "audience_focus": asset.get("audience_focus", []),
                    "creative_hooks": asset.get("creative_hooks", []),
                }
                for asset in assets
            ],
        }


class GoogleExportAdapter(BaseExportAdapter):
    platform = "google"

    def build_payload(self, campaign: Campaign, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "campaignName": f"{campaign.name} - Search",
            "goal": campaign.brief.get("goal"),
            "keywords": [pillar.get("pillar") for pillar in blueprint.get("messaging_pillars", [])],
            "adGroups": [
                {
                    "name": asset.get("headline", "Ad Group")[:50],
                    "ads": [
                        {
                            "headline": asset.get("headline"),
                            "description": asset.get("primary_text", blueprint.get("summary")),
                            "finalUrl": asset.get("creative_hooks", [None])[0],
                        }
                    ],
                }
                for asset in blueprint.get("draft_assets", [])
            ],
        }


class LinkedInExportAdapter(BaseExportAdapter):
    platform = "linkedin"

    def build_payload(self, campaign: Campaign, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        audience_hypotheses = blueprint.get("audience_hypotheses", [])
        return {
            "campaignName": f"{campaign.name} - LinkedIn",
            "audienceTargeting": {
                "segments": [hypothesis.get("audience") for hypothesis in audience_hypotheses],
                "languageNotes": [
                    note
                    for hypothesis in audience_hypotheses
                    for note in hypothesis.get("language_notes", [])
                ],
            },
            "messageThemes": [
                {
                    "pillar": pillar.get("pillar"),
                    "key_messages": pillar.get("key_messages", []),
                }
                for pillar in blueprint.get("messaging_pillars", [])
            ],
            "cta": "Learn More",
        }


ADAPTERS = {
    adapter.platform: adapter
    for adapter in [
        MetaExportAdapter(),
        GoogleExportAdapter(),
        LinkedInExportAdapter(),
    ]
}
