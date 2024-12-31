from abc import ABC, abstractmethod

from schemas import SearchResponse, SearchResult
from typing import List

from trafilatura import fetch_url, extract
import asyncio

from clients import short_term_cache_client, long_term_cache_client, llm_client

from logs import logger
import time


class SearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str, max_num_result: int) -> SearchResponse:
        raise NotImplementedError

    async def search_in_cache(self, query: str, max_num_result: int) -> SearchResponse:
        # Check the short-term cache
        cached_response = await short_term_cache_client.get(query)
        if cached_response:
            return cached_response

        # Search the web
        response = await self.search(query, max_num_result)

        # Cache the response asynchronously
        asyncio.create_task(short_term_cache_client.set(response))
        asyncio.create_task(long_term_cache_client.set(response))

        return response

    async def fetch_details_and_generate_consise_answer(self, query: str, results_without_details: List[SearchResult]) -> List[SearchResult]:
        async def fetch_details_for_result(result: SearchResult):
            try:
                start_time = time.time()
                # find the result in the cache
                cached_details = await long_term_cache_client.get(result.url)
                if cached_details:
                    result.details = cached_details
                else:
                    # Fetch the URL in an executor
                    html = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: fetch_url(result.url)
                    )
                    # Extract details in an executor
                    details = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: extract(html)
                    )
                    result.details = details
                
                # log the time taken to fetch the details
                logger.info(f"Fetched details for {result.url} in {time.time() - start_time:.2f} seconds")
                start_time = time.time()

                # Generate a concise answer
                result.answer = await llm_client.summarize_page(query, result)

                # log the time taken to generate the concise answer
                logger.info(f"Generated concise answer for {result.url} in {time.time() - start_time:.2f} seconds")
                
            except Exception as e:
                # Handle exceptions (e.g., log the error)
                print(f"Error fetching details for {result.url}: {e}")

        await asyncio.gather(*[fetch_details_for_result(result) for result in results_without_details])
        return results_without_details