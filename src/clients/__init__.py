from .llm_clients import LLMClient
from .embedding_clients import EmbeddingClient
from .cache_clients import ShortTermCacheClient, LongTermCacheClient

from constants import (
    REDIS_URL,
    EXPIRE_TIME,
    SIM_THRESHOLD,
    EMBEDDING_DIM,

    MONGO_URL,
    MONGO_DB_NAME,
    MONGO_COLLECTION_NAME,

    EMBEDDING_URL,
    EMBEDDING_API_KEY,
    EMBEDDING_MODEL_NAME,

    LLM_URL,
    LLM_API_KEY,
    LLM_MODEL_NAME,
    LLM_BASE_MODEL_NAME,
    HF_TOKEN,
)

llm_client = LLMClient(
    base_url=LLM_URL,
    api_key=LLM_API_KEY,
    model_name=LLM_MODEL_NAME,
    base_model_name=LLM_BASE_MODEL_NAME,
    hf_token=HF_TOKEN,
)

embedding_client = EmbeddingClient(
    base_url=EMBEDDING_URL,
    api_key=EMBEDDING_API_KEY,
    embedding_model_name=EMBEDDING_MODEL_NAME,
)

short_term_cache_client = ShortTermCacheClient(
    redis_url=REDIS_URL,
    expire_time=EXPIRE_TIME,
    sim_threshold=SIM_THRESHOLD,
    embedding_client=embedding_client,
    embedding_dim=EMBEDDING_DIM
)


long_term_cache_client = LongTermCacheClient(
    mongo_url=MONGO_URL,
    db_name=MONGO_DB_NAME,
    collection_name=MONGO_COLLECTION_NAME,
)

