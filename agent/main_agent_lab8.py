import asyncio
import os
from typing import List, Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv
from engine.index_v2 import LabIndexer

load_dotenv(override=True)

class MainAgent:
    """
    Agent RAG thực tế kết nối với ChromaDB và OpenAI GPT.
    """
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.name = "SupportAgent-v1"
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.indexer = LabIndexer()
        self.model_name = model_name

    async def query(self, question: str, expected_answer: str = "") -> Dict:
        """
        Quy trình RAG thực tế:
        1. Retrieval: Tìm kiếm chunk liên quan từ ChromaDB.
        2. Generation: Sử dụng context để sinh câu trả lời.
        """
        # 1. Retrieval
        try:
            search_results = self.indexer.search(question, n_results=3)
            
            retrieved_ids = search_results.get("ids", [[]])[0]
            retrieved_texts = search_results.get("documents", [[]])[0]
            retrieved_metadatas = search_results.get("metadatas", [[]])[0]
        except Exception as e:
            print(f"❌ Lỗi Retrieval: {e}")
            retrieved_ids = []
            retrieved_texts = []
            retrieved_metadatas = []

        # 2. Generation
        context_str = "\n---\n".join(retrieved_texts)
        prompt = f"""
        Bạn là một trợ lý hỗ trợ khách hàng chuyên nghiệp. 
        Dựa trên các đoạn trích dẫn tài liệu sau đây, hãy trả lời câu hỏi của khách hàng.
        Nếu tài liệu không chứa thông tin cần thiết, hãy nói rằng bạn không biết, đừng bịa đặt.

        Tài liệu:
        {context_str}

        Câu hỏi: {question}
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful customer support agent."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            answer = response.choices[0].message.content
        except Exception as e:
            print(f"❌ Lỗi Generation: {e}")
            answer = "Rất tiếc, đã có lỗi xảy ra khi xử lý câu trả lời của bạn."

        return {
            "answer": answer,
            "contexts": retrieved_texts,
            "metadata": {
                "model": self.model_name,
                "retrieved_ids": retrieved_ids,
                "retrieved_metadatas": retrieved_metadatas
            }
        }

if __name__ == "__main__":
    async def test():
        agent = MainAgent()
        resp = await agent.query("Chính sách hoàn tiền của công ty là gì?")
        print(f"Question: Chính sách hoàn tiền của công ty là gì?")
        print(f"Answer: {resp['answer']}")
        print(f"Retrieved IDs: {resp['metadata']['retrieved_ids']}")
        
    asyncio.run(test())
