# Search Providers Module Documentation

## Introduction

The search-providers module implements a pluggable architecture for web search functionality across multiple search engines. It provides a unified interface for performing searches, caching results, and generating AI-powered summaries of web content. The module supports DuckDuckGo, SearXNG, and Google Custom Search APIs, with built-in caching mechanisms and content extraction capabilities.

## Architecture Overview

The module follows an abstract factory pattern with a base `SearchProvider` class that defines the contract for all search implementations. Each concrete provider implements the search logic specific to its underlying API while inheriting common functionality like caching and content processing.

```mermaid
classDiagram
    class SearchProvider {
        <<abstract>>
        +search(query, max_num_result) SearchResponse
        +search_without_cache(query, max_num_result, sumup_page_timeout) SearchResponse
        +search_in_cache(query, max_num_result, newest_first, sumup_page_timeout) SearchResponse
        +fetch_details_and_generate_consise_answer(query, results, sumup_page_timeout) List~SearchResult~
    }
    
    class DuckDuckGoSearchProvider {
        -ddgs: DDGS
        +search(query, max_num_result) SearchResponse
        +get_link_results(query, num_results) List~SearchResult~
    }
    
    class SearxngSearchProvider {
        -host: str
        +search(query, max_num_result) SearchResponse
        +get_link_results(client, query, num_results) List~SearchResult~
        +get_image_results(client, query, num_results) List~str~
    }
    
    class GoogleSearchProvider {
        -api_key: str
        -search_engine_id: str
        +search(query, max_num_result, newest_first, sumup_page_timeout) SearchResponse
        +get_link_results(client, query, num_results, newest_first) List~SearchResult~
    }
    
    SearchProvider <|-- DuckDuckGoSearchProvider
    SearchProvider <|-- SearxngSearchProvider
    SearchProvider <|-- GoogleSearchProvider
```

## Component Relationships

```mermaid
graph TB
    subgraph "Search Providers Module"
        SP[SearchProvider Base Class]
        DDG[DuckDuckGoSearchProvider]
        SX[SearxngSearchProvider]
        GGL[GoogleSearchProvider]
    end
    
    subgraph "External Dependencies"
        SC[short_term_cache_client]
        LC[long_term_cache_client]
        LLM[llm_client]
        TR[trafilatura]
        LOG[logger]
        SCH[schemas]
    end
    
    SP --> SC
    SP --> LC
    SP --> LLM
    SP --> TR
    SP --> LOG
    SP --> SCH
    
    DDG --> SP
    SX --> SP
    GGL --> SP
    
    DDG --> DDGS[duckduckgo_search library]
    SX --> HTT[httpx]
    GGL --> HTT
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant Client
    participant SearchProvider
    participant Cache
    participant SearchAPI
    participant ContentExtractor
    participant LLM
    
    Client->>SearchProvider: search_in_cache(query, max_results)
    SearchProvider->>Cache: get(query)
    alt Cache Hit
        Cache-->>SearchProvider: cached_response
        SearchProvider-->>Client: SearchResponse
    else Cache Miss
        SearchProvider->>SearchAPI: search(query, max_results)
        SearchAPI-->>SearchProvider: raw_results
        
        loop For each result
            SearchProvider->>Cache: get(result.url)
            alt URL Cache Hit
                Cache-->>SearchProvider: cached_details
            else URL Cache Miss
                SearchProvider->>ContentExtractor: fetch_url(result.url)
                ContentExtractor-->>SearchProvider: html_content
                SearchProvider->>ContentExtractor: extract(html_content)
                ContentExtractor-->>SearchProvider: extracted_text
                SearchProvider->>Cache: set(result.url, extracted_text)
            end
            
            SearchProvider->>LLM: summarize_page(query, result)
            LLM-->>SearchProvider: concise_answer
        end
        
        SearchProvider->>Cache: set(response)
        SearchProvider-->>Client: SearchResponse
    end
```

## Core Components

### SearchProvider (Abstract Base Class)

The `SearchProvider` abstract class defines the contract for all search implementations and provides common functionality:

- **Abstract Method**: `search(query, max_num_result)` - Must be implemented by concrete providers
- **Caching Methods**: `search_in_cache()` and `search_without_cache()` provide caching wrappers
- **Content Processing**: `fetch_details_and_generate_consise_answer()` handles URL fetching, content extraction, and AI summarization
- **Timeout Management**: Implements comprehensive timeout handling for all external operations

**Key Features:**
- Multi-level caching (short-term and long-term)
- Asynchronous content fetching with configurable timeouts
- AI-powered content summarization
- Comprehensive error handling and logging

### DuckDuckGoSearchProvider

Implements search using the DuckDuckGo search engine:

- **Library**: Uses the `duckduckgo_search` Python library
- **Features**: Privacy-focused search without API keys
- **Implementation**: Synchronous library wrapped in async executor
- **Rate Limiting**: Built-in through the DDGS library

### SearxngSearchProvider

Implements search using a self-hosted SearXNG instance:

- **Protocol**: HTTP/HTTPS API calls using httpx
- **Features**: Meta-search engine aggregating multiple sources
- **Configuration**: Requires SearXNG host URL
- **Additional**: Supports image search functionality

### GoogleSearchProvider

Implements search using Google Custom Search JSON API:

- **API**: Google Custom Search API v1
- **Authentication**: Requires API key and Search Engine ID
- **Features**: Supports date-based sorting and time restrictions
- **Rate Limiting**: Subject to Google's API quotas

## Process Flow

```mermaid
flowchart TD
    Start([Search Request]) --> CacheCheck{Cache Check}
    CacheCheck -->|Hit| ReturnCache[Return Cached Response]
    CacheCheck -->|Miss| ProviderSearch[Provider Search]
    
    ProviderSearch --> RawResults[Raw Search Results]
    RawResults --> ProcessResults[Process Each Result]
    
    ProcessResults --> URLCache{URL Cache Check}
    URLCache -->|Hit| UseCached[Use Cached Content]
    URLCache -->|Miss| FetchContent[Fetch URL Content]
    
    FetchContent --> ExtractContent[Extract Text Content]
    ExtractContent --> CacheContent[Cache Extracted Content]
    
    UseCached --> GenerateSummary[Generate AI Summary]
    CacheContent --> GenerateSummary
    
    GenerateSummary --> CacheResponse[Cache Full Response]
    CacheResponse --> ReturnResponse[Return Response]
    
    ReturnCache --> End([End])
    ReturnResponse --> End
```

## Configuration and Dependencies

### External Dependencies
- **trafilatura**: Web content extraction and text processing
- **httpx**: Asynchronous HTTP client for API calls
- **duckduckgo_search**: DuckDuckGo search library
- **asyncio**: Asynchronous programming support

### Configuration Requirements
- **tralifatura_config**: Configuration for content extraction (from [constants](constants.md))
- **Cache Clients**: Short-term and long-term caching (from [clients](clients.md))
- **LLM Client**: For content summarization (from [clients](clients.md))
- **Logger**: For operation logging (from [logs](logs.md))

### Provider-Specific Configuration
- **DuckDuckGo**: No configuration required
- **SearXNG**: Requires host URL parameter
- **Google**: Requires API key and Search Engine ID

## Error Handling and Timeouts

The module implements comprehensive timeout handling:

- **Cache Lookup**: 5-second timeout
- **URL Fetching**: 10-second timeout
- **Content Extraction**: 5-second timeout
- **LLM Summarization**: Configurable timeout (sumup_page_timeout)

All operations are wrapped in try-catch blocks with detailed logging of failures and performance metrics.

## Performance Optimization

- **Multi-level Caching**: Reduces redundant API calls and content fetching
- **Async Processing**: Concurrent processing of multiple search results
- **Timeout Management**: Prevents hanging operations
- **Selective Processing**: Only fetches details for results that will be returned

## Usage Patterns

### Basic Search with Caching
```python
provider = DuckDuckGoSearchProvider()
response = await provider.search_in_cache("query", max_results=10)
```

### Direct Search without Caching
```python
provider = GoogleSearchProvider(api_key, engine_id)
response = await provider.search_without_cache("query", max_results=10)
```

### Custom Provider Implementation
```python
class CustomSearchProvider(SearchProvider):
    async def search(self, query: str, max_num_result: int) -> SearchResponse:
        # Custom search implementation
        pass
```

## Integration Points

The module integrates with:
- **[schemas](schemas.md)**: SearchResponse and SearchResult data structures
- **[clients](clients.md)**: Caching and LLM clients
- **[logs](logs.md)**: Centralized logging system
- **[constants](constants.md)**: Configuration constants

## Security Considerations

- **API Keys**: Google provider requires secure API key management
- **Rate Limiting**: Respects provider-specific rate limits
- **Content Filtering**: Relies on underlying search engines for content safety
- **Timeout Protection**: Prevents resource exhaustion through comprehensive timeouts

## Monitoring and Observability

The module provides detailed logging for:
- Search query execution times
- Cache hit/miss ratios
- Content fetching performance
- LLM summarization times
- Success/failure rates for each operation

All operations include timing information and detailed error messages for debugging and performance monitoring.