# gpt_code_gen

`gpt_code_gen` is a Python tool that can help you generate boilerplate code from a large codebase using GPT.

## Usage
To use `gpt_code_gen`, you need to have Python 3.9+ installed. Run the following command:
```sh
python3 -m pip install -r requirements.txt

python3 main.py \
    --input-dir=/Your/Path/inputs \
    --output-dir=/Your/Path/outputs \
    --file-name-prompt-path=/Your/Path/your_file_name_prompt.yaml \
    --process-prompt-path=/Your/Path/your_process_prompt.yaml \
    --output-template-prompt-path=/Your/Path/your_output_template_prompt.yaml \
    --[no-]include-relative-code-snippets \
    --language=cxx
```

### Arguments
The following arguments are available for use:

- `input-dir`: The directory containing your source files.
- `output-dir`: The directory where you want the generated files to be saved.
- `file-name-prompt-path`: The YAML file that specifies how to create the file name based on the class name. See [file_name_prompt.yaml](examples/cxx_wrapper_functions/promptions/file_name_prompt.yaml) for an example.
- `process-prompt-path`: The YAML file that specifies how to process the functions for the class. See [wrapper_function_prompt.yaml](examples/cxx_wrapper_functions/promptions/wrapper_function_prompt.yaml) for an example.
- `output-template-prompt-path`: The YAML file that specifies how to create the final output content template. The template should contain the key `{{ BODY }}`. See [wrapper_class_template_prompt.yaml](examples/cxx_wrapper_functions/promptions/wrapper_class_template_prompt.yaml) for an example.
- `--[no-]include-relative-code-snippets`: Whether to include the relative code snippets of the type from the function parameter list, structs. This flag defaults to true to provide as much information as possible to the [GPT-3.5](https://platform.openai.com/docs/models/gpt-3-5) model. You can set it to false to reduce token usage.
- `language`: The programming language. Only "cxx" is currently supported.

### Prompt format
The YAML files specified by the `file-name-prompt-path`, `process-prompt-path`, and `output-template-prompt-path` arguments use the following prompt format, which matches the format of OpenAI's [chat completion](https://platform.openai.com/docs/guides/chat/introduction) API:

```yaml
- role: system
  content: The system content
  
- role: user
  content: This is the user content

- role: assistant
  content: This is the assistant content
```

### Examples
> The examples use the [Agora Windows C++ headers](https://docs.agora.io/en/sdks?platform=windows) as input.

- Generate the `MOCK_METHOD`s of gMock, see `examples/cxx_gmock` for example.
- Generate wrapper functions that take the parameters from the json, and pass it to the original functions, see  `examples/cxx_wrapper_functions` for example.

## Add new language support
To add support for a new language, implement the `CodeSnippetExtractor` to extract the new language to the `CodeSnippetFile`. See [cxx_code_snippet_extractor.py](src/cxx_code_snippet_extractor.py) for an example.

## Contributing
Currently, the project only supports C++. However, it may be expanded according to the actual work content. If you are interested in the project and willing to expand it to help more people, welcome to submit a pull request.

## License
The project is under the Apache License.