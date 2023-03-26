from typing import List
import fs.osfs
from fs.base import FS
import openai

from src.cpp_code_extractor import ChunkCodeSnippet, CodeSnippet, CodeSnippetType


class OpenAICodeGen:
    __fileSystem: FS

    def __init__(self, fileSystem: FS) -> None:
        self.__fileSystem = fileSystem
        


    def generate(self,
                 codeSnippets: List[CodeSnippet],
                 wrapperTemplate: str,
                 boilerplateFunctionPrompt: str,
                 structFinderPrompt: str
                 ) -> str:
        output = ""
        for cs in codeSnippets:
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
                    print(f"Processing code snippet:\n{ccs.source}")
                    print(f"######\n")
                    # prompt = boilerplateFunctionPrompt
                    prompt = structFinderPrompt
                    
                    messages = [
                        {
                            "role": "system",
                            "content": prompt,
                        },
                        {"role": "user", "content": ccs.source},
                    ]
                    # call the OpenAI chat completion API with the given messages
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0
                    )

                    choices = response["choices"]  # type: ignore
                    completion = choices[0].message.content.strip()
                    
                    # print(code_completion.choices[0].text)
                    # cb.codeBlocks=code_completion['choices'][0]['text']
                    # response = code_completion['choices'][0]['text']
                    
                    print(completion)
                    print(f"\n######\n\n")
                    functions.append(completion)
                
                # output = newWrapperTemplate.replace("{{ FUNCTIONS }}", "\n".join(functions))

                break

        return output
