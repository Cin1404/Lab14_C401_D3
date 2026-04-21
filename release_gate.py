import json
import os
import sys
from typing import Dict, Any

# =============================================================================
# CẤU HÌNH NGƯỠNG (THRESHOLDS)
# =============================================================================
THRESHOLDS = {
    "hit_rate": 0.80,       # Tối thiểu 80%
    "avg_mrr": 0.70,        # Tối thiểu 0.7
    "avg_score": 4.0,       # Tối thiểu 4.0/5.0
    "avg_faithfulness": 0.70, # Tối thiểu 70%
    "avg_relevancy": 0.80,    # Tối thiểu 80%
    "latency_max_inc": 0.20 # Không chậm hơn 20% so với bản cũ
}

def load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_release_gate():
    print("\n" + "="*50)
    print("       🤖 AI EVALUATION FACTORY: RELEASE GATE")
    print("="*50)

    # 1. Load Dữ liệu
    baseline = load_json("reports/summary_mock_lab8.json")
    candidate = load_json("reports/summary_lab8.json")

    if not baseline or not candidate:
        print("❌ Lỗi: Thiếu file báo cáo summary_lab8.json hoặc summary_mock.json.")
        sys.exit(1)

    b_meta = baseline["metadata"]
    c_meta = candidate["metadata"]
    b_metrics = baseline["metrics"]
    c_metrics = candidate["metrics"]

    print(f"Bản gốc (V1): {b_meta['version']} ({b_meta['timestamp']})")
    print(f"Bản mới (V2): {c_meta['version']} ({c_meta['timestamp']})")
    print("-" * 50)

    # 2. So sánh và Đánh giá
    checks = []
    
    # Check Hit Rate
    hr_pass = c_metrics["hit_rate"] >= THRESHOLDS["hit_rate"]
    checks.append(("Hit Rate", c_metrics["hit_rate"], THRESHOLDS["hit_rate"], hr_pass))

    # Check MRR
    mrr_pass = c_metrics["avg_mrr"] >= THRESHOLDS["avg_mrr"]
    checks.append(("Avg MRR", c_metrics["avg_mrr"], THRESHOLDS["avg_mrr"], mrr_pass))

    # Check Score
    score_pass = c_metrics["avg_score"] >= THRESHOLDS["avg_score"]
    checks.append(("LLM Score", c_metrics["avg_score"], THRESHOLDS["avg_score"], score_pass))

    # Check Faithfulness
    faith_pass = c_metrics.get("avg_faithfulness", 0) >= THRESHOLDS["avg_faithfulness"]
    checks.append(("Ragas Faith", c_metrics.get("avg_faithfulness", 0), THRESHOLDS["avg_faithfulness"], faith_pass))

    # Check Relevancy
    relev_pass = c_metrics.get("avg_relevancy", 0) >= THRESHOLDS["avg_relevancy"]
    checks.append(("Ragas Relev", c_metrics.get("avg_relevancy", 0), THRESHOLDS["avg_relevancy"], relev_pass))

    # Check Latency Regression
    max_allowed_lat = b_metrics["avg_latency"] * (1 + THRESHOLDS["latency_max_inc"])
    lat_pass = c_metrics["avg_latency"] <= max_allowed_lat
    checks.append(("Latency", c_metrics["avg_latency"], f"<= {max_allowed_lat:.2f}s", lat_pass))

    # 3. Hiển thị báo cáo
    print(f"{'Tiêu chí':<15} | {'Bản mới':<10} | {'Yêu cầu':<12} | {'Kết quả'}")
    print("-" * 50)
    
    all_passed = True
    for name, value, target, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        if not passed: all_passed = False
        
        # Định dạng hiển thị
        val_str = f"{value:.2%}" if "Rate" in name else (f"{value:.2f}" if isinstance(value, float) else str(value))
        tar_str = f"{target:.2%}" if isinstance(target, float) and "Rate" in name else (f"{target:.2f}" if isinstance(target, float) else str(target))
        
        print(f"{name:<15} | {val_str:<10} | {tar_str:<12} | {status}")

    # 4. Quyết định cuối cùng
    print("-" * 50)
    if all_passed:
        print("🎉 KẾT LUẬN: BẢN MỚI ĐẠT CHUẨN. CẤP PHÉP RELEASE!")
        decision = "APPROVED"
        exit_code = 0
    else:
        print("⛔ KẾT LUẬN: BẢN MỚI KHÔNG ĐẠT CHUẨN. CHẶN RELEASE!")
        decision = "REJECTED"
        exit_code = 1

    # 5. Lưu quyết định
    output = {
        "decision": decision,
        "timestamp": c_meta["timestamp"],
        "summary": {
            "baseline_version": b_meta["version"],
            "candidate_version": c_meta["version"],
            "all_passed": all_passed
        }
    }
    os.makedirs("reports", exist_ok=True)
    with open("reports/release_decision.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return exit_code

if __name__ == "__main__":
    sys.exit(run_release_gate())
