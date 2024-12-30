import asyncio

import httpx

from schemas import SearchResponse, SearchResult
from ..providers.base import SearchProvider


class SearxngSearchProvider(SearchProvider):
    def __init__(self, host: str):
        self.host = host
    
    async def search(self, query: str, max_num_result: int) -> SearchResponse:
        async with httpx.AsyncClient() as client:
            link_results = await self.get_link_results(client, query, num_results=max_num_result)

        # Fetch details for each result
        if link_results:
            link_results = await self.fetch_details_and_generate_consise_answer(query, link_results)

        return SearchResponse(query=query, results=link_results)

    async def get_link_results(
        self, client: httpx.AsyncClient, query: str, num_results: int
    ) -> list[SearchResult]:
        response = await client.get(
            f"{self.host}/search",
            params={"q": query, "format": "json"},
        )
        results = response.json()

        return [
            SearchResult(
                title=result["title"],
                url=result["url"],
                content=result["content"],
            )
            for result in results["results"][:num_results]
        ]

    async def get_image_results(
        self, client: httpx.AsyncClient, query: str, num_results: int = 4
    ) -> list[str]:
        response = await client.get(
            f"{self.host}/search",
            params={"q": query, "format": "json", "categories": "images"},
        )
        results = response.json()
        return [result["img_src"] for result in results["results"][:num_results]]
