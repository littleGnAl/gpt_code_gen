
from typing import List, Tuple, Optional
import re
from enum import Enum
from pydantic import BaseModel
from pydantic.dataclasses import dataclass

import openai

class CodeSnippetType(str, Enum):
    class_t = "class"
    struct_t = "struct"
    enum_t = "enum"
    
class CodeSnippet(BaseModel):
    type: CodeSnippetType = None
    name: str = None
    source: str = ""
    start: int = 0
    end: int = 0
    
class ChunkCodeSnippet(CodeSnippet):
    codeSnippets: List[CodeSnippet] = None


# class CPPCodeBlock:
#     start: int
#     end: int
#     codeBlocks: str

#     def __init__(self):
#         self.start = 0
#         self.end = 0
#         self.codeBlocks = ""


class CPPCodeExtractor:
    def __extractClassBlock(fileInLines: List[str]) -> List[str]:
        out = []
        classStartPattern = r"class\s+\w+\s*(:?\s*(public)+\s+[\w\:\<\>]*)?\s*\{"

        matches = re.finditer(classStartPattern, fileInLines, re.MULTILINE)

        for match in matches:
            start_line = content[:match.start()].count("\n") + 1
            end_line = content[:match.end()].count("\n") + 1
            print(
                f"Class declaration found from line {start_line} to line {end_line}:")
            print(match.group(0))
            print("")

        for line in fileInLines:
            match = re.search(classStartPattern, line)
            if match:
                print(f"Class declaration found at line {i+1}:")
                print(line)
                print("")

        return []

    def __extractStructBlock(fileInLines: List[str]) -> str:
        return ""

    def __extractEnumBlock(fileInLines: List[str]) -> str:
        return ""

    def __removeComments(fileInLines: List[str]) -> str:
        return ""

    def extractCodeBlocks(self, fileInStr: str) -> List[CodeSnippet]:
        # Define the regular expression patterns for class, enum, and struct
        class_pattern = r"class\s+\w+\s*(:?\s*(public)+\s+[\w\:\<\>]*)?\s*\{[\s\S]*\};"
        enum_pattern = r"enum\s+\w+\s*\{[^{}]*\};"
        struct_pattern = r"struct\s+\w+\s*\{[^{}]*\};"
        
        class_name_pattern = "class ([a-zA-Z0-9_\<\>]+)"
        struct_name_pattern = "struct ([a-zA-Z0-9_\<\>]+)"
        enum_name_pattern = "enum ([a-zA-Z0-9_\<\>]+)"

        vagueCodeBlockPattern = r"^(class|enum|struct)\s+(\w+)\s*(:?\s*(public)+\s+[\w\:\<\>]*)?\s*\{"
        classCodeBlockPattern = r"^class\s+\w+\s*(:?\s*(public)+\s+[\w\:\<\>]*)?\s*\{"
        
        function_pattern = r"[^\S\n\t]+[a-z]+\s[a-zA-Z\<\>\s\*]+\s[a-zA-Z0-9_]+\([^()]*\)\s=\s0\;$"

        vagueBlocks: List[CodeSnippet] = []

        comment_pattern = r"\/\/.*|\/\*(?:.|[\n])*?\*\/"
        # Remove all single-line and multi-line comments using the regular expression pattern
        cleaned_str = re.sub(comment_pattern, "", fileInStr)

        input_str = cleaned_str.split("\n")
        
        # f = open("log.txt", "w")

        for index, line in enumerate(input_str):
            match = re.search(vagueCodeBlockPattern, line)
            if match:
                cb: CodeSnippet = CodeSnippet()
                cb.type = CodeSnippetType(match.group(1))
                cb.name = match.group(2)
                
                # start_line = cleaned_str[:match.start()].count("\n") + 1
                cb.start = index
                for i, v in enumerate(input_str[index:]):
                    if v == "};":
                        cb.end = i + index + 1

                        break

                cb.source = "\n".join(input_str[cb.start:cb.end])
                vagueBlocks.append(cb)
        
        finalCodeSnippets: List[CodeSnippet] = []
        f = open("log.txt", "w")
        for block in vagueBlocks:
            if block.type != CodeSnippetType.class_t:
                finalCodeSnippets.append(block)
                continue
            
            chunkCodeSnippet = ChunkCodeSnippet()
            finalCodeSnippets.append(chunkCodeSnippet)
            
            chunkCodeSnippet.type = block.type
            chunkCodeSnippet.name = block.name
            chunkCodeSnippet.source = block.source
            chunkCodeSnippet.start = block.start
            chunkCodeSnippet.end = block.end
            chunkCodeSnippet.codeSnippets = []
            
            
            codeSnippets: List[str] = []
            cbs=chunkCodeSnippet.source.split("\n")

            i = 0
            
            while(i < len(cbs)):
                if cbs[i].startswith("#if"):
                    # codeSnippet = CodeSnippet()
                    # codeSnippet.start = i
                    
                    macroSuround = []
                    macroSuround.append(cbs[i])

                    macroStack=[]
                    macroStack.append(cbs[i])
                    j = i + 1
                    while(j < len(cbs)):
                        macroSuround.append(cbs[j])
                        if cbs[j].strip() == "#endif":
                            macroStack.pop()
                        elif cbs[j].startswith("#"):
                            macroStack.append(cbs[j])
                            
                        if len(macroStack) == 0:
                            break
                        
                        j += 1
                        
                    i = j + 1
                    
                    # codeSnippet.end = j
                    # codeSnippet.source = "\n".join(macroSuround)
                    
                    # chunkCodeSnippet.codeSnippets.append(codeSnippet)
                    
                    codeSnippets.append("\n".join(macroSuround))
                    continue
                
                m = i
                while (m < len(cbs)):
                    if cbs[m].startswith("#if"):
                        break
                    m += 1
                        
                # Finded a macro block
                if m > i and m < len(cbs):
                    codeSnippets.append("\n".join(cbs[i:m - 1]))
                    i = m
                else:
                    codeSnippets.append("\n".join(cbs[i:m]))
                    i = m + 1
                
            
            for cs in codeSnippets:
                if "#if" not in cs:
                    functionBlocks: List[str] = []
                    csl = cs.split("\n")
                    j = 0
                    while (j < len(csl)):
                        strToMatch = "\n".join(csl[j:])
                        
                        if fm:=re.search(function_pattern, strToMatch, re.MULTILINE):
                            matchedStr = strToMatch[fm.start():fm.end()]
                            lineCount = matchedStr.count("\n") + 1
                            offsetLineCount = strToMatch[0:fm.end()].count("\n") + 1
                            
                            f.write(matchedStr)
                            f.write("\n---------\n\n")
                            
                            functionBlocks.append(matchedStr)

                            j = j + offsetLineCount + 1
                            continue
                        
                        j += 1
                        
                    for fb in functionBlocks:
                        codeSnippet = CodeSnippet()
                        codeSnippet.source = fb
                        chunkCodeSnippet.codeSnippets.append(codeSnippet)
                    
                        f.write(fb)
                        f.write("\n-----\n\n")
                else:
                    codeSnippet = CodeSnippet()
                    codeSnippet.source = cs
                    chunkCodeSnippet.codeSnippets.append(codeSnippet)
                    f.write(cs)
                    f.write("\n-----\n\n")
 
        f.close()

        return finalCodeSnippets

    def extractCodes(self, fileInStr: str) -> str:
        comment_pattern = r"\/\/.*|\/\*(?:.|[\n])*?\*\/"
        # Remove all single-line and multi-line comments using the regular expression pattern
        cleaned_str = re.sub(comment_pattern, "", fileInStr)
        f = open("log.txt", "w")
        f.write(cleaned_str)
        f.write("---------\n\n")
        f.close()

        return cleaned_str
