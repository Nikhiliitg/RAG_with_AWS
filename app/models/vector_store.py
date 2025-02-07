# from langchain.embeddings.huggingface import HuggingFaceEmbeddings
# from langchain.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
class VectorStore:
    def __init__(self, path):
        """Initialize ChromaDB with HuggingFace embeddings."""
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        self.vector_store = Chroma(
            persist_directory=path,
            embedding_function=self.embeddings
        )

    def add_documents(self, documents):
        """Add documents to ChromaDB with proper formatting."""
        formatted_docs = [
            {"page_content": doc.page_content, "metadata": doc.metadata} for doc in documents
        ]
        self.vector_store.add_documents(formatted_docs)
        self.vector_store.persist()  # Ensure data is saved

    def similarity_search(self, query, k=4):
        """Search for similar documents and return JSON-friendly output."""
        results = self.vector_store.similarity_search(query, k=k)
        return [{"content": doc.page_content, "metadata": doc.metadata} for doc in results]

    def persist(self):
        """Persist changes to disk."""
        self.vector_store.persist()

