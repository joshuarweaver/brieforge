"""SearchAPI.io service wrapper with rate limiting and error handling."""
import time
from typing import Dict, Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings


class SearchAPIError(Exception):
    """Base exception for SearchAPI errors."""
    pass


class SearchAPIRateLimitError(SearchAPIError):
    """Rate limit exceeded error."""
    pass


class SearchAPIClient:
    """
    SearchAPI.io client with built-in rate limiting, retries, and error handling.

    Features:
    - Automatic retry with exponential backoff
    - Rate limit handling
    - Error normalization
    - Request tracking for debugging
    """

    BASE_URL = "https://www.searchapi.io/api/v1/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.SEARCHAPI_KEY
        if not self.api_key:
            raise ValueError("SEARCHAPI_KEY not configured")

        self.last_request_time = 0
        min_interval_ms = max(settings.SEARCHAPI_MIN_REQUEST_INTERVAL_MS or 0, 0)
        # Convert configured interval to seconds, defaulting to 100ms if unset
        self.min_request_interval = (min_interval_ms / 1000.0) if min_interval_ms else 0.1

    def _rate_limit(self):
        """Enforce minimum interval between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)

        self.last_request_time = time.time()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        retry=retry_if_exception_type(
            (httpx.TimeoutException, httpx.ConnectError, SearchAPIRateLimitError)
        ),
        reraise=True,
    )
    def search(self, engine: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a search with the given engine and parameters.

        Args:
            engine: Search engine (google, youtube, meta_ad_library, etc.)
            params: Search parameters (q, location, etc.)

        Returns:
            Search results as dictionary

        Raises:
            SearchAPIRateLimitError: If rate limit is exceeded
            SearchAPIError: For other API errors
        """
        self._rate_limit()

        # Build request params
        request_params = {
            "engine": engine,
            "api_key": self.api_key,
            **params
        }

        try:
            response = httpx.get(
                self.BASE_URL,
                params=request_params,
                timeout=30.0
            )
            response.raise_for_status()
            results = response.json()

            # Check for errors in response
            if "error" in results:
                error_msg = results["error"]
                if "rate limit" in error_msg.lower():
                    raise SearchAPIRateLimitError(error_msg)
                raise SearchAPIError(error_msg)

            return results

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                # Increase backoff window to ease pressure on the SearchAPI service
                self.min_request_interval = min(self.min_request_interval * 2, 5.0)
                raise SearchAPIRateLimitError("Rate limit exceeded")
            raise SearchAPIError(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise SearchAPIError(f"Request failed: {str(e)}")
        except Exception as e:
            if isinstance(e, (SearchAPIRateLimitError, SearchAPIError)):
                raise
            raise SearchAPIError(f"SearchAPI request failed: {str(e)}")

    def google_search(
        self,
        query: str,
        location: str = "United States",
        num_results: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a Google search."""
        params = {
            "q": query,
            "location": location,
            "num": num_results,
            **kwargs
        }
        return self.search("google", params)

    def youtube_search(
        self,
        query: str,
        gl: str = "us",
        hl: str = "en",
        **kwargs
    ) -> Dict[str, Any]:
        """Search YouTube."""
        params = {
            "q": query,
            "gl": gl,
            "hl": hl,
            **kwargs
        }
        return self.search("youtube", params)

    def meta_ads_library_search(
        self,
        query: str,
        country: str = "ALL",
        **kwargs
    ) -> Dict[str, Any]:
        """Search Meta (Facebook/Instagram) Ads Library."""
        params = {
            "q": query,
            "country": country,
            **kwargs
        }
        return self.search("meta_ad_library", params)

    def linkedin_ads_library_search(
        self,
        query: str = None,
        advertiser: str = None,
        country: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Search LinkedIn Ads Library."""
        params = {}
        if query:
            params["q"] = query
        if advertiser:
            params["advertiser"] = advertiser
        if country:
            params["country"] = country
        params.update(kwargs)
        return self.search("linkedin_ad_library", params)

    def tiktok_ads_library_search(
        self,
        query: str = None,
        advertiser_id: str = None,
        country: str = "ALL",
        **kwargs
    ) -> Dict[str, Any]:
        """Search TikTok Ads Library."""
        params = {"country": country}
        if query:
            params["q"] = query
        if advertiser_id:
            params["advertiser_id"] = advertiser_id
        params.update(kwargs)
        return self.search("tiktok_ads_library", params)

    def reddit_ads_library_search(
        self,
        query: str,
        industry: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Search Reddit Ads Library."""
        params = {"q": query}
        if industry:
            params["industry"] = industry
        params.update(kwargs)
        return self.search("reddit_ad_library", params)

    def pinterest_search(
        self,
        query: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Search Pinterest (via Google site search as fallback)."""
        # SearchAPI.io doesn't have a dedicated Pinterest engine
        # Use Google with site:pinterest.com as workaround
        params = {
            "q": f"site:pinterest.com {query}",
            **kwargs
        }
        return self.search("google", params)


# Singleton instance
_searchapi_client: Optional[SearchAPIClient] = None


def get_searchapi_client() -> SearchAPIClient:
    """Get or create the global SearchAPI client instance."""
    global _searchapi_client
    if _searchapi_client is None:
        _searchapi_client = SearchAPIClient()
    return _searchapi_client
