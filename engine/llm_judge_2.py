import asyncio
import os
import json
from openai import AsyncOpenAI
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

class MultiModelJudge:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or "your_openai_api_key_here" in api_key:
            print("WARNING: OPENAI_API_KEY not found or invalid in .env")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model_name = model_name
        
        # Định nghĩa Rubric chấm điểm
        self.rubric = """
        Bạn là một chuyên gia đánh giá chất lượng câu trả lời của AI.
        Hãy chấm điểm câu trả lời dựa trên thang điểm từ 1 đến 5 với các tiêu chí sau:
        1. Accuracy (Độ chính xác): So với Ground Truth, thông tin có đúng không?
        2. Relevance (Độ liên quan): Câu trả lời có giải quyết đúng vấn đề người dùng hỏi không?
        3. Professionalism (Sự chuyên nghiệp): Ngôn ngữ có lịch sự, rõ ràng không?

        Thang điểm:
        - 5 (Excellent): Hoàn hảo, chính xác tuyệt đối, hành văn chuyên nghiệp.
        - 4 (Good): Chính xác, có ích nhưng có thể cải thiện cách diễn đạt.
        - 3 (Fair): Có thông tin đúng nhưng còn thiếu sót hoặc hơi lan man.
        - 2 (Poor): Thông tin sai lệch một phần hoặc không rõ ràng.
        - 1 (Critical Fail): Sai hoàn toàn thông tin hoặc vi phạm quy tắc ứng xử.

        Định dạng phản hồi bắt buộc là JSON:
        {"score": <int>, "reasoning": "<chuỗi giải thích lý do>"}
        """

    async def _get_score_from_persona(self, system_instruction: str, question: str, answer: str, ground_truth: str) -> Dict:
        """
        Gọi OpenAI với một Persona (vai trò) cụ thể và tính toán chi phí.
        """
        prompt = f"""
        Dữ liệu đánh giá:
        - Câu hỏi: {question}
        - Câu trả lời của AI: {answer}
        - Ground Truth (Đáp án đúng): {ground_truth}
        
        Hãy chấm điểm ngay:
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0 # Ép kiểu JSON và sử dụng temperature thấp để ổn định kết quả (Calibration)
            )
            
            # Tính toán chi phí (gpt-4o-mini: $0.15/1M input, $0.60/1M output)
            usage = response.usage
            input_cost = (usage.prompt_tokens / 1_000_000) * 0.15
            output_cost = (usage.completion_tokens / 1_000_000) * 0.60
            total_cost = input_cost + output_cost

            content = json.loads(response.choices[0].message.content)
            content["usage_cost"] = total_cost
            
            return content
        except Exception as e:
            print(f"Error calling OpenAI Judge: {e}")
            return {"score": 3, "reasoning": f"Lỗi kỹ thuật khi chấm điểm: {str(e)}", "usage_cost": 0}

    async def evaluate_multi_judge(self, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        """
        Thực hiện đánh giá từ 2 góc nhìn khác nhau (Sử dụng OpenAI calls).
        """
        # Persona 1: Chuyên gia khắt khe (Focus on Accuracy)
        persona_strict = f"{self.rubric}\n\nLưu ý: Bạn là một chuyên gia khắt khe, ưu tiên tuyệt đối độ chính xác của dữ kiện."
        
        # Persona 2: Chuyên gia trải nghiệm người dùng (Focus on Tone & Helpfulness)
        persona_helpful = f"{self.rubric}\n\nLưu ý: Bạn là một chuyên gia UX, ưu tiên cách diễn đạt dễ hiểu và sự hữu ích cho người dùng."

        # Chạy song song
        tasks = [
            self._get_score_from_persona(persona_strict, question, answer, ground_truth),
            self._get_score_from_persona(persona_helpful, question, answer, ground_truth)
        ]
        
        judgements = await asyncio.gather(*tasks)
        
        score_a = judgements[0].get("score", 3)
        score_b = judgements[1].get("score", 3)
        total_cost = sum(j.get("usage_cost", 0) for j in judgements)
        
        avg_score = (score_a + score_b) / 2
        agreement = 1.0 if score_a == score_b else (1.0 - abs(score_a - score_b)/4)
        
        return {
            "final_score": avg_score,
            "agreement_rate": agreement,
            "total_cost": total_cost,
            "individual_scores": {
                "strict_judge": judgements[0],
                "helpful_judge": judgements[1]
            }
        }

if __name__ == "__main__":
    async def test():
        judge = MultiModelJudge()
        print(f"Testing with model: {judge.model_name}")
        res = await judge.evaluate_multi_judge(
            "Thủ đô của Pháp là gì?",
            "Thủ đô của Pháp là Paris.",
            "Paris"
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))
    
    asyncio.run(test())
