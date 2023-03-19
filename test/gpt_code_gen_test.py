
import os
import tempfile
import unittest
from typing import List
from unittest.mock import MagicMock

import aiohttp
from mock import patch

from src.code_snippet_extractor import CodeSnippet, CodeSnippetFile
from src.cxx_code_snippet_extractor import CXXCodeSnippetExtractor
import src.gpt_code_gen
from src.gpt_code_gen import DefaultResponseHandler, DefaultRequestBuilder, GPTCodeGen, RequestBuilder, ResponseHandler


class TestResponseHandler(ResponseHandler):
    progress_request_code_snippet: List[str]
    progress_completions: List[str]
    complete_completions: List[str]

    def __init__(self) -> None:
        self.progress_request_code_snippet = []
        self.progress_completions = []
        self.complete_completions = []

    def on_start(self,
                 code_snippet_file: CodeSnippetFile,
                 code_snippet: CodeSnippet):
        return

    def on_progress(self,
                    code_snippet_file: CodeSnippetFile,
                    code_snippet: CodeSnippet,
                    request_codeSnippet: str,
                    completion: str):
        self.progress_request_code_snippet.append(request_codeSnippet)
        self.progress_completions.append(completion)

    def on_complete(self, code_snippet_file: CodeSnippetFile, code_snippet: CodeSnippet, completions: List[str]):
        self.complete_completions.extend(completions)


class TestRequestBuilder(RequestBuilder):

    def build_request_messages(self, code_snippet_file: CodeSnippetFile, code_snippet: CodeSnippet) -> List[str]:
        return list(map(lambda x: x.source.strip(), code_snippet.codeSnippets))


class TestGPTCodeGen(unittest.TestCase):

    __cxx_code_snippet_extractor: CXXCodeSnippetExtractor
    __gpt_code_gen: GPTCodeGen
    __output_dir: str
    __tmp_dir: tempfile.TemporaryDirectory
    __test_response_handler: TestResponseHandler

    @classmethod
    def setUpClass(self):
        self.__tmp_dir = tempfile.TemporaryDirectory("gpt_code_gen_test")

        self.__cxx_code_snippet_extractor = CXXCodeSnippetExtractor()
        self.__output_dir = os.path.join(self.__tmp_dir.name, "output")
        os.mkdir(self.__output_dir)

        self.__test_response_handler = TestResponseHandler()
        self.__gpt_code_gen = GPTCodeGen()

    @classmethod
    def tearDownClass(self):
        # use temp_dir, and when done:
        self.__tmp_dir.cleanup()

    @patch('src.api_request_parallel_processor.num_tokens_consumed_from_request')
    def test_gpt_code_gen(self, num_tokens_mock):
        num_tokens_mock.return_value = 10

        res = {"id": "96", "object": "chat.completion", "created": 1680964891, "model": "gpt-3.5-turbo-0301", "usage": {"prompt_tokens": 1984, "completion_tokens": 399,
                                                                                                                        "total_tokens": 2383}, "choices": [{"message": {"role": "assistant", "content": "fake content"}, "finish_reason": "stop", "index": 0}]}
        # FIXME(littlegnal): Figure it out how to mock the `aiohttp.ClientSession` with side effect
        mock = aiohttp.ClientSession
        mock.post = MagicMock()
        mock.post.return_value.__aenter__.return_value.status = 200
        mock.post.return_value.__aenter__.return_value.json.return_value = res

        intput_dir = os.path.join(self.__tmp_dir.name, "input")
        os.mkdir(intput_dir)
        intput_path1 = os.path.join(intput_dir, "intput_class.h")
        with open(intput_path1, "w") as f:
            f.write("""
class ClassA {
    virtual void release(bool sync = false) = 0;
    
    virtual int initialize() = 0;
    
    virtual int stopEchoTest() = 0;
};
""")

        prompt_path = os.path.join(intput_dir, "prompt.yaml")
        with open(prompt_path, "w") as f:
            f.write("""
- role: system
  content: |
    This is the prompt

- role: user
  content: |
    virtual void release(bool sync = false) = 0;

- role: assistant
  content: |
    void release(bool sync = false) {
        return;
    }
""")

        cxx_files = self.__cxx_code_snippet_extractor.extract([intput_path1])

        # The `DefaultResponseHandler` has been tested in `TestDefaultResponseHandler`,
        # it's ok that use a fake `ResponseHandler` to test the response output here.
        self.__gpt_code_gen.generate(cxx_files,
                                     DefaultRequestBuilder(prompt_path),
                                     self.__test_response_handler,)

        self.assertEqual(self.__test_response_handler.progress_request_code_snippet,
                         [
                             "virtual void release(bool sync = false) = 0;",
                             "virtual int initialize() = 0;",
                             "virtual int stopEchoTest() = 0;",
                         ])
        self.assertEqual(self.__test_response_handler.progress_completions, [
                         "fake content", "fake content", "fake content"])
        self.assertEqual(self.__test_response_handler.complete_completions, [
                         "fake content", "fake content", "fake content"])


class TestDefaultResponseHandler(unittest.TestCase):
    __output_dir: str
    __tmp_dir: tempfile.TemporaryDirectory

    @classmethod
    def setUpClass(self):
        self.__tmp_dir = tempfile.TemporaryDirectory("gpt_code_gen_test")

        self.__output_dir = os.path.join(self.__tmp_dir.name, "output")
        os.mkdir(self.__output_dir)

    @classmethod
    def tearDownClass(self):
        self.__tmp_dir.cleanup()

    def __get_chat_completion_mock_side_effect(self, *args, **kwargs):
        file_name_messages = [
            {"role": "system", "content": "The system content"},
            {"role": "user", "content": "MyClass"},
            {"role": "assistant",
             "content": "myclass_gen.hpp"},
            {"role": "user", "content": "MyClass"},
        ]
        if kwargs['messages'] == file_name_messages:
            return "myclass_gen.hpp"

        return "/// GENERATED BY gpt_code_gen, DO NOT MODIFY BY HAND.\n{{ BODY }}"

    @patch('src.gpt_code_gen.get_chat_completion')
    def test_onstart(self, get_chat_completion_mock):
        get_chat_completion_mock.side_effect = self.__get_chat_completion_mock_side_effect

        output_template_prompt_path = os.path.join(
            self.__output_dir, "output_template_prompt.yaml")
        file_name_prompt_path = os.path.join(
            self.__output_dir, "file_name_prompt.yaml")

        with open(output_template_prompt_path, "w") as f:
            f.write("""
- role: system
  content: The system content

- role: user
  content: MyClass

- role: assistant
  content: |
    /// GENERATED BY gpt_code_gen, DO NOT MODIFY BY HAND.
    {{ BODY }}
""")

        with open(file_name_prompt_path, "w") as f:
            f.write("""
- role: system
  content: The system content
  
- role: user
  content: MyClass

- role: assistant
  content: myclass_gen.hpp                 
""")

        response_handler = DefaultResponseHandler(
            output_template_prompt_path, file_name_prompt_path, self.__output_dir)

        csf = CodeSnippetFile
        cs = CodeSnippet
        cs.name = "MyClass"

        response_handler.on_start(csf, cs)

        expected_output_file_path = os.path.join(
            self.__output_dir, "myclass_gen.hpp")

        self.assertEqual(
            response_handler._DefaultResponseHandler__output_file_path, expected_output_file_path)

        build_tmp_path = src.gpt_code_gen._get_build_tmp_path()
        expected_tmp_path = os.path.join(build_tmp_path, "myclass_gen.hpp.tmp")
        self.assertEqual(
            response_handler._DefaultResponseHandler__output_file_path_tmp, expected_tmp_path)

        expected_output_template = """
/// GENERATED BY gpt_code_gen, DO NOT MODIFY BY HAND.
{{ BODY }}
""".strip("\n")
        self.assertEqual(
            response_handler._DefaultResponseHandler__output_template, expected_output_template)

    def __get_chat_completion_mock_side_effect_will_raise(self, *args, **kwargs):
        file_name_messages = [
            {"role": "system", "content": "The system content"},
            {"role": "user", "content": "MyClass"},
            {"role": "assistant",
             "content": "myclass_gen.hpp"},
            {"role": "user", "content": "MyClass"},
        ]
        if kwargs['messages'] == file_name_messages:
            return "myclass_gen.hpp"

        return "/// GENERATED BY gpt_code_gen, DO NOT MODIFY BY HAND."

    @patch('src.gpt_code_gen.get_chat_completion')
    def test_onstart_raise_exception(self, get_chat_completion_mock):
        get_chat_completion_mock.side_effect = self.__get_chat_completion_mock_side_effect_will_raise

        output_template_prompt_path = os.path.join(
            self.__output_dir, "output_template_prompt.yaml")
        file_name_prompt_path = os.path.join(
            self.__output_dir, "file_name_prompt.yaml")

        with open(output_template_prompt_path, "w") as f:
            f.write("""
- role: system
  content: The system content

- role: user
  content: MyClass

- role: assistant
  content: |
    /// GENERATED BY gpt_code_gen, DO NOT MODIFY BY HAND.
    {{ BODY }}
""")

        with open(file_name_prompt_path, "w") as f:
            f.write("""
- role: system
  content: The system content
  
- role: user
  content: MyClass

- role: assistant
  content: myclass_gen.hpp                 
""")

        response_handler = DefaultResponseHandler(
            output_template_prompt_path, file_name_prompt_path, self.__output_dir)

        csf = CodeSnippetFile
        cs = CodeSnippet
        cs.name = "MyClass"

        with self.assertRaises(SystemExit) as cm:
            response_handler.on_start(csf, cs)

        self.assertEqual(
            cm.exception.code,
            'The template should contain the template key "{{ BODY }}", please check your prompt.')

    @patch('src.gpt_code_gen.get_chat_completion')
    def test_onprogress(self, get_chat_completion_mock):
        get_chat_completion_mock.side_effect = self.__get_chat_completion_mock_side_effect

        output_template_prompt_path = os.path.join(
            self.__output_dir, "output_template_prompt.yaml")
        file_name_prompt_path = os.path.join(
            self.__output_dir, "file_name_prompt.yaml")

        with open(output_template_prompt_path, "w") as f:
            f.write("""
- role: system
  content: The system content

- role: user
  content: MyClass

- role: assistant
  content: |
    /// GENERATED BY gpt_code_gen, DO NOT MODIFY BY HAND.
    {{ BODY }}
""")

        with open(file_name_prompt_path, "w") as f:
            f.write("""
- role: system
  content: The system content
  
- role: user
  content: MyClass

- role: assistant
  content: myclass_gen.hpp                 
""")

        response_handler = DefaultResponseHandler(
            output_template_prompt_path, file_name_prompt_path, self.__output_dir)

        csf = CodeSnippetFile
        cs = CodeSnippet
        cs.name = "MyClass"

        response_handler.on_start(csf, cs)

        request_code_snippet1 = "virtual int initialize() = 0;"
        completion1 = "int initialize() {}"

        response_handler.on_progress(
            csf, cs, request_code_snippet1, completion1)

        request_code_snippet2 = "virtual int initialize2() = 0;"
        completion2 = "int initialize2() {}"

        response_handler.on_progress(
            csf, cs, request_code_snippet2, completion2)

        output_file_path_tmp = os.path.join(
            src.gpt_code_gen._get_build_tmp_path(), "myclass_gen.hpp.tmp")

        expected_output = """
/// GENERATED BY gpt_code_gen, DO NOT MODIFY BY HAND.
/// virtual int initialize() = 0;
int initialize() {}

/// virtual int initialize2() = 0;
int initialize2() {}
""".strip("\n")

        with open(output_file_path_tmp) as f:
            self.assertEqual(f.read(), expected_output)

    @patch('src.gpt_code_gen.get_chat_completion')
    def test_oncomplete(self, get_chat_completion_mock):
        get_chat_completion_mock.side_effect = self.__get_chat_completion_mock_side_effect

        output_template_prompt_path = os.path.join(
            self.__output_dir, "output_template_prompt.yaml")
        file_name_prompt_path = os.path.join(
            self.__output_dir, "file_name_prompt.yaml")

        with open(output_template_prompt_path, "w") as f:
            f.write("""
- role: system
  content: The system content

- role: user
  content: MyClass

- role: assistant
  content: |
    /// GENERATED BY gpt_code_gen, DO NOT MODIFY BY HAND.
    {{ BODY }}
""")

        with open(file_name_prompt_path, "w") as f:
            f.write("""
- role: system
  content: The system content
  
- role: user
  content: MyClass

- role: assistant
  content: myclass_gen.hpp                 
""")

        response_handler = DefaultResponseHandler(
            output_template_prompt_path, file_name_prompt_path, self.__output_dir)

        csf = CodeSnippetFile
        cs = CodeSnippet
        cs.name = "MyClass"

        response_handler.on_start(csf, cs)

        completion1 = "int initialize() {}"
        completion2 = "int initialize2() {}"

        response_handler.on_complete(csf, cs, [completion1, completion2])

        output_file_path = os.path.join(
            self.__output_dir, "myclass_gen.hpp")

        expectedOutput = """
/// GENERATED BY gpt_code_gen, DO NOT MODIFY BY HAND.
int initialize() {}

int initialize2() {}
""".strip("\n")

        with open(output_file_path) as f:
            self.assertEqual(f.read(), expectedOutput)
