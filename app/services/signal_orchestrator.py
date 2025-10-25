"""Signal orchestrator for running multiple cartridges and storing results."""
import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session

from app.services.searchapi import get_searchapi_client
from app.services.signals.base import SignalCartridge, SignalResult, CartridgeRegistry
from app.models.signal import Signal
from app.models.campaign import Campaign

# Import all cartridges to register them
from app.services.signals.google_serp import GoogleSERPCartridge
from app.services.signals.meta_ads import MetaAdsCartridge
from app.services.signals.linkedin_ads import LinkedInAdsCartridge
from app.services.signals.tiktok_ads import TikTokAdsCartridge
from app.services.signals.youtube import YouTubeCartridge
from app.services.signals.pinterest import PinterestCartridge
from app.services.signals.reddit import RedditCartridge


class SignalOrchestrator:
    """
    Orchestrates signal collection across multiple cartridges.

    Features:
    - Parallel execution of cartridges
    - Automatic database persistence
    - Error handling and retry logic
    - Progress tracking
    """

    def __init__(self, db: Session):
        self.db = db
        self.searchapi = get_searchapi_client()

    async def collect_signals(
        self,
        campaign_id: int,
        cartridge_names: Optional[List[str]] = None,
        max_queries_per_cartridge: int = 10
    ) -> Dict[str, Any]:
        """
        Collect signals for a campaign using specified cartridges.

        Args:
            campaign_id: Campaign ID to collect signals for
            cartridge_names: List of cartridge names to use (None = all)
            max_queries_per_cartridge: Max queries per cartridge

        Returns:
            Summary of signal collection
        """
        # Get campaign
        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        brief = campaign.brief

        # Determine which cartridges to use
        if cartridge_names is None:
            # Use all registered cartridges
            cartridges_to_use = [cls() for cls in CartridgeRegistry.get_all().values()]
        else:
            cartridges_to_use = []
            for name in cartridge_names:
                cartridge_class = CartridgeRegistry.get(name)
                if cartridge_class:
                    cartridges_to_use.append(cartridge_class())

        # Run cartridges
        results = []
        total_signals = 0
        errors = []

        for cartridge in cartridges_to_use:
            try:
                cartridge_results = await self._run_cartridge(
                    cartridge,
                    campaign,
                    brief,
                    max_queries_per_cartridge
                )
                results.extend(cartridge_results)
                total_signals += len(cartridge_results)
            except Exception as e:
                errors.append({
                    "cartridge": cartridge.name,
                    "error": str(e)
                })

        return {
            "campaign_id": campaign_id,
            "cartridges_run": len(cartridges_to_use),
            "total_signals": total_signals,
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _run_cartridge(
        self,
        cartridge: SignalCartridge,
        campaign: Campaign,
        brief: Dict[str, Any],
        max_queries: int
    ) -> List[Signal]:
        """
        Run a single cartridge and store results.

        Args:
            cartridge: Cartridge instance
            campaign: Campaign object
            brief: Campaign brief
            max_queries: Max queries to execute

        Returns:
            List of created Signal objects
        """
        signals_created = []

        # Generate queries
        queries = cartridge.generate_queries(brief)[:max_queries]

        for query in queries:
            try:
                # Execute search based on cartridge type
                raw_results = await self._execute_search(cartridge, query)

                # Extract evidence
                evidence_list = cartridge.extract_evidence(raw_results, query)

                # Compute relevance scores
                for evidence in evidence_list:
                    evidence.relevance_score = cartridge.compute_relevance(evidence, brief)

                # Store as signal in database
                signal = Signal(
                    campaign_id=campaign.id,
                    source=cartridge.platform,
                    search_method=cartridge.name,
                    query=query,
                    evidence=[e.to_dict() for e in evidence_list],
                    relevance_score=sum(e.relevance_score for e in evidence_list) / len(evidence_list) if evidence_list else 0.0,
                    created_at=datetime.utcnow()
                )

                self.db.add(signal)
                self.db.flush()  # Get the ID without committing

                signals_created.append(signal)

            except Exception as e:
                # Log error but continue with other queries
                print(f"Error running query '{query}' on {cartridge.name}: {str(e)}")
                continue

        # Commit all signals for this cartridge
        self.db.commit()

        return signals_created

    async def _execute_search(self, cartridge: SignalCartridge, query: str) -> Dict[str, Any]:
        """
        Execute a search using the appropriate SearchAPI method.

        Args:
            cartridge: Cartridge instance
            query: Search query

        Returns:
            Raw API results
        """
        # Map cartridge names to SearchAPI methods
        # This is a synchronous call, but we wrap it in asyncio for future async support
        loop = asyncio.get_event_loop()

        if cartridge.name == "google_serp":
            result = await loop.run_in_executor(
                None,
                self.searchapi.google_search,
                query
            )
        elif cartridge.name == "meta_ads":
            result = await loop.run_in_executor(
                None,
                self.searchapi.meta_ads_library_search,
                query
            )
        elif cartridge.name == "linkedin_ads":
            result = await loop.run_in_executor(
                None,
                self.searchapi.linkedin_ads_library_search,
                query
            )
        elif cartridge.name == "tiktok_ads":
            result = await loop.run_in_executor(
                None,
                self.searchapi.tiktok_ads_library_search,
                query
            )
        elif cartridge.name == "youtube":
            result = await loop.run_in_executor(
                None,
                self.searchapi.youtube_search,
                query
            )
        elif cartridge.name == "pinterest":
            result = await loop.run_in_executor(
                None,
                self.searchapi.pinterest_search,
                query
            )
        elif cartridge.name == "reddit":
            # Reddit now uses Reddit Ads Library via SearchAPI
            result = await loop.run_in_executor(
                None,
                self.searchapi.reddit_ads_library_search,
                query
            )
        else:
            raise ValueError(f"Unknown cartridge: {cartridge.name}")

        return result

    def get_campaign_signals(
        self,
        campaign_id: Union[int, UUID, str],
        min_relevance: float = 0.0,
        source: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Signal]:
        """
        Get signals for a campaign with optional filtering.

        Args:
            campaign_id: Campaign ID (int, UUID, or str)
            min_relevance: Minimum relevance score (ignored, kept for API compatibility)
            source: Filter by source platform
            limit: Max number of signals to return

        Returns:
            List of Signal objects
        """
        query = self.db.query(Signal).filter(
            Signal.campaign_id == campaign_id
        )

        if source:
            query = query.filter(Signal.source == source)

        query = query.order_by(Signal.relevance_score.desc())

        if limit:
            query = query.limit(limit)

        signals = query.all()
        
        if not signals:
            raise ValueError(f"No signals found for campaign {campaign_id}")
        
        return signals
