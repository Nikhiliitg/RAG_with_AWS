from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from config import Config
import os
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

class LLMService:
    def __init__(self, vector_store):
        self.llm = ChatGroq(model="gemma2-9b-it", api_key=groq_api_key)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=vector_store.as_retriever(),  # ✅ Fixed
            memory=self.memory
        )

    def get_response(self, query):
        try:
            response = self.chain.invoke({"question": query})  # ✅ Use `.invoke()` instead of calling it like a dict
            return response['answer']
        except Exception as e:
            print(f"Error getting LLM response: {e}")
            return "I encountered an error processing your request."
