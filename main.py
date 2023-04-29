import argparse
import asyncio
from enum import Enum
import os
import sys

import aiohttp
from src.cxx_code_snippet_extractor import CXXCodeSnippetExtractor
from src.gpt_code_gen import DefaultResponseHandler, DefaultRequestBuilder, GPTCodeGen
import semantic_kernel as sk
from semantic_kernel.ai.open_ai import OpenAITextCompletion

import openai


class LanguageType(str, Enum):
    cxx = "cxx"


async def main():
    root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(root)))

    parser = argparse.ArgumentParser(description='GPT code gen CLI')

    parser.add_argument('--input-dir', type=str,
                        help='The directory of the code files')
    parser.add_argument('--output-dir', type=str,
                        help='The directory of the output')
    parser.add_argument('--file-name-prompt-path', type=str,
                        help='The prmopt file path of how to named the file.')
    parser.add_argument('--process-prompt-path', type=str,
                        help='The prompt file path of how the functions be process.')
    parser.add_argument('--output-template-prompt-path', type=str,
                        help='The prompt file path of the output content template.')
    parser.add_argument('--language', type=str,
                        help='The program language of the intput code files, only support \"cxx\" at this time')
    parser.add_argument('--include-relative-code-snippets', action=argparse.BooleanOptionalAction,
                        help='Whether include the relative code snippets of the type from the function parameter list, struct')
    parser.add_argument('--rpm', type=int, default=2,
                        help='Requests per minute, see rate limits https://platform.openai.com/docs/guides/rate-limits/what-are-the-rate-limits-for-our-api')
    args = parser.parse_args()

    intput_dir = args.input_dir
    output_dir = args.output_dir
    file_name_prompt_path = args.file_name_prompt_path
    process_prompt_path = args.process_prompt_path
    output_template_prompt_path = args.output_template_prompt_path
    include_relative_code_snippets = args.include_relative_code_snippets
    rpm = args.rpm
    language_type = LanguageType(args.language)

    if language_type != LanguageType.cxx:
        print(f"The language of {language_type} is not supported yet.")
        return

    api_key = os.getenv("OPENAI_API_KEY")

    global_session = aiohttp.ClientSession(trust_env=True)
    openai.aiosession.set(global_session)

    sk_kernel = sk.Kernel()
    sk_kernel.config.add_text_backend(
        "dv", OpenAITextCompletion("text-davinci-003", api_key))

    cpp_extractor = CXXCodeSnippetExtractor()
    request_builder = DefaultRequestBuilder(
        process_prompt_path,
        include_relative_code_snippets)
    reponse_handler = DefaultResponseHandler(
        output_template_prompt_path, file_name_prompt_path, output_dir, sk_kernel)
    gpt_code_gen = GPTCodeGen(max_requests_per_minute=rpm)

    export_files = list(map(lambda p: os.path.join(
        os.path.abspath(intput_dir), p), os.listdir(intput_dir)))

    code_snippet_files = cpp_extractor.extract(export_files)

    # Only handle `IRtcEngine` for demostration purpose
    for code_snippet_file in code_snippet_files:
        code_snippet_file.code_snippets = list(filter(
            lambda x: (x.type == "class" and x.name ==
                       "IRtcEngine") or x.type != "class",
            code_snippet_file.code_snippets))

    await gpt_code_gen.generate(
        code_snippet_files,
        request_builder,
        reponse_handler)

    await global_session.close()


if __name__ == '__main__':
    asyncio.run(main())
