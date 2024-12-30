import redis
from redis.commands.search.field import (
    VectorField,
)

from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
import numpy as np

from .embedding_clients import EmbeddingClient
from pymongo import MongoClient, errors

from schemas import SearchResponse

from logs import logger


class ShortTermCacheClient:
    """
    A Redis-based cache client for short-term storage of search results with vector similarity search capabilities.
    This class implements a caching mechanism using Redis as the backend storage, specifically designed
    for storing and retrieving search results based on vector similarity searches. It utilizes Redis JSON
    and RediSearch for efficient storage and querying of vector embeddings.
    Attributes:
        client (redis.Redis): Redis client instance
        expire_time (int): Time in seconds after which cache entries expire
        sim_threshold (float): Similarity threshold for vector matching
        index_name (str): Name of the Redis search index
    Parameters:
        redis_url (str): URL for connecting to Redis instance
        expire_time (int): Cache expiration time in seconds
        sim_threshold (float): Threshold for vector similarity matching
        embedding_dim (int): Dimension of the vector embeddings
    """

    def __init__(
        self,
        redis_url: str,
        expire_time: int,
        sim_threshold: float,
        embedding_client: EmbeddingClient,
    ):
        self.client = redis.Redis.from_url(redis_url, decode_responses=True)

        self.expire_time = expire_time
        self.sim_threshold = sim_threshold

        self.index_name: str="idx:search_vss"
        self._create_index()

        self.embedding_client = embedding_client


    def _create_index(self):

        embedding_dim = len(self.embedding_client.get_embedding("test"))

        schema = (
            VectorField(
                "$.query_embedding",
                "FLAT",
                {
                    "TYPE": "FLOAT32",
                    "DIM": embedding_dim,
                    "DISTANCE_METRIC": "COSINE",
                },
                as_name="vector",
            )
        )

        definition = IndexDefinition(prefix=["search:"], index_type=IndexType.JSON)

        try:
            status = self.client.ft(self.index_name).create_index(fields=schema, definition=definition)
            logger.info(f"Index created: {status}")
        except Exception as e:
            logger.error(f"Error creating index: {e}")
    
        

    async def set(
        self,
        obj: SearchResponse,
    ):
        
        # validate the object
        obj = obj.model_dump()

        # get the embedding for the object
        obj["query_embedding"] = self.embedding_client.get_embedding(obj["query"])

        # generate a unique key for the object, format "seach:<id>"
        id = str(hash(str(obj)))
        key = f"search:{id}"

        # set the object in the cache
        set_ojb = self.client.json().set(key, "$", obj)

        # set the expiration time
        set_ex = self.client.expire(key, self.expire_time)

        return set_ojb, set_ex
    
    async def get(self, query: str) -> SearchResponse:
        
        # get the embedding for the query
        query_embedding = self.embedding_client.get_embedding(query)


        # create a query to search for similar embeddings
        query = (
            Query('(*)=>[KNN 1 @vector $query_vector AS vector_score]')
            .sort_by('vector_score')
            .return_fields('vector_score', 'id')
            .dialect(2)
        )

        # search for similar embeddings
        docs = self.client.ft(self.index_name).search(
            query,
            {
                "query_vector": np.array(query_embedding, dtype=np.float32).tobytes()
            }
        )

        if not docs:
            return None
        
        # get the first document
        doc = docs[0]

        # return null if the similarity score is below the threshold
        if doc.vector_score < self.sim_threshold:
            return None

        # get the object from the cache
        obj = self.client.json().get(doc.id)

        # log the query which was found
        logger.info(f"Found similar query: {obj}")

        return SearchResponse(**obj)



class LongTermCacheClient:
    """
    A cache client for long-term storage using MongoDB.
    This class provides caching functionality using MongoDB as the backend storage system.
    It stores search results with their associated URLs for long-term persistence.
    Attributes:
        collection: MongoDB collection object for storing cache entries
    Args:
        mongo_url (str): MongoDB connection URL
        db_name (str): Name of the MongoDB database to use
        collection_name (str): Name of the collection to store cache entries
    Methods:
        set(search_response): Stores search results in the cache
        get(url): Retrieves cached details for a given URL
    Raises:
        errors.ConnectionFailure: If connection to MongoDB fails
    """


    def __init__(
        self,
        mongo_url: str,
        db_name: str,
        collection_name: str,
    ):
        try:
            mongo_client = MongoClient(mongo_url)
        except errors.ConnectionFailure as error:
            logger.info(f"Error: {error}")
            raise error
        db = mongo_client[db_name]

        self.collection = db[collection_name]

        # create an index on the URL field if it doesn't exist
        if "url_1" not in self.collection.index_information():
            self.collection.create_index("url", unique=True)


    async def set(self, search_response: SearchResponse):

        # validate the object
        urls_details = [{"url": result.url, "details": result.details} for result in search_response.results]

        # insert the object in the collection
        return self.collection.insert_many(urls_details)


    async def get(self, url: str) -> str:
        # get the object from the collection
        doc = self.collection.find_one({"url": url})

        if not doc:
            return None
        
        # log the url which was found
        logger.info(f"Found details for URL: {url}")

        return doc["details"]