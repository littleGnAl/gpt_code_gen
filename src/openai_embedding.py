from typing import List
import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_not_exception_type
import tiktoken
from itertools import islice
import numpy as np
from openai.embeddings_utils import cosine_similarity
import pandas as pd
from pandas import DataFrame

from src.cpp_code_snippet_extractor import CodeSnippet


EMBEDDING_MODEL = 'text-embedding-ada-002'
EMBEDDING_CTX_LENGTH = 8191
EMBEDDING_ENCODING = 'cl100k_base'


class OpenAIEmbedding:

    __dataFrame: DataFrame
    
    def __init__(self) -> None:
        self.__dataFrame = None

    # let's make sure to not retry on an invalid request, because that is what we want to demonstrate
    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6), retry=retry_if_not_exception_type(openai.InvalidRequestError))
    def get_embedding(self, text_or_tokens, model=EMBEDDING_MODEL):
        return openai.Embedding.create(input=text_or_tokens, model=model)["data"][0]["embedding"]

    def truncate_text_tokens(self, text, encoding_name=EMBEDDING_ENCODING, max_tokens=EMBEDDING_CTX_LENGTH):
        """Truncate a string to have `max_tokens` according to the given encoding."""
        encoding = tiktoken.get_encoding(encoding_name)
        return encoding.encode(text)[:max_tokens]

    def batched(self, iterable, n):
        """Batch data into tuples of length n. The last batch may be shorter."""
        # batched('ABCDEFG', 3) --> ABC DEF G
        if n < 1:
            raise ValueError('n must be at least one')
        it = iter(iterable)
        while (batch := tuple(islice(it, n))):
            yield batch

    def chunked_tokens(self, text, encoding_name, chunk_length):
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)

        chunks_iterator = self.batched(tokens, chunk_length)
        yield from chunks_iterator

    def len_safe_get_embedding(self, text, model=EMBEDDING_MODEL, max_tokens=EMBEDDING_CTX_LENGTH, encoding_name=EMBEDDING_ENCODING, average=True):
        chunk_embeddings = []
        chunk_lens = []
        for chunk in self.chunked_tokens(text, encoding_name=encoding_name, chunk_length=max_tokens):
            chunk_embeddings.append(self.get_embedding(chunk, model=model))
            chunk_lens.append(len(chunk))

        if average:
            chunk_embeddings = np.average(
                chunk_embeddings, axis=0, weights=chunk_lens)
            chunk_embeddings = chunk_embeddings / \
                np.linalg.norm(chunk_embeddings)  # normalizes length to 1
            chunk_embeddings = chunk_embeddings.tolist()
        return chunk_embeddings

    # def searchCodes(self, code_query, n=3, pprint=True, n_lines=1000):
    #     # embedding = self.len_safe_get_embedding(code_query)
    #     encoding = tiktoken.get_encoding(EMBEDDING_ENCODING)
    #     num_tokens = len(encoding.encode(sourceCodes))
    #     print(f'num_tokens: {num_tokens}')

        # df = pd.DataFrame([{"code":sourceCodes}])
        # df['code_embedding'] = df['code'].apply(lambda x: self.len_safe_get_embedding(x))
        # # df['filepath'] = df['filepath'].apply(lambda x: x.replace(code_root, ""))
        # df.to_csv("code_search_openai-python.csv", index=False)
        # df.head()

        # embedding = self.len_safe_get_embedding(code_query)
        # df['similarities'] = df.code_embedding.apply(lambda x: cosine_similarity(x, embedding))

        # code_completion = openai.Completion.create(
        #     engine="text-davinci-002",
        #     prompt=f"Find {code_query} following embedding: {self.len_safe_get_embedding(sourceCodes)[0:50]}",
        #     max_tokens=3000,
        #     stream=True
        # )
        # print(code_completion)

        # generated_code = code_completion.choices[0].text

        # res = df.sort_values('similarities', ascending=False).head(n)
        # if pprint:
        #     for r in res.iterrows():
        #         print("  score=" + str(round(r[1].similarities, 3)))
        #         print("\n".join(r[1].code.split("\n")[:n_lines]))
        #         print('-'*70)

        # df = pd.DataFrame([sourceCodes], columns=["source", "ada_embedding"])
        # df['ada_embedding'] = df.source.apply(lambda x: self.len_safe_get_embedding(x))
        # df.to_csv('output/embedded_1k_reviews.csv', index=True)

        # df = pd.read_csv('output/embedded_1k_reviews.csv')
        # df['ada_embedding'] = df.ada_embedding.apply(eval).apply(np.array)

        # df['similarities'] = df.code_embedding.apply(lambda x: cosine_similarity(x, embedding))

        # res = df.sort_values('similarities', ascending=False).head(n)
        # if pprint:
        #     for r in res.iterrows():
        #         print(r[1].filepath+":"+r[1].function_name + "  score=" + str(round(r[1].similarities, 3)))
        #         print("\n".join(r[1].code.split("\n")[:n_lines]))
        #         print('-'*70)

        # prompt = "Generate some text based on this input:"
        # response = openai.Completion.create(
        #     engine="text-davinci-002",
        #     prompt=prompt,
        #     max_tokens=100,
        #     n=1,
        #     temperature=0.5,
        #     logprobs=10,
        #     input_embeddings=[embedding.id]
        # )

        # # Print the generated text
        # generated_text = response.choices[0].text
        # print(generated_text)

        # return res

    def embeddingCodeBlocks(self, codeBlocks: List[CodeSnippet]):
        codes: dict[str] = []
        for block in codeBlocks:
            codes.append({"code": block.codeBlocks})

        if self.__dataFrame is None:
            self.__dataFrame = pd.DataFrame(codes)

        df = self.__dataFrame

        # df = pd.DataFrame(codes)
        df['code_embedding'] = df['code'].apply(
            lambda x: self.len_safe_get_embedding(x))
        # df['filepath'] = df['filepath'].apply(lambda x: x.replace(code_root, ""))
        df.to_csv("code_search_openai-python.csv", index=False)
        df.head()

    def searchCodes(self, code_query, n=3, pprint=True, n_lines=10):
        # embedding = self.len_safe_get_embedding(code_query)
        # encoding = tiktoken.get_encoding(EMBEDDING_ENCODING)
        # num_tokens = len(encoding.encode(sourceCodes))
        # print(f'num_tokens: {num_tokens}')

        # codes: dict[str] = []
        # for block in sourceCodes:
        #     codes.append({"code": block.codeBlocks})

        # df = pd.DataFrame(codes)
        # df['code_embedding'] = df['code'].apply(lambda x: self.len_safe_get_embedding(x))
        # # df['filepath'] = df['filepath'].apply(lambda x: x.replace(code_root, ""))
        # df.to_csv("code_search_openai-python.csv", index=False)
        # df.head()

        # df = pd.read_csv("code_search_openai-python.csv")
        # df.head()

        f = open("log.txt", "w")

        df = self.__dataFrame
        embedding = self.len_safe_get_embedding(code_query)
        df['similarities'] = df.code_embedding.apply(
            lambda x: cosine_similarity(x, embedding))
        res = df.sort_values('similarities', ascending=False).head(n)
        if pprint:
            for r in res.iterrows():
                # embedding = self.len_safe_get_embedding(code_query)
                # encoding = tiktoken.get_encoding(EMBEDDING_ENCODING)
                # num_tokens = len(encoding.encode(r[1].code))
                # print(f'num_tokens: {num_tokens}')

                print("  score=" + str(round(r[1].similarities, 3)))
                outputCode = "\n".join(r[1].code.split("\n")[:n_lines])
                print(outputCode)
                f.write(outputCode)
                print('-'*70)
                f.write('-'*70)
                
                code_completion = openai.Completion.create(
                    engine="text-davinci-002",
                    prompt=f"Is the code for `{code_query}` below, just reply me YES or NO:\n{outputCode}",
                    max_tokens=3500
                )
                # print(code_completion.choices[0].text)
                # cb.codeBlocks=code_completion['choices'][0]['text']
                print(code_completion['choices'][0]['text'])

        f.close()

        return res
