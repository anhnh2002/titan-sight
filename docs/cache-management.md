# Cache Management Module

## Introduction

The cache-management module provides a dual-layer caching system designed to optimize search operations by storing and retrieving search results efficiently. It implements both short-term and long-term caching strategies using Redis and MongoDB respectively, enabling intelligent result caching based on query similarity and URL-based content storage.

## Architecture Overview

The module implements a sophisticated caching architecture that leverages vector embeddings for intelligent cache matching and persistent storage for long-term data retention.

```mermaid
graph TB
    subgraph "Cache Management Layer"
        STC[ShortTermCacheClient<br/>Redis-based]
        LTC[LongTermCacheClient<br/>MongoDB-based]
        EC[EmbeddingClient]
    end
    
    subgraph "Storage Systems"
        Redis[(Redis<br/>Vector Search)]
        MongoDB[(MongoDB<br/>Persistent Storage)]
    end
    
    subgraph "External Dependencies"
        SP[Search Providers]
        SR[SearchResponse]
    end
    
    SP -->|provides results| STC
    SP -->|provides results| LTC
    EC -->|generates embeddings| STC
    STC <--> Redis
    LTC <--> MongoDB
    STC -->|returns cached| SR
    LTC -->|returns cached| SR
```

## Core Components

### ShortTermCacheClient

The `ShortTermCacheClient` implements an intelligent caching mechanism using Redis with vector similarity search capabilities. It stores search results with their query embeddings, enabling retrieval of cached results for semantically similar queries.

**Key Features:**
- Vector-based similarity matching using cosine distance
- Configurable similarity threshold for cache hits
- Automatic expiration management
- Redis JSON and RediSearch integration

**Architecture:**

```mermaid
graph LR
    subgraph "ShortTermCacheClient"
        Init[__init__]
        CreateIdx[_create_index]
        Set[set method]
        Get[get method]
    end
    
    subgraph "Redis Operations"
        VSS[Vector Similarity Search]
        JSON[JSON Storage]
        Expire[Expiration Setting]
    end
    
    subgraph "Embedding Flow"
        EC[EmbeddingClient]
        Embed[Query Embedding]
    end
    
    Init --> CreateIdx
    Set --> Embed
    Embed --> EC
    Set --> JSON
    Set --> Expire
    Get --> Embed
    Get --> VSS
    VSS --> JSON
```

**Cache Storage Process:**

```mermaid
sequenceDiagram
    participant SP as Search Provider
    participant STC as ShortTermCacheClient
    participant EC as EmbeddingClient
    participant Redis as Redis
    
    SP->>STC: set(search_response)
    STC->>EC: get_embedding(query)
    EC-->>STC: query_embedding
    STC->>STC: generate unique key
    STC->>Redis: json.set(key, obj, nx=True)
    STC->>Redis: expire(key, expire_time)
    Redis-->>STC: confirmation
    STC-->>SP: cache status
```

**Cache Retrieval Process:**

```mermaid
sequenceDiagram
    participant Client as Client
    participant STC as ShortTermCacheClient
    participant EC as EmbeddingClient
    participant Redis as Redis
    
    Client->>STC: get(query)
    STC->>EC: get_embedding(query)
    EC-->>STC: query_embedding
    STC->>Redis: vector similarity search
    Redis-->>STC: similar documents
    alt similarity > threshold
        STC->>Redis: json.get(doc.id)
        Redis-->>STC: cached result
        STC-->>Client: SearchResponse
    else similarity < threshold
        STC-->>Client: None
    end
```

### LongTermCacheClient

The `LongTermCacheClient` provides persistent caching capabilities using MongoDB for long-term storage of search result details. It focuses on URL-based caching, storing detailed information about specific URLs for extended periods.

**Key Features:**
- URL-based unique indexing
- Persistent storage in MongoDB
- Upsert operations for efficient updates
- Long-term data retention

**Architecture:**

```mermaid
graph LR
    subgraph "LongTermCacheClient"
        Init[__init__]
        Set[set method]
        Get[get method]
    end
    
    subgraph "MongoDB Operations"
        Index[Index Creation]
        Upsert[Upsert Operation]
        Query[Document Query]
    end
    
    Init --> Index
    Set --> Upsert
    Get --> Query
```

**Data Flow:**

```mermaid
sequenceDiagram
    participant SP as Search Provider
    participant LTC as LongTermCacheClient
    participant Mongo as MongoDB
    
    SP->>LTC: set(search_response)
    loop for each result
        LTC->>Mongo: update_one({url: url}, {$set: {...}}, upsert=True)
        Mongo-->>LTC: update confirmation
    end
    
    Note over LTC,Mongo: Efficient bulk operations with upsert
```

## Component Interactions

### Integration with Search Providers

The cache management module integrates seamlessly with the [search-providers](search-providers.md) module to provide intelligent caching capabilities:

```mermaid
graph TB
    subgraph "Search Flow with Caching"
        Client[Client Request]
        CacheCheck{Cache Check}
        CacheHit[Return Cached]
        CacheMiss[Fetch from Provider]
        StoreCache[Store in Cache]
        Response[Return Response]
    end
    
    Client --> CacheCheck
    CacheCheck -->|Hit| CacheHit
    CacheCheck -->|Miss| CacheMiss
    CacheMiss --> StoreCache
    StoreCache --> Response
    CacheHit --> Response
```

### Data Schema Integration

Both cache clients work with the `SearchResponse` schema, ensuring consistent data handling across the system:

```mermaid
graph LR
    subgraph "Schema Flow"
        SR[SearchResponse]
        STC[ShortTermCacheClient]
        LTC[LongTermCacheClient]
    end
    
    SR -->|stores complete| STC
    SR -->|extracts details| LTC
    
    STC -->|returns| SR
    LTC -->|returns details| SR
```

## Configuration and Dependencies

### External Dependencies

The module relies on several external systems and services:

1. **Redis**: Used for short-term caching with vector search capabilities
2. **MongoDB**: Used for long-term persistent storage
3. **EmbeddingClient**: Provides vector embeddings for similarity matching

### Configuration Parameters

**ShortTermCacheClient:**
- `redis_url`: Connection string for Redis instance
- `expire_time`: Cache expiration time in seconds
- `sim_threshold`: Similarity threshold for cache hits (0.0 to 1.0)
- `embedding_dim`: Dimension of vector embeddings

**LongTermCacheClient:**
- `mongo_url`: Connection string for MongoDB instance
- `db_name`: Database name for cache storage
- `collection_name`: Collection name for cache entries

## Performance Considerations

### Short-Term Cache Performance
- Vector similarity search provides O(log n) lookup time
- Redis in-memory storage ensures sub-millisecond response times
- Configurable similarity threshold balances accuracy vs. recall

### Long-Term Cache Performance
- MongoDB indexing on URL field ensures O(log n) lookup time
- Upsert operations minimize write overhead
- Persistent storage eliminates cache warmup periods

## Error Handling

The module implements comprehensive error handling:

- **Connection Failures**: Graceful handling of Redis/MongoDB connection issues
- **Index Creation**: Automatic index creation with error logging
- **Data Validation**: Schema validation for all cached objects
- **Timeout Management**: Configurable timeouts for cache operations

## Usage Patterns

### Typical Integration Pattern

```mermaid
graph TD
    A[Receive Search Query] --> B{Check Short-Term Cache}
    B -->|Cache Hit| C[Return Cached Results]
    B -->|Cache Miss| D[Execute Search]
    D --> E{Check Long-Term Cache}
    E -->|Details Found| F[Enhance Results]
    E -->|Details Not Found| G[Store Details]
    F --> H[Store in Short-Term Cache]
    G --> H
    H --> C
```

## Monitoring and Observability

The module provides comprehensive logging for:
- Cache hit/miss rates
- Similarity scores for vector searches
- Connection status for external systems
- Performance metrics for cache operations

## Security Considerations

- Connection strings should be properly secured
- Redis and MongoDB instances should implement appropriate access controls
- Data encryption should be considered for sensitive cached content
- Regular cleanup of expired cache entries

## Future Enhancements

Potential improvements to the cache management system:

1. **Distributed Caching**: Support for Redis cluster deployments
2. **Cache Warming**: Proactive population of frequently accessed content
3. **Intelligent Eviction**: LRU/LFU-based cache eviction policies
4. **Compression**: Data compression for large cache entries
5. **Metrics Export**: Integration with monitoring systems like Prometheus