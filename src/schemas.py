# Code here is based on github.com/rashadphz/farfalle

from typing import List, Optional

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    title: str
    url: str
    content: str
    details: Optional[str] = None
    answer: Optional[str] = None
    

    def __str__(self):
        return f"Title: {self.title}\nURL: {self.url}\n Summary: {self.content}"


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult] = Field(default_factory=list)

