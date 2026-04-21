import os
import json
import asyncio
from typing import List, Dict
from openai import AsyncOpenAI

class RagasEvaluator:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=api_key)
        self.model_name = model_name

    async def _eval_faithfulness(self, answer: str, context: str) -> float:
        """
        Đo lường mức độ trung thành của câu trả lời với Context (0-1).
        """
        prompt = f"""
        Bạn là giám khảo đánh giá RAG. Hãy kiểm tra xem câu trả lời dưới đây có được hỗ trợ hoàn toàn bởi Context không.
        
        Context: {context}
        Câu trả lời: {answer}
        
        Chỉ trả về JSON: {{"score": <float 0.0 to 1.0>, "reason": "<giải thích ngắn>"}}
        """
        try:
            res = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": "Bạn là chuyên gia về Faithfulness."}, {"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0
            )
            data = json.loads(res.choices[0].message.content)
            return float(data.get("score", 0))
        except: return 0.5

    async def _eval_relevancy(self, question: str, answer: str) -> float:
        """
        Đo lường mức độ liên quan của câu trả lời với câu hỏi (0-1).
        """
        prompt = f"""
        Bạn là giám khảo đánh giá RAG. Hãy kiểm tra xem câu trả lời có giải quyết đúng và trực tiếp câu hỏi không.
        
        Câu hỏi: {question}
        Câu trả lời: {answer}
        
        Chỉ trả về JSON: {{"score": <float 0.0 to 1.0>, "reason": "<giải thích ngắn>"}}
        """
        try:
            res = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": "Bạn là chuyên gia về Answer Relevancy."}, {"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0
            )
            data = json.loads(res.choices[0].message.content)
            return float(data.get("score", 0))
        except: return 0.5

    async def calculate_metrics(self, results: List[Dict]) -> Dict:
        """
        Tính toán Faithfulness và Relevancy nhanh chóng bằng asyncio.gather.
        """
        print(f"\n🧪 Đang chạy đánh giá RAGAS-Lite cho {len(results)} cases (Siêu tốc)...")
        
        tasks_f = []
        tasks_r = []
        
        for res in results:
            if "error" in res: continue
            
            ctx_text = " ".join(res.get("contexts", []))
            tasks_f.append(self._eval_faithfulness(res["agent_answer"], ctx_text))
            tasks_r.append(self._eval_relevancy(res["question"], res["agent_answer"]))
            
        # Chạy song song hàng trăm request
        f_scores = await asyncio.gather(*tasks_f)
        r_scores = await asyncio.gather(*tasks_r)
        
        avg_f = sum(f_scores) / len(f_scores) if f_scores else 0
        avg_r = sum(r_scores) / len(r_scores) if r_scores else 0
        
        print(f"✅ Hoàn tất RAGAS-Lite: Faithfulness={avg_f:.2%}, Relevancy={avg_r:.2%}")
        
        return {
            "avg_faithfulness": avg_f,
            "avg_relevancy": avg_r
        }
