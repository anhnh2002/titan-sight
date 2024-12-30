from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from search import get_search_provider
from constants import SEARCH_PROVIDER, SEARCH_PROVIDER_BASE_URL

app = FastAPI()

# Get the search provider
search_provider = get_search_provider(SEARCH_PROVIDER, SEARCH_PROVIDER_BASE_URL)

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
@app.get("/v1/search")
async def search_v1(query: str, max_num_result: int = 3):
    return await search_provider.search_in_cache(query, max_num_result)
