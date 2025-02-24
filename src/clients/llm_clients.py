from openai import AsyncOpenAI
from transformers import AutoTokenizer
import tiktoken

from typing import List, Optional
from schemas import SearchResult

from prompt_template import CONCISE_ANSWER_PROMPT
from constants import MAX_PAGE_DETAILS_LENGTH, MAX_ANSWER_TOKEN_PER_PAGE

class LLMClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model_name: str,
        base_model_name: str,
        hf_token: Optional[str]=None,
    ):
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
        )

        self.model_name = model_name

        try:
            # Use the tokenizer from tiktoken if available
            self.tokenizer = tiktoken.encoding_for_model(base_model_name)
        except:
            # Use the Hugging Face tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_name, token=hf_token)


    async def count_tokens(self, text: str) -> int:
        tokenized: List[int] = self.tokenizer.encode(text)
        return len(tokenized)


    async def complettion(self, prompt: str) -> str:

        completion = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt},
            ],
            top_p=0.5,
            max_tokens=MAX_ANSWER_TOKEN_PER_PAGE,
        )

        return completion.choices[0].message.content.strip()
    

    async def summarize_page(self, query: str, search_result: SearchResult) -> str:

        title = search_result.title
        url = search_result.url
        summary = search_result.content
        details = search_result.details

        # truncate MAX_PAGE_DETAILS_LENGTH tokens from the details
        if details:

            truncated = ""
            current_num_tokens = 0

            for line in details.split("\n"):

                line_num_tokens = await self.count_tokens(line)

                if current_num_tokens + line_num_tokens > MAX_PAGE_DETAILS_LENGTH:
                    break

                truncated += line + "\n"
                current_num_tokens += line_num_tokens

            details = truncated
        
        prompt = CONCISE_ANSWER_PROMPT.format(
            title=title,
            url=url,
            summary=summary,
            details=details,
            query=query,
        )

        return await self.complettion(prompt)





    