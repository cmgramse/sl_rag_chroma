from langchain.llms import OpenAI
from langchain.chains import RetrievalQAChain
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.graphs import Neo4jGraph
from langchain.chains import GraphQAChain
import os

class RAGQueryEngine:
    def __init__(self):
        self.llm = OpenAI(temperature=0)
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(embedding_function=self.embeddings)
        self.neo4j_graph = Neo4jGraph(
            url=os.getenv('NEO4J_URI'),
            username=os.getenv('NEO4J_USERNAME'),
            password=os.getenv('NEO4J_PASSWORD')
        )

    def query(self, query, user):
        # Retrieve from vector store
        retriever = self.vectorstore.as_retriever()
        vector_chain = RetrievalQAChain.from_llm(self.llm, retriever=retriever)
        vector_result = vector_chain.run(query)

        # Retrieve from graph database
        graph_chain = GraphQAChain.from_llm(self.llm, graph=self.neo4j_graph)
        graph_result = graph_chain.run(query)

        # Combine results (you might want to implement a more sophisticated combination strategy)
        combined_result = f"Vector Store: {vector_result}\n\nGraph Database: {graph_result}"
        return combined_result