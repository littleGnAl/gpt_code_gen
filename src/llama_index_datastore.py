

from typing import List
from langchain import OpenAI
from llama_index import GPTSimpleVectorIndex, LLMPredictor, PromptHelper, QueryMode, ServiceContext, SimpleDirectoryReader

from src.cpp_code_snippet_extractor import CPPCodeSnippetExtractor, CodeSnippet, CodeSnippetType
from llama_index.data_structs.node_v2 import Node, DocumentRelationship


class LlamaIndexDataStore:
    __gptSimpleVectorIndex: GPTSimpleVectorIndex

    __cppCodeSnippetExtractor: CPPCodeSnippetExtractor
    
    def __init__(self, cppCodeSnippetExtractor: CPPCodeSnippetExtractor) -> None:
        self.__cppCodeSnippetExtractor = cppCodeSnippetExtractor
        self.__gptSimpleVectorIndex = None
    

    def loadData(self, dataDir: str):
        documents = SimpleDirectoryReader(dataDir).load_data()
               # define LLM
        # llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003"))

        # # define prompt helper
        # # set maximum input size
        # max_input_size = 4096
        # # set number of output tokens
        # num_output = 10000
        # # set maximum chunk overlap
        # max_chunk_overlap = 20
        # prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)

        # service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)

        self.__gptSimpleVectorIndex = GPTSimpleVectorIndex.from_documents(
            documents)
        
    def query(self, queryStr: str):
        q = self.__gptSimpleVectorIndex.query(queryStr)
        print('response: \n')
        print(q)
        
    def indexCodeSnippets(self, codeSnippets: List[CodeSnippet]):
        nextDocId = 1
        previousNode: Node = None
        nodes: List[Node] = []
        
        for codeSnippet in codeSnippets:
            node = Node(text=codeSnippet.source, doc_id=str(nextDocId))
            nodes.append(node)
            
            if previousNode is not None:
                previousNode.relationships[DocumentRelationship.NEXT] = node.get_doc_id()
                node.relationships[DocumentRelationship.PREVIOUS] = previousNode.get_doc_id()
                
            previousNode = node
            nextDocId += 1
            
        # define LLM
        llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-davinci-003"))

        # define prompt helper
        # set maximum input size
        max_input_size = 4096
        # set number of output tokens
        num_output = 10000
        # set maximum chunk overlap
        max_chunk_overlap = 20
        prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)

        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)

        self.__gptSimpleVectorIndex = GPTSimpleVectorIndex(nodes=nodes, service_context=service_context)

