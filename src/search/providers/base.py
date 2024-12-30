from abc import ABC, abstractmethod

from schemas import SearchResponse, SearchResult
from typing import List

from trafilatura import fetch_url, extract
import asyncio


class SearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str) -> SearchResponse:
        pass

    async def fetch_details(self, results_without_details: List[SearchResult]) -> List[SearchResult]:
        async def fetch_details_for_result(result: SearchResult):
            try:
                # Fetch the URL in an executor
                html = await asyncio.get_event_loop().run_in_executor(
                    None, fetch_url, result.url
                )
                # Extract details in an executor
                details = await asyncio.get_event_loop().run_in_executor(
                    None, extract, html
                )
                result.details = details
            except Exception as e:
                # Handle exceptions (e.g., log the error)
                print(f"Error fetching details for {result.url}: {e}")

        await asyncio.gather(*[fetch_details_for_result(result) for result in results_without_details])
        return results_without_details