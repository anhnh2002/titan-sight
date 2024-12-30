from .providers import SearchProvider
from .providers import SearxngSearchProvider
from fastapi import HTTPException

def get_search_provider(search_provider: str, provider_base_url: str) -> SearchProvider:
    match search_provider:
        case "searxng":
            return SearxngSearchProvider(provider_base_url)
        case _:
            raise HTTPException(
                status_code=500,
                detail="Invalid search provider. Please set the SEARCH_PROVIDER environment variable to either 'searxng', 'tavily', 'serper', or 'bing'.",
            )