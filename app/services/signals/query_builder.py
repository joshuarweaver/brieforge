"""AI-assisted query builder for signal cartridges."""
import json
import logging
import re
from typing import Any, Dict, Iterable, List, Optional

from app.services.llm import LLMError, LLMService, LLMProvider

logger = logging.getLogger(__name__)


class SignalQueryBuilder:
    """
    Generate search queries for signal cartridges using an LLM.

    Falls back to provided defaults when the LLM is unavailable or returns
    malformed output.
    """

    DEFAULT_LIMIT = 10

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        *,
        provider: Optional[LLMProvider] = None
    ):
        self.llm = llm_service or LLMService(provider=provider or LLMProvider.CLAUDE)

    def generate(
        self,
        *,
        brief: Dict[str, Any],
        cartridge_name: str,
        platform: str,
        intent: str,
        limit: int = DEFAULT_LIMIT,
        fallback: Optional[Iterable[str]] = None
    ) -> List[str]:
        """
        Request platform-specific search queries from the LLM.

        Args:
            brief: Campaign brief dictionary
            cartridge_name: Internal cartridge identifier
            platform: Platform name (google, meta, etc.)
            intent: Short description of the research objective
            limit: Desired number of queries
            fallback: Queries to use when LLM generation fails
        """
        fallback_list = list(fallback or [])

        prompt = self._build_prompt(
            brief=brief,
            cartridge_name=cartridge_name,
            platform=platform,
            intent=intent,
            limit=limit or self.DEFAULT_LIMIT,
        )

        try:
            response = self.llm.complete(
                prompt,
                system_prompt=(
                    "You are an elite marketing intelligence researcher. "
                    "Craft concise, high-intent search inputs tailored to the "
                    "specified platform. Return ONLY a JSON array of strings."
                ),
                max_tokens=800,
                temperature=0.4,
            )
            content = response.get("content", "") if isinstance(response, dict) else ""
            queries = self._parse_queries(content, limit)
            if queries:
                return queries[:limit]
        except LLMError as exc:
            logger.warning(
                "LLM query generation failed for cartridge %s: %s",
                cartridge_name,
                exc,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "Unexpected error generating queries for %s: %s",
                cartridge_name,
                exc,
            )

        return fallback_list[:limit]

    def _build_prompt(
        self,
        *,
        brief: Dict[str, Any],
        cartridge_name: str,
        platform: str,
        intent: str,
        limit: int,
    ) -> str:
        goal = brief.get("goal") or "Not specified"
        offer = brief.get("offer") or "Not specified"
        brand = brief.get("brand") or brief.get("campaign_name") or "Not specified"
        audiences = brief.get("audiences") or []
        competitors = brief.get("competitors") or []
        markets = brief.get("markets") or brief.get("locations") or []

        def _format_list(items: Iterable[str], default: str) -> str:
            items = [item for item in items if item]
            return "\n".join(f"- {item}" for item in items) if items else default

        return (
            f"Generate up to {limit} distinct search inputs for the {platform} "
            f"platform using the data below. Each search input should be between "
            f"4 and 9 words, avoid boolean operators unless critical, and focus on "
            f"high-signal discoveries that support the intent.\n\n"
            f"Cartridge: {cartridge_name}\n"
            f"Intent: {intent}\n"
            f"Brand: {brand}\n"
            f"Goal: {goal}\n"
            f"Offer: {offer}\n"
            f"Primary audiences:\n{_format_list(audiences, '- Not specified')}\n"
            f"Key competitors:\n{_format_list(competitors, '- Not specified')}\n"
            f"Priority markets/locations:\n{_format_list(markets, '- Not specified')}\n\n"
            "Output: JSON array of unique strings, ordered by priority.\n"
            "No commentary, markdown, or code fences."
        )

    def _parse_queries(self, raw_content: str, limit: int) -> List[str]:
        cleaned = raw_content.strip()

        # Remove common code fences or prefixes
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

        try:
            queries = json.loads(cleaned)
            if isinstance(queries, list):
                normalized = [
                    str(item).strip()
                    for item in queries
                    if isinstance(item, (str, int, float)) and str(item).strip()
                ]
                return normalized[:limit]
        except json.JSONDecodeError:
            # Some models embed JSON inside text; attempt naive extraction
            match = re.search(r"\[.*\]", cleaned, re.DOTALL)
            if match:
                try:
                    queries = json.loads(match.group(0))
                    if isinstance(queries, list):
                        normalized = [
                            str(item).strip()
                            for item in queries
                            if isinstance(item, (str, int, float)) and str(item).strip()
                        ]
                        return normalized[:limit]
                except json.JSONDecodeError:
                    return []

        return []


# Shared singleton to avoid re-initialising the LLM client per cartridge.
_default_builder: Optional[SignalQueryBuilder] = None


def get_signal_query_builder() -> SignalQueryBuilder:
    """Return a module-level builder instance."""
    global _default_builder  # noqa: PLW0603
    if _default_builder is None:
        _default_builder = SignalQueryBuilder()
    return _default_builder

