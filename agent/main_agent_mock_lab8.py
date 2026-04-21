import asyncio
import os
import random
from typing import List, Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv
from engine.index_v2 import LabIndexer

load_dotenv(override=True)

class MockAgent:
    """
    Agent Mock thực hiện Retrieval kém hơn để so sánh Benchmark.
    """
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.name = "MockAgent-Weak-v1"
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.indexer = LabIndexer()
        self.model_name = model_name

    async def query(self, question: str, expected_answer: str = "") -> Dict:
        """
        Quy trình RAG Mock (Cố tình làm tệ):
        1. Retrieval: Chỉ lấy 1 chunk duy nhất (thay vì 3) và có xác suất lấy sai chunk.
        2. Generation: Prompt hời hợt, không ép tuân thủ tài liệu.
        """
        # 1. Retrieval (Mock tệ)
        try:
            # Chỉ lấy n_results=1 để giảm Hit Rate và MRR
            search_results = self.indexer.search(question, n_results=1)
            
            retrieved_ids = search_results.get("ids", [[]])[0]
            retrieved_texts = search_results.get("documents", [[]])[0]
            
            # Cố tình giả lập lỗi retrieval: 30% xác suất trả về một chunk ngẫu nhiên hoàn toàn
            if random.random() < 0.3:
                all_chunks = self.indexer.get_all_chunks()
                random_chunk = random.choice(all_chunks)
                retrieved_ids = [random_chunk["id"]]
                retrieved_texts = [random_chunk["text"]]
                
        except Exception as e:
            print(f"❌ Lỗi Retrieval: {e}")
            retrieved_ids = []
            retrieved_texts = []

        # 2. Generation (Mock hời hợt)
        context_str = "\n---\n".join(retrieved_texts)
        prompt = f"""
        Chào, bạn hãy trả lời câu hỏi sau dựa trên cảm nhận của bạn. 
        Nếu có tài liệu thì xem qua cũng được:
        
        Tài liệu: {context_str}
        
        Câu hỏi: {question}
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a casual assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0 # Tăng randomness để dễ sai hơn
            )
            answer = response.choices[0].message.content
        except Exception as e:
            print(f"❌ Lỗi Generation: {e}")
            answer = "Tôi không biết."

        return {
            "answer": answer,
            "contexts": retrieved_texts,
            "metadata": {
                "model": self.model_name,
                "retrieved_ids": retrieved_ids,
                "type": "mock_weak"
            }
        }

if __name__ == "__main__":
    async def test():
        agent = MockAgent()
        resp = await agent.query("Chế độ bảo hành là gì?")
        print(f"Mock Answer: {resp['answer']}")
        print(f"Retrieved IDs: {resp['metadata']['retrieved_ids']}")
        
    asyncio.run(test())
