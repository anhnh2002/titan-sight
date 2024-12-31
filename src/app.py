from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from search import PROVIDERS
from logs import logger
import time
from typing import Literal


logger.info(f"Available search providers: {list(PROVIDERS.keys())}")

app = FastAPI(

)

# Set up middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "*",
        "localhost",
        "127.0.0.1",
        "172.17.0.1",
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ping
@app.get("/ping")
def ping(req: Request):
    return {"status": "Healthy"}

# Version 1
@app.get("/v1/search", description=f"Available search providers: {list(PROVIDERS.keys()) + ["auto"]}")
async def search_v1(query: str, provider: Literal["searxng", "google", "duckduckgo", "auto"] = "auto", max_num_result: int = 3, enable_cache: bool = True):
    
    start_time = time.time()

    # Get the provider
    search_provider = PROVIDERS[provider]

    # Search
    if enable_cache:
        result = await search_provider.search_in_cache(query, max_num_result)
    else:
        result = await search_provider.search(query, max_num_result)

    logger.info(f"Search for '{query}' returned {len(result.results)} results in {time.time() - start_time:.2f} seconds")
    
    return result
