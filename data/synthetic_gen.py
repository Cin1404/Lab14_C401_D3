import json
import asyncio
import os
import time
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Cấu hình Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class SyntheticDataGenerator:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    async def generate_batch(self, text: str, num_pairs: int = 5, difficulty: str = "easy") -> List[Dict]:
        """
        Sử dụng Gemini để tạo các cặp (Question, Expected Answer, Context) từ đoạn văn bản.
        """
        prompt = f"""
        Nhiệm vụ: Tạo ra đúng {num_pairs} cặp câu hỏi/trả lời từ tài liệu.
        Độ khó: {difficulty.upper()}
        
        Định dạng trả về là JSON array, mỗi phần tử có:
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
                response = await self.model.generate_content_async(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                
                content = json.loads(response.text)
                if isinstance(content, list):
                    return content
                elif isinstance(content, dict):
                    return content.get("results", content.get("qa_pairs", []))
                return []
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "quota" in err_msg.lower():
                    wait_time = (attempt + 1) * 30
                    print(f"⚠️ Bị giới hạn tốc độ (429). Đang nghỉ {wait_time}s trước khi thử lại...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"❌ Lỗi: {e}")
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
    
    # Dùng 1.5-flash để ổn định với gói Free
    generator = SyntheticDataGenerator(model_name="gemini-2.5-flash")
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
