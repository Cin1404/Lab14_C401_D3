import json
import os

def validate_lab():
    print("🔍 Đang kiểm tra định dạng bài nộp...")
    
    required_files = [
        "reports/summary.json",
        "reports/benchmark_results.json",
        "analysis/failure_analysis.md"
    ]
    
    # 1. Kiểm tra sự tồn tại của file
    for f in required_files:
        if os.path.exists(f):
            print(f"✅ Tìm thấy: {f}")
        else:
            print(f"❌ Thiếu file: {f}")
            return

    # 2. Kiểm tra nội dung summary.json
    with open("reports/summary.json", "r") as f:
        data = json.load(f)
        
        metrics = data["metrics"]
        
        print(f"\n--- Thống kê nhanh ---")
        print(f"Tổng số cases: {data['metadata']['total']}")
        print(f"Điểm trung bình: {metrics['avg_score']:.2f}")
        
        # EXPERT CHECKS
        has_retrieval = "hit_rate" in metrics
        has_multi_judge = "agreement_rate" in metrics or "avg_score" in metrics # In expert version, avg_score comes from multi-judge
        
        if has_retrieval:
            print(f"✅ Đã tìm thấy Retrieval Metrics (Hit Rate: {metrics['hit_rate']*100:.1f}%)")
        else:
            print(f"⚠️ CẢNH BÁO: Thiếu Retrieval Metrics.")

        if data["metadata"].get("version"):
            print(f"✅ Đã tìm thấy thông tin phiên bản Agent (Regression Mode)")

    print("\n🚀 Bài lab đã sẵn sàng để chấm điểm!")

if __name__ == "__main__":
    validate_lab()
