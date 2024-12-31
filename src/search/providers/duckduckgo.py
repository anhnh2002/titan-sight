import asyncio

import httpx

from schemas import SearchResponse, SearchResult
from ..providers.base import SearchProvider
from duckduckgo_search import DDGS

from logs import logger
import time


class DuckDuckGoSearchProvider(SearchProvider):
    def __init__(self, **kwargs):
        self.ddgs = DDGS()
    
    async def search(self, query: str, max_num_result: int) -> SearchResponse:

        start_time = time.time()

        # Get link results
        link_results = await self.get_link_results(query, num_results=max_num_result)

        logger.info(f"Search links for '{query}' returned {len(link_results)} links in {time.time() - start_time:.2f} seconds")

        # Fetch details for each result
        if link_results:
            link_results = await self.fetch_details_and_generate_consise_answer(query, link_results)

        return SearchResponse(query=query, results=link_results)

    async def get_link_results(
        self, query: str, num_results: int
    ) -> list[SearchResult]:
        
        results = await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.ddgs.text(query, max_results=num_results)
        )

        return [
            SearchResult(
                title=result["title"],
                url=result["href"],
                content=result["body"],
            )
            for result in results
        ]

