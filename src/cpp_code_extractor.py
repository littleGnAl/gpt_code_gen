from typing import List, Tuple
import re

class CPPCodeExtractor:
    def __extractClassBlock(fileInLines: List[str]) -> List[str]:
        out = []
        classStartPattern = r"class\s+\w+\s*(:?\s*(public)+\s+[\w\:\<\>]*)?\s*\{"
        
        matches = re.finditer(classStartPattern, fileInLines, re.MULTILINE)

        for match in matches:
            start_line = content[:match.start()].count("\n") + 1
            end_line = content[:match.end()].count("\n") + 1
            print(f"Class declaration found from line {start_line} to line {end_line}:")
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
    
    def extractCodeBlocks(self, fileInStr: str):
        # Define the regular expression patterns for class, enum, and struct
        class_pattern = r"class\s+\w+\s*(:?\s*(public)+\s+[\w\:\<\>]*)?\s*\{[\s\S]*\};"
        enum_pattern = r"enum\s+\w+\s*\{[^{}]*\};"
        struct_pattern = r"struct\s+\w+\s*\{[^{}]*\};"
        
        input_str = fileInStr

        # Define the input file name
        # file_name = "example.cpp"

        # # Read the input file
        # with open(file_name, "r") as f:
        #     input_str = f.read()

        # Find all matches of the regular expression patterns
        class_matches = re.finditer(class_pattern, input_str)
        enum_matches = re.finditer(enum_pattern, input_str)
        struct_matches = re.finditer(struct_pattern, input_str)

        # Extract the matched code blocks
        class_blocks = [match.group() for match in class_matches]
        enum_blocks = [match.group() for match in enum_matches]
        struct_blocks = [match.group() for match in struct_matches]

        f = open("log.txt", "w")
        # Print the extracted code blocks
        # print("Class blocks:")
        # print(class_blocks)
        f.write(str("Class blocks:\n"))
        f.write("\n".join(class_blocks))
        f.write("---------\n\n")
        f.write("\nEnum blocks:\n")
        f.write("\n".join(enum_blocks))
        f.write("---------\n\n")
        f.write("\nStruct blocks:\n")
        f.write("\n".join(struct_blocks))
        f.write("---------\n\n")

        
        
        f.close()

    def extractCodes(self, fileInStr: str) -> str:
        comment_pattern = r"\/\/.*|\/\*(?:.|[\n])*?\*\/"
        # Remove all single-line and multi-line comments using the regular expression pattern
        cleaned_str = re.sub(comment_pattern, "", fileInStr)
        f = open("log.txt", "w")
        f.write(cleaned_str)
        f.write("---------\n\n")
        f.close()
        
        return cleaned_str
        
        