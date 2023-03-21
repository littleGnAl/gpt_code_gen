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

        vagueBlocks: List[CPPCodeBlock] = []

        comment_pattern = r"\/\/.*|\/\*(?:.|[\n])*?\*\/"
        # Remove all single-line and multi-line comments using the regular expression pattern
        cleaned_str = re.sub(comment_pattern, "", fileInStr)

        input_str = cleaned_str.split("\n")

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

        # for block in vagueBlocks:
        #     codeBlocks = block.codeBlocks.split("\n")
        #     for i, v in enumerate(codeBlocks):
        #         if v != "}" or v != "};":
        #             block.start = block.start + i
        #             break

        #     for i, v in enumerate(reversed(codeBlocks)):
        #         if v == "#if" or v == "};":
        #             block.end = block.end - i + 3
        #             break

        #     block.codeBlocks = "\n".join(input_str[block.start:block.end])

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

        for cb in vagueBlocks:
            prompt = "There're some unexpected line from my c++ code, plese help remove it\n"
            prompt += "- The c++ code should be begin with keywords like: class, struct, enum, and should be end with \"};\"\n"
            prompt += "- You should not generate other codes, just remove the unexpected line from the code\n"
            prompt += "- Do not introduce any other new codes base on my codes\n"
            prompt += "- If you can't remove it, just reply \"I don't know how to do\"\n"
            prompt += "- Here a example, there an invalid \"};\" at the begining of the code:\n"
            prompt += ""
            prompt += """
};


enum AUDIO_MIXING_STATE_TYPE {
 
  AUDIO_MIXING_STATE_PLAYING = 710,
  
  AUDIO_MIXING_STATE_PAUSED = 711,
  
  AUDIO_MIXING_STATE_STOPPED = 713,
  
  AUDIO_MIXING_STATE_FAILED = 714,
};

            
"""
            prompt += """
The output should be:
enum AUDIO_MIXING_STATE_TYPE {
 
  AUDIO_MIXING_STATE_PLAYING = 710,
  
  AUDIO_MIXING_STATE_PAUSED = 711,
  
  AUDIO_MIXING_STATE_STOPPED = 713,
  
  AUDIO_MIXING_STATE_FAILED = 714,
};
"""
            prompt += "Ok, now you should help me fix the code below:\n"
            prompt += cb.codeBlocks

            # code_completion = openai.Completion.create(
            #     engine="text-davinci-002",
            #     prompt=prompt,
            #     max_tokens=1000
            # )
            # # print(code_completion.choices[0].text)
            # # cb.codeBlocks=code_completion['choices'][0]['text']
            # print(code_completion['choices'][0]['text'])

            # f.write("---------\n")
            # f.write(cb.codeBlocks)
            # f.write("\n")

        # f.write("---------\n\n")

        # f.close()

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
