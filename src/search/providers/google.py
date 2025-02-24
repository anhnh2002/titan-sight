import asyncio

import httpx
import requests
import urllib.parse

from schemas import SearchResponse, SearchResult
from ..providers.base import SearchProvider

from logs import logger
import time


class GoogleSearchProvider(SearchProvider):
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
    
    async def search(self, query: str, max_num_result: int, newest_first: bool, sumup_page_timeout: int) -> SearchResponse:

        start_time = time.time()

        # Get link results
        async with httpx.AsyncClient() as client:
            link_results = await self.get_link_results(client, query, num_results=max_num_result, newest_first=newest_first)

        logger.info(f"Search links for '{query}' returned {len(link_results)} links in {time.time() - start_time:.2f} seconds")

        # Fetch details for each result
        if link_results:
            link_results = await self.fetch_details_and_generate_consise_answer(query, link_results, sumup_page_timeout)

        return SearchResponse(query=query, results=link_results)

    async def get_link_results(
        self, client:httpx.AsyncClient, query: str, num_results: int, newest_first: bool = False
    ) -> list[SearchResult]:
        
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
        }
        
        if newest_first:
            params['sort'] = 'date'
            params['dateRestrict'] = 'y1'
        
        url = f"{base_url}?{urllib.parse.urlencode(params)}"

        response = await client.get(url)
        if response.status_code == 200:
            data = response.json().get("items", [])
        else:
            print(f"Error: {response.status_code}")
            data = []

        return [
            SearchResult(
                title=result["title"],
                url=result["link"],
                content=result["snippet"],
            )
            for result in data[:num_results]
        ]

