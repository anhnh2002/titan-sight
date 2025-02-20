import os
from dotenv import load_dotenv
from copy import deepcopy
from trafilatura.settings import DEFAULT_CONFIG

load_dotenv()

# Trafilatura config
tralifatura_config = deepcopy(DEFAULT_CONFIG)
tralifatura_config['DEFAULT']['DOWNLOAD_TIMEOUT'] = '2'

# Redis
REDIS_URL=os.getenv("REDIS_URL")
EXPIRE_TIME=int(os.getenv("EXPIRE_TIME", 3600))
SIM_THRESHOLD=float(os.getenv("SIM_THRESHOLD", 0.9))
EMBEDDING_DIM=int(os.getenv("EMBEDDING_DIM", 512))


# Mongo
MONGO_URL=os.getenv("MONGO_URL")
MONGO_DB_NAME=os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION_NAME=os.getenv("MONGO_COLLECTION_NAME")


# Embedding
EMBEDDING_URL=os.getenv("EMBEDDING_URL")
EMBEDDING_API_KEY=os.getenv("EMBEDDING_API_KEY")
EMBEDDING_MODEL_NAME=os.getenv("EMBEDDING_MODEL_NAME")


# LLM
LLM_URL=os.getenv("LLM_URL")
LLM_API_KEY=os.getenv("LLM_API_KEY")
LLM_MODEL_NAME=os.getenv("LLM_MODEL_NAME")
LLM_BASE_MODEL_NAME=os.getenv("LLM_BASE_MODEL_NAME")
HF_TOKEN=os.getenv("HF_TOKEN")
MAX_PAGE_DETAILS_LENGTH = int(os.getenv("MAX_PAGE_DETAILS_LENGTH", 2048))
MAX_ANSWER_TOKEN_PER_PAGE = int(os.getenv("MAX_ANSWER_TOKEN_PER_PAGE", 512))

# Searxng
SEARXNG_BASE_URL=os.getenv("SEARXNG_BASE_URL")

# Google
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
GOOGLE_SEARCH_ENGINE_ID=os.getenv("GOOGLE_SEARCH_ENGINE_ID")

