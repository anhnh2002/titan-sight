from openai import AsyncOpenAI
from typing import List


class EmbeddingClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        embedding_model_name: str,
    ):
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key
        )

        self.embedding_model_name = embedding_model_name

    async def get_embedding(self, text: str) -> List[float]:
        response = await self.client.embeddings.create(
            model=self.embedding_model_name,
            input=text,
        )

        return response.data[0].embedding