import asyncio  # for running API calls concurrently
import json
import logging
import os
from typing import List

import yaml

from .api_request_parallel_processor import process_api_requests_from_file
from .code_snippet_extractor import ChunkCodeSnippet, CodeSnippet, CodeSnippetFile
from abc import ABC, abstractmethod

from .openai_api import get_chat_completion


class ResponseHandler(ABC):
    @abstractmethod
    def on_start(self,
                 code_snippetFile: CodeSnippetFile,
                 code_snippet: CodeSnippet):
        pass

    @abstractmethod
    def on_progress(self,
                    code_snippet_file: CodeSnippetFile,
                    code_snippet: CodeSnippet,
                    request_code_snippet: str,
                    completion: str):
        pass

    @abstractmethod
    def on_complete(self, code_snippet_file: CodeSnippetFile, code_snippet: CodeSnippet, completions: List[str]):
        pass


class RequestBuilder(ABC):
    def build_request_messages(self, code_snippet_file: CodeSnippetFile, code_snippet: CodeSnippet) -> List[List[str]]:
        pass


def create_gpt_messages(prompt_path: str, content: str) -> List[str]:
    messages: List[dict] = []
    with open(prompt_path) as f:
        prompt = f.read()

        y = yaml.safe_load_all(prompt)
        for d in y:
            for dd in d:
                messages.append(dd)

        messages.append({"role": "user", "content": content})

    return messages


def _get_build_tmp_path() -> str:
    build_tmp_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "..", "build", "tmp")
    if not os.path.exists(build_tmp_path):
        os.makedirs(build_tmp_path)

    return build_tmp_path


class DefaultRequestBuilder(RequestBuilder):
    __process_prompt_path: str
    __include_relative_code_snippets: bool

    def __init__(self, process_prompt_path: str, include_relative_code_snippets: bool = True) -> None:
        self.__process_prompt_path = process_prompt_path
        self.__include_relative_code_snippets = include_relative_code_snippets

    def build_request_messages(self, code_snippet_file: CodeSnippetFile, code_snippet: CodeSnippet) -> List[List[str]]:
        if not isinstance(code_snippet, ChunkCodeSnippet):
            return []

        request_contents: List[List[str]] = []

        for ccs in code_snippet.code_snippets:
            content = ccs.source.strip()
            if self.__include_relative_code_snippets:
                relative_code_snippets = "\n".join(
                    list(map(lambda cs: cs.source, ccs.relative_code_snippets)))
                content = (
                    relative_code_snippets + "\n\n" if relative_code_snippets else "") + content

            messages = create_gpt_messages(
                self.__process_prompt_path, content)
            request_contents.append(messages)

        return request_contents


class DefaultResponseHandler(ResponseHandler):
    __output_dir: str

    __output_template_prompt_path: str
    __file_name_prompt_path: str
    __output_template: str

    __output_file_path: str
    __output_file_path_tmp: str

    __processing_contents: List[str]

    def __init__(self, output_template_prompt_path: str, file_name_prompt_path: str, output_dir: str) -> None:
        self.__output_dir = output_dir
        self.__output_file_path = ""
        self.__output_file_path_tmp = ""
        self.__processing_contents = []

        self.__output_template_prompt_path = output_template_prompt_path
        self.__file_name_prompt_path = file_name_prompt_path

    def on_start(self,
                 code_snippet_file: CodeSnippetFile,
                 code_snippet: CodeSnippet):

        print(f'Creating file name for: {code_snippet.name}')
        file_name_messages = create_gpt_messages(
            self.__file_name_prompt_path, code_snippet.name)
        file_name = get_chat_completion(
            messages=file_name_messages,
            model="gpt-3.5-turbo",
            temperature=0)
        print(f'file name: {file_name}')

        output_file_name = file_name
        self.__output_file_path = os.path.join(
            os.path.abspath(self.__output_dir), output_file_name)

        if os.path.exists(self.__output_file_path):
            os.remove(self.__output_file_path)

        build_tmp_path = _get_build_tmp_path()
        self.__output_file_path_tmp = os.path.join(
            build_tmp_path, output_file_name + ".tmp")

        if os.path.exists(self.__output_file_path):
            os.remove(self.__output_file_path)

        if os.path.exists(self.__output_file_path_tmp):
            os.remove(self.__output_file_path_tmp)

        print(f'Creating output template for: {code_snippet.name}')
        output_template_messages = create_gpt_messages(
            self.__output_template_prompt_path, code_snippet.name)
        self.__output_template = get_chat_completion(
            messages=output_template_messages,
            model="gpt-3.5-turbo",
            temperature=0)
        print(f'Output template:\n {self.__output_template}')

        if "{{ BODY }}" not in self.__output_template:
            raise SystemExit(
                'The template should contain the template key "{{ BODY }}", please check your prompt.')

    def on_progress(self,
                    code_snippet_file: CodeSnippetFile,
                    code_snippet: CodeSnippet,
                    request_code_snippet: str,
                    completion: str):
        comments = "\n".join(
            list(map(lambda x: "/// " + x, request_code_snippet.split("\n"))))
        self.__processing_contents.append(comments + "\n" + completion)

        file_content = self.__output_template.replace(
            "{{ BODY }}", "\n\n".join(self.__processing_contents))

        with open(self.__output_file_path_tmp, "w") as f:
            f.write(file_content)

    def on_complete(self, code_snippet_file: CodeSnippetFile, code_snippet: CodeSnippet, completions: List[str]):
        file_content = self.__output_template.replace(
            "{{ BODY }}", "\n\n".join(completions))

        with open(self.__output_file_path, "w") as f:
            f.write(file_content)

        print(f"All completions write to: {self.__output_file_path}")


class _CompletionHandler:
    __output_file_path: str
    __processing_result_save_path: str

    __code_snippet_file: CodeSnippetFile
    __code_snippet: CodeSnippet
    __output_content_handler: ResponseHandler

    def __init__(self, output_file_path: str, code_snippet_file: CodeSnippetFile,
                 code_snippet: CodeSnippet, output_content_handler: ResponseHandler):
        self.__code_snippet_file = code_snippet_file
        self.__code_snippet = code_snippet
        self.__output_content_handler = output_content_handler

        self.__output_file_path = output_file_path

        self.__processing_result_save_path = self.__output_file_path.replace(
            ".jsonl", "_processing.jsonl")

        if os.path.exists(self.__processing_result_save_path):
            os.remove(self.__processing_result_save_path)

        open(self.__processing_result_save_path, 'w').close()

        self.__output_content_handler.on_start(
            self.__code_snippet_file, self.__code_snippet)

    def __call__(self, task_id, request_data, response):
        messages = request_data["messages"]
        request_content = messages[len(messages) - 1]["content"]
        completion = response["choices"][0]['message']['content'].strip()
        json_string = json.dumps(
            {"task_id": task_id, "request_content": request_content, "completion": completion})

        with open(self.__processing_result_save_path, "a") as f:
            f.write(json_string + "\n")

        self.__output_content_handler.on_progress(
            self.__code_snippet_file, self.__code_snippet, request_content, completion)

    def __get_all_completions(self) -> List[str]:
        completions: List[str] = []
        tmp_completions: List[dict] = []
        with open(self.__processing_result_save_path, "r") as f:
            for line in f.readlines():
                tmp_completions.append(json.loads(line))

            tmp_completions = sorted(
                tmp_completions, key=lambda x: x["task_id"])

            completions = map(lambda x: x["completion"], tmp_completions)

        return completions

    def complete(self):
        self.__output_content_handler.on_complete(
            self.__code_snippet_file, self.__code_snippet, self.__get_all_completions())


class GPTCodeGen:
    __model: str
    __max_requests_per_minute: int

    def __init__(self, model: str = "gpt-3.5-turbo", max_requests_per_minute: int = 2) -> None:
        self.__model = model
        self.__max_requests_per_minute = max_requests_per_minute

    def __generate_requests_file(
            self,
            code_snippet: ChunkCodeSnippet,
            cxx_file_path: str,
            output_dir: str,
            request_contents: List[List[str]]) -> str:
        output_file_name = f'{os.path.splitext(os.path.basename(cxx_file_path))[0]}_{code_snippet.name}_requests.jsonl'
        output_file_path = os.path.join(
            os.path.abspath(output_dir), output_file_name)

        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        requests: List[dict] = []
        for messages in request_contents:
            requests.append(
                {"model": self.__model, "messages": messages, "temperature": 0})

        with open(output_file_path, "w") as f:
            for job in requests:
                json_string = json.dumps(job)
                f.write(json_string + "\n")

        return output_file_path

    def __request(self, requests_file_path: str, save_completion: _CompletionHandler, max_requests_per_minute: int):
        save_file_path = requests_file_path.replace(
            ".jsonl", "_results.jsonl")
        request_url = "https://api.openai.com/v1/chat/completions"
        api_key = os.getenv("OPENAI_API_KEY")

        max_tokens_per_minute = 250_000 * 0.5
        token_encoding_name = "cl100k_base"
        max_attempts = 10
        logging_level = logging.INFO

        # run script
        asyncio.run(
            process_api_requests_from_file(
                requests_filepath=requests_file_path,
                save_filepath=save_file_path,
                request_url=request_url,
                api_key=api_key,
                max_requests_per_minute=float(max_requests_per_minute),
                max_tokens_per_minute=float(max_tokens_per_minute),
                token_encoding_name=token_encoding_name,
                max_attempts=int(max_attempts),
                logging_level=int(logging_level),
                on_success=save_completion
            )
        )

        save_completion.complete()

    def generate(
            self,
            code_snippet_files: List[CodeSnippetFile],
            request_builder: RequestBuilder,
            response_handler: ResponseHandler):
        build_tmp_path = _get_build_tmp_path()

        for cxx_file in code_snippet_files:
            for cs in cxx_file.code_snippets:
                request_contents = request_builder.build_request_messages(
                    cxx_file, cs)

                if (len(request_contents) > 0):
                    requests_file_path = self.__generate_requests_file(
                        cs,
                        cxx_file.file_path,
                        build_tmp_path,
                        request_contents)

                    save_completion = _CompletionHandler(
                        requests_file_path,
                        cxx_file,
                        cs,
                        response_handler)

                    self.__request(requests_file_path,
                                   save_completion,
                                   self.__max_requests_per_minute)
