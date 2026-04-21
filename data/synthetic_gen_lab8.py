import json
import asyncio
import os
import time
import sys
import random
from typing import List, Dict
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Thêm project root vào sys.path để import từ engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.index_v2 import LabIndexer

load_dotenv(override=True)

class SyntheticDataGenerator:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name

    async def generate_batch(self, text: str, chunk_id: str, num_pairs: int = 5, difficulty: str = "easy") -> List[Dict]:
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
            "metadata": {{ "difficulty": "{difficulty}", "chunk_id": "{chunk_id}" }},
            "expected_retrieval_ids": ["{chunk_id}"]
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
                
                # Check for common wrapping keys
                final_list = []
                if isinstance(content, list):
                    final_list = content
                elif isinstance(content, dict):
                    for key in ["results", "qa_pairs", "data", "questions"]:
                        if key in content and isinstance(content[key], list):
                            final_list = content[key]
                            break
                    if not final_list and "question" in content:
                        final_list = [content]
                
                # Bổ sung chunk_id nếu Model quên field expected_retrieval_ids
                for item in final_list:
                    if "expected_retrieval_ids" not in item or not item["expected_retrieval_ids"]:
                        item["expected_retrieval_ids"] = [chunk_id]
                    if "metadata" not in item:
                        item["metadata"] = {}
                    item["metadata"]["chunk_id"] = chunk_id
                    item["metadata"]["difficulty"] = difficulty

                return final_list
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
    # 1. Khởi tạo Indexer để lấy chunks thật
    print("🔍 Đang lấy dữ liệu chunks từ ChromaDB...")
    try:
        indexer = LabIndexer()
        all_chunks = indexer.get_all_chunks()
    except Exception as e:
        print(f"❌ Lỗi khi kết nối ChromaDB: {e}")
        print("💡 Hãy đảm bảo bạn đã chạy 'python engine/index_v2.py' trước.")
        return

    if not all_chunks:
        print("⚠️ Không tìm thấy chunk nào trong ChromaDB. Hãy chạy Indexing trước.")
        return

    print(f"✅ Tìm thấy {len(all_chunks)} chunks.")

    # 2. Cấu hình sinh dữ liệu
    generator = SyntheticDataGenerator(model_name="gpt-4o-mini")
    all_qa_pairs = []

    # Chọn ngẫu nhiên một số chunks để sinh dữ liệu (để tiết kiệm token và thời gian)
    num_chunks_to_use = min(10, len(all_chunks))
    selected_chunks = random.sample(all_chunks, num_chunks_to_use)

    configs = [
        {"diff": "easy", "num_pairs": 3},
        {"diff": "hard", "num_pairs": 2},
    ]

    print(f"🚀 Bắt đầu tạo dữ liệu tổng hợp từ {num_chunks_to_use} chunks...")

    for chunk in selected_chunks:
        chunk_id = chunk["id"]
        text = chunk["text"]
        
        for config in configs:
            diff = config["diff"]
            num_pairs = config["num_pairs"]
            
            print(f" -> Đang tạo {num_pairs} câu {diff} cho chunk {chunk_id}...")
            batch = await generator.generate_batch(text, chunk_id, num_pairs=num_pairs, difficulty=diff)
            if batch:
                all_qa_pairs.extend(batch)
            
            # Nghỉ ngắn giữa các lần gọi
            await asyncio.sleep(2)

    # 3. Lưu kết quả
    if all_qa_pairs:
        os.makedirs("data", exist_ok=True)
        output_file = "data/golden_set_lab8.jsonl"
        with open(output_file, "w", encoding="utf-8") as f:
            for pair in all_qa_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + "\n")
        print(f"✅ Hoàn thành! Đã tạo {len(all_qa_pairs)} cases tại {output_file}")
    else:
        print("❌ Không tạo được dữ liệu nào.")

if __name__ == "__main__":
    asyncio.run(main())
