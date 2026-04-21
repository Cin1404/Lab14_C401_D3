import json
import os

def export_retrieval_failures(input_path: str, output_path: str):
    """
    Tìm và xuất các trường hợp Retrieval bị sai (hit_rate == 0) ra file JSON.
    """
    if not os.path.exists(input_path):
        print(f"❌ Không tìm thấy file đầu vào: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    # Lọc các trường hợp có hit_rate == 0
    failures = [res for res in results if res.get("retrieval", {}).get("hit_rate") == 0]

    # Lưu ra file mới
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(failures, f, ensure_ascii=False, indent=2)

    print(f"✅ Đã tìm thấy {len(failures)} trường hợp retrieval sai.")
    print(f"✅ Đã lưu kết quả vào: {output_path}")

if __name__ == "__main__":
    # Đường dẫn file kết quả chi tiết
    input_file = "reports/results_detail.json"
    # Đường dẫn file lỗi retrieval
    output_file = "reports/retrieval_failures.json"
    
    export_retrieval_failures(input_file, output_file)
