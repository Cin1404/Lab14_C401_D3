import json
import asyncio
import os
import time
from typing import List, Dict
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class SyntheticDataGenerator:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name

    async def generate_batch(self, text: str, num_pairs: int = 5, difficulty: str = "easy") -> List[Dict]:
        """
        Sử dụng OpenAI gpt-4o-mini để tạo các cặp (Question, Expected Answer, Context) từ đoạn văn bản.
        """
        prompt = f"""
        Nhiệm vụ: Tạo ra đúng {num_pairs} cặp câu hỏi/trả lời từ tài liệu.
        Độ khó: {difficulty.upper()}
        
        Định dạng trả về là JSON array, mỗi phần tử có cấu trúc sau:
        {{
            "question": "Câu hỏi",
            "expected_answer": "Câu trả lời chuẩn",
            "context": "Đoạn trích dẫn tài liệu",
            "metadata": {{ "difficulty": "{difficulty}" }},
            "expected_retrieval_ids": ["doc_{difficulty}"]
        }}
        
        Tài liệu: {text}
        """

        # Thử lại (Retry) tối đa 3 lần nếu gặp lỗi Rate Limit
        for attempt in range(3):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that generates high-quality synthetic data in JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                raw_content = response.choices[0].message.content
                content = json.loads(raw_content)
                
                # OpenAI json_object mode requires a root key usually, or we can just parse it.
                # If the content is already a list, return it. If not, look for common keys.
                if isinstance(content, list):
                    return content
                elif isinstance(content, dict):
                    # Check for common wrapping keys
                    for key in ["results", "qa_pairs", "data", "questions"]:
                        if key in content and isinstance(content[key], list):
                            return content[key]
                    # If it's a single object that should have been a list, wrap it
                    if "question" in content:
                        return [content]
                    
                return []
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg:
                    wait_time = (attempt + 1) * 2
                    print(f"⚠️ OpenAI Rate Limit. Đang nghỉ {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"❌ Lỗi OpenAI: {e}")
                    return []
        return []

async def main():
    # Tài liệu nguồn
    source_text = """
    AI Evaluation Factory là quy trình đánh giá AI chuyên sâu. 
    Nó giúp đo lường Hit Rate, MRR và độ chính xác của câu trả lời. 
    Quy trình gồm 4 giai đoạn chính: 1. SDG (Tạo dữ liệu), 2. Eval Engine (Bộ máy chấm điểm), 
    3. Failure Analysis (Phân tích lỗi), 4. Report (Báo cáo).
    """
    
    # Dùng gpt-4o-mini
    generator = SyntheticDataGenerator(model_name="gpt-4o-mini")
    all_qa_pairs = []

    print("🚀 Bắt đầu tạo dữ liệu tổng hợp (Chế độ Sequential để tránh 429 Error)...")
    
    configs = [
        {"diff": "easy", "total": 20},
        {"diff": "hard", "total": 20},
        {"diff": "adversarial", "total": 10},
    ]

    for config in configs:
        diff = config["diff"]
        total = config["total"]
        batch_size = 5 # Chia nhỏ mỗi lần 5 câu
        
        for i in range(0, total, batch_size):
            print(f" đang tạo {batch_size} câu loại {diff} ({i}/{total})...")
            batch = await generator.generate_batch(source_text, num_pairs=batch_size, difficulty=diff)
            if batch:
                all_qa_pairs.extend(batch)
            
            # Nghỉ giữa các lần gọi để không bị API block
            await asyncio.sleep(12) 

    # Lưu kết quả
    if all_qa_pairs:
        os.makedirs("data", exist_ok=True)
        with open("data/golden_set.jsonl", "w", encoding="utf-8") as f:
            for pair in all_qa_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + "\n")
        print(f"✅ Hoàn thành! Đã tạo {len(all_qa_pairs)} cases tại data/golden_set.jsonl")
    else:
        print("❌ Không tạo được dữ liệu nào. Hãy kiểm tra lại API Key và Quota.")

if __name__ == "__main__":
    asyncio.run(main())
