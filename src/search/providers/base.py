from abc import ABC, abstractmethod
from schemas import SearchResponse, SearchResult
from typing import List
from trafilatura import fetch_url, extract
from constants import tralifatura_config
import asyncio
from clients import short_term_cache_client, long_term_cache_client, llm_client
from logs import logger
import time

class SearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str, max_num_result: int) -> SearchResponse:
        raise NotImplementedError
    
    async def search_without_cache(self, query: str, max_num_result: int, sumup_page_timeout: int) -> SearchResponse:
        response = await self.search(query, max_num_result)
        return response

    async def search_in_cache(self, query: str, max_num_result: int, newest_first: bool, sumup_page_timeout: int) -> SearchResponse:
        cached_response = await short_term_cache_client.get(query)
        if cached_response:
            return cached_response

        response = await self.search(query, max_num_result, newest_first=newest_first, sumup_page_timeout=sumup_page_timeout)

        asyncio.create_task(short_term_cache_client.set(response))
        asyncio.create_task(long_term_cache_client.set(response))

        return response

    async def fetch_details_and_generate_consise_answer(self, query: str, results_without_details: List[SearchResult], sumup_page_timeout: int) -> List[SearchResult]:
        async def fetch_details_for_result(result: SearchResult):
            try:
                start_time = time.time()
                await asyncio.sleep(0.1)

                # Create tasks for both cache lookup and URL fetching
                cached_details = await asyncio.wait_for(
                    long_term_cache_client.get(result.url),
                    timeout=5  # 5 seconds timeout for cache lookup
                )

                if cached_details:
                    result.details = cached_details
                else:
                    # Fetch and extract with timeout
                    html = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, lambda: fetch_url(result.url, config=tralifatura_config)
                        ),
                        timeout=10  # 10 seconds timeout for fetching
                    )
                    
                    details = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, lambda: extract(html)
                        ),
                        timeout=5  # 5 seconds timeout for extraction
                    )
                    result.details = details

                logger.info(f"Fetched details for {result.url} in {time.time() - start_time:.2f} seconds")
                start_time = time.time()

                await asyncio.sleep(0.1)

                # Generate concise answer with timeout
                result.answer = await asyncio.wait_for(
                    llm_client.summarize_page(query, result),
                    timeout=sumup_page_timeout  # sumup_page_timeout seconds timeout for LLM
                )

                logger.info(f"Generated concise answer for {result.url} in {time.time() - start_time:.2f} seconds")
                return True

            except asyncio.TimeoutError:
                logger.warning(f"Timeout while processing {result.url}")
                return False
            except Exception as e:
                logger.error(f"Error fetching details for {result.url}: {e}")
                return False

        # Create tasks with gather and return_exceptions=True to handle failures
        tasks = [fetch_details_for_result(result) for result in results_without_details]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failed results
        successful_results = [
            result for result, success in zip(results_without_details, results)
            if success and not isinstance(success, Exception)
        ]

        logger.info(f"Successfully processed {len(successful_results)} out of {len(results_without_details)} results")
        return successful_results