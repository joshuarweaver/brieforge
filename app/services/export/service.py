"""Ad export orchestration service."""
from typing import Any, Dict
from sqlalchemy.orm import Session

from app.models import Campaign
from app.services.campaign_blueprint import CampaignBlueprintService
from app.services.export.adapters import ADAPTERS
from app.services.observability import ObservabilityService
from app.services.compliance import ComplianceService


class AdExportService:
    """Coordinates blueprint generation and adapter payloads."""

    def __init__(self, db: Session, observability: ObservabilityService | None = None):
        self.db = db
        self.observability = observability or ObservabilityService(db)
        self.compliance = ComplianceService(db)

    def export_campaign(
        self,
        *,
        campaign: Campaign,
        workspace_id,
        user_id: int,
        platform: str,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        adapter = ADAPTERS.get(platform)
        if not adapter:
            raise ValueError(f"Unsupported export platform: {platform}")

        self.compliance.ensure_allowed(
            workspace_id=workspace_id,
            event_type="campaign.export",
            context={"campaign_id": str(campaign.id), "platform": platform, "dry_run": dry_run},
        )

        blueprint_service = CampaignBlueprintService(self.db, self.observability)
        blueprint = blueprint_service.generate_blueprint(
            campaign=campaign,
            workspace_id=workspace_id,
            user_id=user_id,
            persist=False,
        )

        payload = adapter.build_payload(campaign, blueprint)

        export_record = {
            "platform": platform,
            "dry_run": dry_run,
            "payload": payload,
            "blueprint": blueprint,
        }

        self.observability.log_event(
            workspace_id=workspace_id,
            user_id=user_id,
            event_type="campaign.export_generated",
            source=f"ad_export_service.{platform}",
            details={
                "campaign_id": str(campaign.id),
                "dry_run": dry_run,
            },
        )

        return export_record
