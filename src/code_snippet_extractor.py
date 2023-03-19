from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel


class CodeSnippet(BaseModel):
    type: str = None
    name: str = None
    source: str = ""
    start: int = 0
    end: int = 0
    relative_code_snippets: List[CodeSnippet] = []


class ChunkCodeSnippet(CodeSnippet):
    code_snippets: List[CodeSnippet] = []


class CodeSnippetFile(BaseModel):
    code_snippets: List[CodeSnippet] = []
    file_path: str = ""


class CodeSnippetExtractor(ABC):

    @abstractmethod
    def extract(self, filePaths: List[str]) -> List[CodeSnippetFile]:
        """
        Extract the code snippets from the given file paths, and return the extracted code snippets.
        """
        pass
