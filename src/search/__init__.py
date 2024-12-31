from .providers import (
    SearchProvider,
    SearxngSearchProvider,
    DuckDuckGoSearchProvider,
    GoogleSearchProvider
)

from fastapi import HTTPException
from typing import Dict

from logs import logger


PROVIDERS: Dict[str, SearchProvider] = {}


# Register Searxng search provider
from constants import SEARXNG_BASE_URL
if not SEARXNG_BASE_URL:
    logger.warning("SEARXNG_BASE_URL environment variable is not set.")
else:
    PROVIDERS["searxng"] = SearxngSearchProvider(SEARXNG_BASE_URL)


# Register DuckDuckGo search provider
PROVIDERS["duckduckgo"] = DuckDuckGoSearchProvider()


# Register Google search provider
from constants import GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID
if not GOOGLE_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
    logger.warning("GOOGLE_API_KEY or GOOGLE_SEARCH_ENGINE_ID environment variables are not set.")
else:
    PROVIDERS["google"] = GoogleSearchProvider(GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID)
