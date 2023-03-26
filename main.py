import os
import sys
import fs.osfs
from fs.base import FS
from fs.copy import copy_file

from src.cpp_code_extractor import CPPCodeExtractor
from src.openai_code_gen import OpenAICodeGen
from src.openai_embedding import OpenAIEmbedding


def main():
    fileSystem = fs.osfs.OSFS("/")
    root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(root)))

    cppExtractor = CPPCodeExtractor()
    openAIEmbedding = OpenAIEmbedding()
    openAICodeGen = OpenAICodeGen(fileSystem)

    exportFiles = [
        "/Users/littlegnal/codes/personal-project/gpt_code_gen/test_inputs/IAgoraRtcEngine.h"]

    for path in exportFiles:
        backupFilePath = path + ".backup"
        copy_file(fileSystem, path, fileSystem, backupFilePath)

        # with fileSystem.open(exportFiles[0], 'r') as file:
        fileInStr = fileSystem.readtext(backupFilePath)
        codeBlocks = cppExtractor.extractCodeBlocks(fileInStr)

        wrapperTemplate = fileSystem.readtext(
            "/Users/littlegnal/codes/personal-project/gpt_code_gen/promptions/wrapper_template.txt")
        boilerplateFunctionPrompt = fileSystem.readtext(
            "/Users/littlegnal/codes/personal-project/gpt_code_gen/promptions/boilerplate_function_prompt.md")
        structFinderPrompt = fileSystem.readtext(
            "/Users/littlegnal/codes/personal-project/gpt_code_gen/promptions/struct_finder_prompt.md")
        output = openAICodeGen.generate(
            codeBlocks, wrapperTemplate, boilerplateFunctionPrompt, structFinderPrompt)
        print("\n--------\n")
        print(output)
        # openAIEmbedding.embeddingCodeBlocks(codeBlocks)

        # backupFile = fileSystem.open(backupFilePath, mode="w")
        # backupFile.write(newFileContent)
        # backupFile.flush()
        # backupFile.close()

        # openAIEmbedding.searchCodes(newFileContent, "IRtcEngine")

        # openAIEmbedding.searchCodeBlocks(codeBlocks, "class IRtcEngine ")

        # average_embedding_vector = openAIEmbedding.len_safe_get_embedding(newFileContent, average=True)
        # print(average_embedding_vector)
        # chunks_embedding_vectors = openAIEmbedding.len_safe_get_embedding(newFileContent, average=False)

        # print(f"Setting average=True gives us a single {len(average_embedding_vector)}-dimensional embedding vector for our long text.")
        # print(f"Setting average=False gives us {len(chunks_embedding_vectors)} embedding vectors, one for each of the chunks.")

        # copy_file(fileSystem, backupFilePath, fileSystem, path)

        # fileSystem.remove(backupFilePath)

    # openAIEmbedding.searchCodes("class IRtcEngine")

    return 0


if __name__ == '__main__':
    main()
