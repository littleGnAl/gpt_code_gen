
import re
from enum import Enum
from typing import List, Set

from src.code_snippet_extractor import (
    ChunkCodeSnippet,
    CodeSnippet,
    CodeSnippetExtractor,
    CodeSnippetFile)


class CXXCodeSnippetType(str, Enum):
    class_t = "class"
    struct_t = "struct"
    enum_t = "enum"


class CXXCodeSnippetExtractor(CodeSnippetExtractor):

    def __flatten_code_snippets(self, cxx_files: List[CodeSnippetFile]) -> List[CodeSnippet]:
        return sum(map(lambda x: x.code_snippets, cxx_files), [])

    def __remove_comments(self, file_in_str: str) -> str:
        comment_pattern = r"\/\/.*|\/\*(?:.|[\n])*?\*\/"
        # Remove all single-line and multi-line comments using the regular expression pattern
        cleaned_str = re.sub(comment_pattern, "", file_in_str)
        return cleaned_str

    def __chunk_code_snippets(self, originCodeSnippet: CodeSnippet) -> ChunkCodeSnippet:
        function_pattern = r"(?:[\w]*\s)?[\w\<\>\*]+\s[\w_]+\([^()]*\)\s=\s0\;"

        chunk_code_snippet = ChunkCodeSnippet()
        chunk_code_snippet.type = originCodeSnippet.type
        chunk_code_snippet.name = originCodeSnippet.name
        chunk_code_snippet.source = originCodeSnippet.source
        chunk_code_snippet.start = originCodeSnippet.start
        chunk_code_snippet.end = originCodeSnippet.end
        chunk_code_snippet.code_snippets = []

        code_snippets: List[str] = []
        cbs = chunk_code_snippet.source.split("\n")

        i = 0
        while (i < len(cbs)):
            if cbs[i].startswith("#if"):
                macro_suround = []
                macro_suround.append(cbs[i])

                macro_stack = []
                macro_stack.append(cbs[i])
                j = i + 1
                while (j < len(cbs)):
                    macro_suround.append(cbs[j])
                    if cbs[j].strip() == "#endif":
                        macro_stack.pop()
                    elif cbs[j].startswith("#"):
                        macro_stack.append(cbs[j])

                    if len(macro_stack) == 0:
                        break

                    j += 1

                i = j + 1

                code_snippets.append("\n".join(macro_suround))
                continue

            m = i
            while (m < len(cbs)):
                if cbs[m].startswith("#if"):
                    break
                m += 1

            # Found a macro block
            if m > i and m < len(cbs):
                code_snippets.append("\n".join(cbs[i:m - 1]))
                i = m
            else:
                code_snippets.append("\n".join(cbs[i:m]))
                i = m + 1

        for cs in code_snippets:
            if "#if" not in cs:
                function_blocks: List[str] = []
                csl = cs.split("\n")
                j = 0
                while (j < len(csl)):
                    str_to_match = "\n".join(csl[j:])

                    if fm := re.search(function_pattern, str_to_match, re.MULTILINE):
                        matched_str = str_to_match[fm.start():fm.end()]
                        offset_line_count = str_to_match[0:fm.end()].count(
                            "\n") + 1

                        function_blocks.append(matched_str)

                        j = j + offset_line_count + 1
                        continue

                    j += 1

                for fb in function_blocks:
                    code_snippet = CodeSnippet()
                    code_snippet.source = fb
                    chunk_code_snippet.code_snippets.append(code_snippet)

            else:
                code_snippet = CodeSnippet()
                code_snippet.source = cs
                chunk_code_snippet.code_snippets.append(code_snippet)

        return chunk_code_snippet

    def __fill_relative_code_snippets(
            self,
            code_snippets: List[CodeSnippet],
            cxx_files: List[CodeSnippetFile]) -> List[CodeSnippet]:
        output: List[CodeSnippet] = code_snippets
        for code_snippet in output:
            if code_snippet.type == CXXCodeSnippetType.struct_t:
                code_snippet.relative_code_snippets = self.__get_field_type_code_snippets_from_struct(
                    code_snippet, cxx_files)
            elif isinstance(code_snippet, ChunkCodeSnippet):
                for ccs in code_snippet.code_snippets:
                    parameter_types = self.__find_all_parameter_types_from_code_snippet(
                        ccs.source)
                    ccs.relative_code_snippets = self.__get_code_snippets_of_type_names(
                        parameter_types, cxx_files)

        return output

    def __extract_code_snippets(self, file_path: str) -> CodeSnippetFile:
        print(f'Extract code snippets for file: {file_path}')
        file_in_str: str
        with open(file_path) as f:
            file_in_str = f.read()

        vague_code_block_pattern = r"^(class|enum|struct)\s+(\w+)\s*(:?\s*(public)+\s+[\w\:\<\>]*)?\s*\{"

        vague_blocks: List[CodeSnippet] = []

        cleaned_str = self.__remove_comments(file_in_str)

        input_str = cleaned_str.split("\n")

        for index, line in enumerate(input_str):
            match = re.search(vague_code_block_pattern, line)
            if match:
                cb: CodeSnippet = CodeSnippet()
                cb.type = CXXCodeSnippetType(match.group(1))
                cb.name = match.group(2)

                cb.start = index
                for i, v in enumerate(input_str[index:]):
                    if v == "};":
                        cb.end = i + index + 1

                        break

                cb.source = "\n".join(input_str[cb.start:cb.end])
                vague_blocks.append(cb)

        final_code_snippets: List[CodeSnippet] = []
        for block in vague_blocks:
            if block.type != CXXCodeSnippetType.class_t:
                final_code_snippets.append(block)
                continue

            final_code_snippets.append(self.__chunk_code_snippets(block))

        for cs in final_code_snippets:
            if cs.type == CXXCodeSnippetType.struct_t:
                trim_code_snippet = cs.source
                trim_code_snippet = self.__trim_constructor_block(
                    trim_code_snippet, cs.name)
                trim_code_snippet = self.__trim_functions_block(
                    trim_code_snippet)
                trim_code_snippet = self.__reformat(trim_code_snippet)

                cs.source = trim_code_snippet

            cs.source = self.__reformat(cs.source)

        cxx_file: CodeSnippetFile = CodeSnippetFile()
        cxx_file.file_path = file_path
        cxx_file.code_snippets = final_code_snippets

        return cxx_file

    def __find_all_parameter_types_from_code_snippet(self, code_snippet: str) -> Set[str]:
        parameter_list_pattern = r"\([^()]*\)"
        parameter_list_matches = re.finditer(
            parameter_list_pattern, code_snippet, re.MULTILINE)
        parameter_list: List[str] = []
        for m in parameter_list_matches:
            pl = code_snippet[m.start():m.end()]
            parameter_list.append(pl)

        parameter_types: Set[str] = set()
        for pl in parameter_list:
            for m in pl.strip("(").strip(")").split(","):
                # The macro, e.g., (__APPLE__)
                if m.startswith("_"):
                    continue
                # const int* out = nullptr
                pt = m.split("=")[0].replace("const", "").strip().split(" ")[0].replace(
                    "&", "").replace("*", "").strip()
                parameter_types.add(pt)

        return parameter_types

    def __get_code_snippets_of_type_names(
            self, type_names: List[str], cxx_files: List[CodeSnippetFile]) -> List[CodeSnippet]:
        code_snippets: List[CodeSnippet] = []

        for type_name in type_names:
            for code_snippet in self.__flatten_code_snippets(cxx_files):
                # Filter the `CXXCodeSnippetType.class_t` by default to avoid the exceed the max tokens length,
                # maybe we can calculate the tokens num here to determine whether we should include the `CXXCodeSnippetType.class_t`
                if code_snippet.name == type_name and code_snippet.type != CXXCodeSnippetType.class_t:
                    code_snippets.append(code_snippet)
                    break

        return code_snippets

    def __get_field_type_code_snippets_from_struct(
            self,
            structCodeSnippet: CodeSnippet,
            cxxFiles: List[CodeSnippetFile]) -> List[CodeSnippet]:
        field_pattern = r'\b((?:(const\s)|(\w+\s?))?\:*\<?\w+\>?)(?=\*?\s+\w+;)'
        findall_field_types: List[str] = list(
            map(lambda f: f[0], re.findall(field_pattern, structCodeSnippet.source)))
        field_types: Set[str] = set()
        for fft in findall_field_types:
            ft = fft.replace("const", "").strip().replace(
                "Optional<", "").replace(">", "")
            if "::" in ft:
                sft = ft.split("::")
                ft = sft[len(sft) - 1]

            field_types.add(ft)

        out = list(filter(lambda cs: cs.name in field_types,
                   self.__flatten_code_snippets(cxxFiles)))

        return out

    def __trim_constructor_block(self, code_snippet: str, struct_name: str) -> str:
        constructor_block_pattern = r'\~?' + struct_name + \
            r'\([^\(\)]*\)\s*\n*(?:(\:?\s*[^\{\}]*\{\})|(\=\s*[a-z]+;))'
        return re.sub(constructor_block_pattern, "", code_snippet, re.DOTALL | re.MULTILINE)

    def __trim_functions_block(self, code_snippet: str) -> str:
        new_code_snippet_in_lines = []
        function_start_pattern = r'[a-zA-Z0-9_&~]+\s*[a-zA-Z0-9_]+\S*\([^\(\)]*\)(.*)\{'
        code_snippet_in_lines = code_snippet.split("\n")
        index = 0
        while (index < len(code_snippet_in_lines)):
            line = code_snippet_in_lines[index]
            match = re.search(function_start_pattern, line)
            if match:
                function_end_stack = []
                function_end_index = index + 1
                while (function_end_index < len(code_snippet_in_lines)):
                    next_line = code_snippet_in_lines[function_end_index]
                    if next_line.strip().endswith("}") or (next_line.strip().startswith("}") and next_line.strip() != "};"):
                        if len(function_end_stack) > 0:
                            function_end_stack.pop()
                        else:
                            break

                    if next_line.strip().endswith("{"):
                        function_end_stack.append("{")

                    function_end_index += 1

                index = function_end_index + 1
            else:
                new_code_snippet_in_lines.append(line)
                index += 1

        return ("\n").join(new_code_snippet_in_lines)

    def __reformat(self, code_snippet: str) -> str:
        return "\n".join(filter(lambda f: f.strip() != "", code_snippet.split("\n")))

    def extract(self, file_paths: List[str]) -> List[CodeSnippetFile]:
        cxx_files: List[CodeSnippetFile] = []
        for fp in file_paths:
            cxx_file = self.__extract_code_snippets(fp)
            cxx_files.append(cxx_file)

        for cxx_file in cxx_files:
            cxx_file.code_snippets = self.__fill_relative_code_snippets(
                cxx_file.code_snippets, cxx_files)

        return cxx_files
