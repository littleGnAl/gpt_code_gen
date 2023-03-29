from typing import List
import fs.osfs
from fs.base import FS
import openai
import yaml

from src.cpp_code_snippet_extractor import (
    CPPCodeSnippetExtractor,
    ChunkCodeSnippet,
    CodeSnippet,
    CodeSnippetType
)


class OpenAICodeGen:
    __fileSystem: FS
    __cppCodeSnippetExtractor: CPPCodeSnippetExtractor

    def __init__(self, fileSystem: FS, cppCodeSnippetExtractor: CPPCodeSnippetExtractor) -> None:
        self.__fileSystem = fileSystem
        self.__cppCodeSnippetExtractor = cppCodeSnippetExtractor

    def generate(self,

                 wrapperTemplate: str,
                 boilerplateFunctionPrompt: str,
                 structFinderPrompt: str
                 ) -> str:
        output = ""
        for cs in self.__cppCodeSnippetExtractor.getAllCodeSnippets():
            if isinstance(cs, ChunkCodeSnippet):
                className = cs.name

                if className != "IRtcEngine":
                    continue
                print("\n----------------\n")
                print(f"Processing class {className}")
                print(f"\n")

                newWrapperTemplate = wrapperTemplate.replace("{{ CLASS_NAME }}", className).replace(
                    "{{ CLASS_NAME_LOWERCASE }}", className.lower())
                functions: List[str] = []
                for ccs in cs.codeSnippets:

                    prompt = boilerplateFunctionPrompt
                    # prompt = structFinderPrompt

                    parameterTypes = self.__cppCodeSnippetExtractor.findAllParameterTypesFromCodeSnippet(
                        ccs.source)

                    structCSList = self.__cppCodeSnippetExtractor.getStructCodeSnippetsOfTypeNames(
                        parameterTypes)

                    fieldTypeCSList: List[CodeSnippet] = []
                    for scs in structCSList:
                        t = self.__cppCodeSnippetExtractor.getFieldTypeCodeSnippetsFromStruct(
                            scs)
                        fieldTypeCSList.extend(
                            list(filter(lambda x: x.type == CodeSnippetType.struct_t, t)))

                    structCSList.extend(fieldTypeCSList)

                    content = "\n".join(
                        list(map(lambda cs: cs.source, structCSList))) + "\r\n\n" + ccs.source
                    messages: List[dict] = []

                    y = yaml.load_all(boilerplateFunctionPrompt)
                    for d in y:
                        for dd in d:
                            messages.append(dd)

                    messages.append({"role": "user", "content": content})

                    print(f"Processing code snippet:\n{content}")
                    print(f"######\n")

                    messages = [
                        {
                            "role": "system",
                            "content": prompt,
                        },
                        {"role": "user", "content": content},
                    ]
                    # call the OpenAI chat completion API with the given messages
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0
                    )

                    choices = response["choices"]  # type: ignore
                    completion = choices[0].message.content.strip()

                    print(completion)
                    print(f"\n######\n\n")
                    functions.append(completion)

                # output = newWrapperTemplate.replace("{{ FUNCTIONS }}", "\n".join(functions))

                break

        return output
