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
        Compute relevance score for a piece of evidence using multi-factor analysis.

        Improved implementation using:
        - Weighted keyword matching with partial matches
        - Term frequency consideration
        - Context relevance (title vs snippet)
        - Competitive intelligence weighting

        Args:
            evidence: Evidence to score
            brief: Campaign brief

        Returns:
            Relevance score (0-1)
        """
        score = 0.0
        title_text = evidence.title.lower()
        snippet_text = evidence.snippet.lower()
        combined_text = f"{title_text} {snippet_text}"

        # Helper function for weighted keyword matching
        def keyword_match_score(keywords, text, title_weight=0.6, snippet_weight=0.4):
            """Calculate score with title/snippet weighting."""
            if not keywords:
                return 0.0
            
            title_matches = sum(1 for kw in keywords if kw.lower() in title_text)
            snippet_matches = sum(1 for kw in keywords if kw.lower() in snippet_text)
            
            title_score = (title_matches / len(keywords)) * title_weight
            snippet_score = (snippet_matches / len(keywords)) * snippet_weight
            
            return title_score + snippet_score

        # 1. Goal relevance (weight: 0.25)
        goal = brief.get("goal", "")
        if goal:
            # Split multi-word goals for partial matching
            goal_keywords = [word for word in goal.lower().split() if len(word) > 3]
            if goal_keywords:
                goal_score = keyword_match_score(goal_keywords, combined_text)
                score += goal_score * 0.25

        # 2. Offer/product relevance (weight: 0.30)
        offer = brief.get("offer", "")
        if offer:
            offer_keywords = [word for word in offer.lower().split() if len(word) > 3]
            if offer_keywords:
                offer_score = keyword_match_score(offer_keywords, combined_text)
                score += offer_score * 0.30

        # 3. Audience relevance (weight: 0.20)
        audiences = brief.get("audiences", [])
        if audiences:
            # Check all audiences, use highest match
            audience_scores = []
            for audience in audiences:
                audience_keywords = [word for word in audience.lower().split() if len(word) > 3]
                if audience_keywords:
                    aud_score = keyword_match_score(audience_keywords, combined_text)
                    audience_scores.append(aud_score)
            
            if audience_scores:
                score += max(audience_scores) * 0.20

        # 4. Competitive intelligence (weight: 0.25)
        competitors = brief.get("competitors", [])
        if competitors:
            competitor_matches = sum(1 for comp in competitors if comp.lower() in combined_text)
            if competitor_matches > 0:
                # Boost score for competitive intelligence
                comp_score = min(competitor_matches / len(competitors), 1.0)
                score += comp_score * 0.25

        # 5. Bonus for strong title relevance
        # If title contains multiple key terms, add small bonus
        key_terms = []
        if goal:
            key_terms.extend(goal.lower().split())
        if offer:
            key_terms.extend(offer.lower().split())
        
        key_terms = [t for t in key_terms if len(t) > 3]
        if key_terms:
            title_term_matches = sum(1 for term in key_terms if term in title_text)
            if title_term_matches >= 2:
                score += 0.10

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
