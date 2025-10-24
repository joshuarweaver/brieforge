"""Base signal cartridge class and registry."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SignalEvidence:
    """
    A single piece of evidence found by a signal cartridge.

    Attributes:
        title: Evidence title/headline
        snippet: Text snippet or description
        url: Source URL (receipt)
        platform: Platform name (google, meta, linkedin, etc.)
        published_date: When the content was published (if available)
        metadata: Additional platform-specific data
        relevance_score: Computed relevance score (0-1)
    """
    title: str
    snippet: str
    url: str
    platform: str
    published_date: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    relevance_score: float = 0.0

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "snippet": self.snippet,
            "url": self.url,
            "platform": self.platform,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "metadata": self.metadata,
            "relevance_score": self.relevance_score,
        }


@dataclass
class SignalResult:
    """
    Result from running a signal cartridge.

    Attributes:
        cartridge_name: Name of the cartridge that generated this result
        query: The query used
        evidence: List of evidence found
        raw_response: Raw API response for debugging
        search_metadata: Metadata about the search execution
    """
    cartridge_name: str
    query: str
    evidence: List[SignalEvidence]
    raw_response: Dict[str, Any]
    search_metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.search_metadata is None:
            self.search_metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "cartridge_name": self.cartridge_name,
            "query": self.query,
            "evidence": [e.to_dict() for e in self.evidence],
            "raw_response": self.raw_response,
            "search_metadata": self.search_metadata,
        }


class SignalCartridge(ABC):
    """
    Base class for signal cartridges.

    Each cartridge represents a specific search strategy or platform.
    Cartridges are responsible for:
    1. Generating queries from campaign briefs
    2. Executing searches via SearchAPI.io
    3. Extracting evidence from raw results
    4. Computing relevance scores
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this cartridge."""
        pass

    @property
    @abstractmethod
    def platform(self) -> str:
        """Platform this cartridge searches (google, meta, linkedin, etc.)."""
        pass

    @abstractmethod
    def generate_queries(self, brief: Dict[str, Any]) -> List[str]:
        """
        Generate search queries from a campaign brief.

        Args:
            brief: Campaign brief dictionary

        Returns:
            List of search queries to execute
        """
        pass

    @abstractmethod
    def extract_evidence(self, raw_results: Dict[str, Any], query: str) -> List[SignalEvidence]:
        """
        Extract evidence from raw API results.

        Args:
            raw_results: Raw API response
            query: The query that was executed

        Returns:
            List of evidence items
        """
        pass

    def compute_relevance(
        self,
        evidence: SignalEvidence,
        brief: Dict[str, Any]
    ) -> float:
        """
        Compute relevance score for a piece of evidence.

        Default implementation uses keyword matching.
        Override for more sophisticated scoring.

        Args:
            evidence: Evidence to score
            brief: Campaign brief

        Returns:
            Relevance score (0-1)
        """
        score = 0.0
        text = f"{evidence.title} {evidence.snippet}".lower()

        # Check for goal keywords
        goal = brief.get("goal", "").lower()
        if goal and goal in text:
            score += 0.3

        # Check for offer keywords
        offer = brief.get("offer", "").lower()
        if offer and offer in text:
            score += 0.3

        # Check for audience keywords
        audiences = brief.get("audiences", [])
        for audience in audiences:
            if audience.lower() in text:
                score += 0.2
                break

        # Check for competitor keywords
        competitors = brief.get("competitors", [])
        for competitor in competitors:
            if competitor.lower() in text:
                score += 0.2
                break

        return min(score, 1.0)


class CartridgeRegistry:
    """Registry for signal cartridges."""

    _cartridges: Dict[str, Type[SignalCartridge]] = {}

    @classmethod
    def register(cls, cartridge_class: Type[SignalCartridge]) -> Type[SignalCartridge]:
        """Register a cartridge class."""
        # Get instance to access name
        instance = cartridge_class()
        cls._cartridges[instance.name] = cartridge_class
        return cartridge_class

    @classmethod
    def get(cls, name: str) -> Optional[Type[SignalCartridge]]:
        """Get a cartridge class by name."""
        return cls._cartridges.get(name)

    @classmethod
    def get_all(cls) -> Dict[str, Type[SignalCartridge]]:
        """Get all registered cartridges."""
        return cls._cartridges.copy()

    @classmethod
    def list_names(cls) -> List[str]:
        """List all registered cartridge names."""
        return list(cls._cartridges.keys())
