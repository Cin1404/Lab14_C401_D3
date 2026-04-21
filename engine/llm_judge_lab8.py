import asyncio
import os
import json
from typing import Dict, Any
from openai import AsyncOpenAI

class MultiModelJudge:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY không được tìm thấy trong môi trường.")
        
        self.client = AsyncOpenAI(api_key=api_key)
        # Sử dụng 2 model khác nhau để so sánh
        self.model_a = "gpt-4o-mini"
        self.model_b = "gpt-4o"
        
        # Định nghĩa Rubric chấm điểm chuẩn
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

    async def _get_score(self, model_name: str, question: str, answer: str, ground_truth: str) -> Dict:
        """
        Gọi OpenAI với một Model cụ thể.
        """
        prompt = f"""
        {self.rubric}
        
        Dữ liệu đánh giá:
        - Câu hỏi: {question}
        - Câu trả lời của AI: {answer}
        - Ground Truth (Đáp án đúng): {ground_truth}
        
        Hãy chấm điểm ngay:
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": f"You are a professional quality auditor using {model_name}."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            raw_content = response.choices[0].message.content
            return json.loads(raw_content)
        except Exception as e:
            print(f"Error calling OpenAI Judge ({model_name}): {e}")
            return {"score": 3, "reasoning": f"Lỗi kỹ thuật với model {model_name}: {str(e)}"}

    async def evaluate_multi_judge(self, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        """
        Thực hiện đánh giá bằng 2 model khác nhau (gpt-4o-mini và gpt-4o).
        """
        # Chạy song song 2 model
        tasks = [
            self._get_score(self.model_a, question, answer, ground_truth),
            self._get_score(self.model_b, question, answer, ground_truth)
        ]
        
        judgements = await asyncio.gather(*tasks)
        
        score_a = judgements[0].get("score", 3)
        score_b = judgements[1].get("score", 3)
        
        avg_score = (score_a + score_b) / 2
        # Tính độ đồng thuận (Agreement Rate)
        agreement = 1.0 if score_a == score_b else (1.0 - abs(score_a - score_b)/4)
        
        return {
            "final_score": avg_score,
            "agreement_rate": agreement,
            "individual_scores": {
                self.model_a: judgements[0],
                self.model_b: judgements[1]
            }
        }

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    async def test():
        judge = MultiModelJudge()
        print(f"🚀 Đang chạy thử nghiệm Multi-Model Judge ({judge.model_a} vs {judge.model_b})...")
        res = await judge.evaluate_multi_judge(
            "Chính sách nghỉ phép của công ty như thế nào?",
            "Nhân viên được nghỉ 12 ngày phép mỗi năm và cần báo trước 3 ngày.",
            "Nhân viên có 12 ngày nghỉ phép năm. Cần gửi yêu cầu qua HR Portal trước ít nhất 3 ngày làm việc."
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))
    
    asyncio.run(test())

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    async def test():
        judge = MultiModelJudge()
        res = await judge.evaluate_multi_judge(
            "Thủ đô của Pháp là gì?",
            "Thủ đô của Pháp là Paris.",
            "Paris"
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))
    
    asyncio.run(test())
