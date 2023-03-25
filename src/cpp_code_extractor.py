from typing import List, Tuple
import re

import openai


class CPPCodeBlock:
    start: int
    end: int
    codeBlocks: str

    def __init__(self):
        self.start = 0
        self.end = 0
        self.codeBlocks = ""


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

    def extractCodeBlocks(self, fileInStr: str) -> List[CPPCodeBlock]:
        # Define the regular expression patterns for class, enum, and struct
        class_pattern = r"class\s+\w+\s*(:?\s*(public)+\s+[\w\:\<\>]*)?\s*\{[\s\S]*\};"
        enum_pattern = r"enum\s+\w+\s*\{[^{}]*\};"
        struct_pattern = r"struct\s+\w+\s*\{[^{}]*\};"

        vagueCodeBlockPattern = r"^(class|enum|struct)\s+\w+\s*(:?\s*(public)+\s+[\w\:\<\>]*)?\s*\{"
        classCodeBlockPattern = r"^class\s+\w+\s*(:?\s*(public)+\s+[\w\:\<\>]*)?\s*\{"
        
        function_pattern = r"[^\S\n\t]+[a-z]+\s[a-zA-Z\<\>\s\*]+\s[a-zA-Z0-9_]+\([^()]*\)\s=\s0\;$"

        vagueBlocks: List[CPPCodeBlock] = []

        comment_pattern = r"\/\/.*|\/\*(?:.|[\n])*?\*\/"
        # Remove all single-line and multi-line comments using the regular expression pattern
        cleaned_str = re.sub(comment_pattern, "", fileInStr)

        input_str = cleaned_str.split("\n")
        
        # f = open("log.txt", "w")

        for index, line in enumerate(input_str):
            match = re.search(vagueCodeBlockPattern, line)
            if match:
                cb: CPPCodeBlock = CPPCodeBlock()
                # start_line = cleaned_str[:match.start()].count("\n") + 1
                cb.start = index
                for i, v in enumerate(input_str[index:]):
                    if v == "};":
                        cb.end = i + index + 1

                        break

                cb.codeBlocks = "\n".join(input_str[cb.start:cb.end])
                vagueBlocks.append(cb)
                
                
                
                # if classMatch:=re.search(classCodeBlockPattern, line):
                #     cbs=cb.codeBlocks.split("\n")
                #     functionBlocks = []
                #     i = 0
                #     while(i < len(cbs)):
                #         m = i
                #         while (m < len(cbs)):
                #             if cbs[m].startswith("#if"):
                #                 break
                #             m += 1
                            
                #         # Handle the macro block
                #         if m > i and m < len(cbs):
                #             nonMacroStr = cbs[i:m]
                #             nonMacroBlocks = []
                #             j = i
                #             while (j < len(nonMacroStr)):
                #                 strToMatch = "\n".join(nonMacroStr[j:])
                                
                #                 if fm:=re.search(function_pattern, strToMatch, re.MULTILINE):
                #                     matchedStr = strToMatch[fm.start():fm.end()]
                #                     lineCount = matchedStr.count("\n") + 1
                #                     offsetLineCount = strToMatch[0:fm.end()].count("\n") + 1
                                    
                #                     f.write(matchedStr)
                #                     f.write("\n---------\n\n")
                                    
                #                     functionBlocks.append(matchedStr)

                #                     j = j + offsetLineCount + 1
                #                     continue
                                
                #                 j += 1
                #             i = m
                            
                        
                #         if cbs[i].startswith("#"):
                #             macroSuround = []
                #             macroSuround.append(cbs[i])

                #             macroStack=[]
                #             macroStack.append(cbs[i])
                #             j = i + 1
                #             while(j < len(cbs)):
                #                 macroSuround.append(cbs[j])
                #                 if cbs[j].strip() == "#endif":
                #                     macroStack.pop()
                #                 elif cbs[j].startswith("#"):
                #                     macroStack.append(cbs[j])
                                    
                #                 if len(macroStack) == 0:
                #                     break
                                
                #                 j += 1
                                
                #             i = j + 1
                #             functionBlocks.append("\n".join(macroSuround))

                #             f.write("\n".join(macroSuround))
                #             f.write("\n---------\n\n")
                #             continue

                #         else:
                #             j = i
                #             while (j < len(cbs)):
                #                 strToMatch = "\n".join(cbs[j:])
                                
                #                 if fm:=re.search(function_pattern, strToMatch, re.MULTILINE):
                #                     matchedStr = strToMatch[fm.start():fm.end()]
                #                     lineCount = matchedStr.count("\n") + 1
                #                     offsetLineCount = strToMatch[0:fm.end()].count("\n") + 1
                                    
                #                     f.write(matchedStr)
                #                     f.write("\n---------\n\n")
                                    
                #                     functionBlocks.append(matchedStr)

                #                     j = j + offsetLineCount + 1
                #                     continue
                                
                #                 j += 1
                                
                #             i = j + 1

        
        
        f = open("log.txt", "w")
        for block in vagueBlocks:
            if classMatch:=re.search(classCodeBlockPattern, block.codeBlocks):
                codeSnippets: List[str] = []
                cbs=block.codeBlocks.split("\n")

                i = 0
                
                while(i < len(cbs)):
                    if cbs[i].startswith("#if"):
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
                            f.write(fb)
                            f.write("\n-----\n\n")
                    else:
                        f.write(cs)
                        f.write("\n-----\n\n")





                
        f.close()
                    
                    
                    

        # matches = re.finditer(vagueCodeBlockPattern, cleaned_str)
        # for match in matches:
        #     cb: CPPCodeBlock = CPPCodeBlock()
        #     start_line = cleaned_str[:match.start()].count("\n") + 1
        #     cb.start = start_line
        #     for index, v in enumerate(input_str[start_line:]):
        #         if v.strip() == "};":
        #             cb.end = index

        #             break

        #     cb.codeBlocks = "\n".join(input_str[cb.start:cb.end + 5])
        #     vagueBlocks.append(cb)

        # Define the input file name
        # file_name = "example.cpp"

        # # Read the input file
        # with open(file_name, "r") as f:
        #     input_str = f.read()

        # Find all matches of the regular expression patterns
        # class_matches = re.finditer(class_pattern, input_str)
        # enum_matches = re.finditer(enum_pattern, input_str)
        # struct_matches = re.finditer(struct_pattern, input_str)

        # # Extract the matched code blocks
        # class_blocks = [match.group() for match in class_matches]
        # enum_blocks = [match.group() for match in enum_matches]
        # struct_blocks = [match.group() for match in struct_matches]

        # f = open("log.txt", "w")
        # Print the extracted code blocks
        # print("Class blocks:")
        # print(class_blocks)
        # f.write(str("Class blocks:\n"))
        # f.write("\n".join(class_blocks))
        # f.write("---------\n\n")
        # f.write("\nEnum blocks:\n")
        # f.write("\n".join(enum_blocks))
        # f.write("---------\n\n")
        # f.write("\nStruct blocks:\n")
        # f.write("\n".join(struct_blocks))

        return vagueBlocks

    def extractCodes(self, fileInStr: str) -> str:
        comment_pattern = r"\/\/.*|\/\*(?:.|[\n])*?\*\/"
        # Remove all single-line and multi-line comments using the regular expression pattern
        cleaned_str = re.sub(comment_pattern, "", fileInStr)
        f = open("log.txt", "w")
        f.write(cleaned_str)
        f.write("---------\n\n")
        f.close()

        return cleaned_str
