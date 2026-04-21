import json
import os

def analyze_failures(detail_path):
    with open(detail_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Định nghĩa case thất bại: hit_rate < 1.0 HOẶC score < 4.0
    failures = []
    for item in data:
        hr = item.get("retrieval", {}).get("hit_rate", 0)
        score = item.get("judge", {}).get("final_score", 0)
        if hr < 1.0 or score < 4.0:
            failures.append(item)
    
    clusters = {
        "Retrieval Error": 0,
        "Hallucination": 0,
        "Incomplete / Missing Detail": 0,
        "Tone / Professionalism": 0,
        "Other": 0
    }
    
    print(f"--- PHÂN TÍCH {len(failures)} CASE THẤT BẠI ---")
    
    for item in failures:
        hr = item.get("retrieval", {}).get("hit_rate", 0)
        reason = item.get("judge", {}).get("individual_scores", {}).get("strict_judge", {}).get("reasoning", "").lower()
        
        if hr < 1.0:
            clusters["Retrieval Error"] += 1
        elif "chưa đề cập" in reason or "thiếu" in reason or "incomplete" in reason:
            clusters["Incomplete / Missing Detail"] += 1
        elif "không có trong" in reason or "sai lệch" in reason or "không chính xác" in reason:
            clusters["Hallucination"] += 1
        elif "chuyên nghiệp" in reason or "lịch sự" in reason or "tone" in reason:
            clusters["Tone / Professionalism"] += 1
        else:
            clusters["Other"] += 1
            
    return clusters

if __name__ == "__main__":
    path = "reports/benchmark_results_lab8.json"
    if os.path.exists(path):
        results = analyze_failures(path)
        print("\nKẾT QUẢ PHÂN NHÓM:")
        for cluster, count in results.items():
            if count > 0:
                print(f"| {cluster} | {count} |")
