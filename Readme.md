# Titan Sight

Seamless web search integration for LLM agents. Transforms natural language queries into structured web data, enabling AI models to access real-time information through a clean API.

<div align="center">

<img src="./assets/ts-logo.png" width="200" height="auto" alt="Titan Sight Logo">

</div>

## Features

- **Multi-Level Caching System**
  - Query-level caching with Redis using vector similarity search
  - Page-level content caching with MongoDB for URL-based retrieval

- **Multiple Search Providers**
  - [SearXNG](https://docs.searxng.org/) - Privacy-focused metasearch engine
  - [DuckDuckGo](https://duckduckgo.com/) - Privacy-respecting search engine 
  - [Google Custom Search](https://developers.google.com/custom-search) - Customizable web search

- **Flexible LLM Integration**
  - OpenAI-compatible API interface
  - Configurable models for result summarization
  - Token-aware content truncation

## Quick Start

1. Config enviroment variables: Copy `.env.example` to `.env` and configure the missing variables

2. Build the Docker image:
```bash
docker build -t titan-sight:0.1.0 .
```

3. Create required network:
```bash
docker network create titan_sight_net
```

4. Start services:
```bash
docker-compose up -d
```

## API Usage
Search Endpoint
```bash
curl -X 'GET' \
  'http://localhost:6969/v1/search?query=What%20is%20the%20weather%20like%20today%20in%20Hanoi%3F&provider=google&max_num_result=3&enable_cache=true' \
  -H 'accept: application/json'
```

Response:
```json
{
  "query": "What is the weather like today in Hanoi?",
  "results": [
    {
      "title": "Weather Forecast Hanoi",
      "url": "https://weather.com/...",
      "content": "Current conditions in Hanoi...",
      "details": "Full page content...",
      "answer": "Currently in Hanoi: 24°C, Clear skies..."
    },
    ...
  ]
}
```

## System Architecture
* **FastAPI Backend**: Handles API requests and orchestrates search operations
* **Redis Cache**: Stores query embeddings for fast similarity search
* **MongoDB**: Persists webpage content for frequently accessed URLs
* **SearXNG**: Self-hosted metasearch engine component

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.