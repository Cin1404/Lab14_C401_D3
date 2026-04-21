import asyncio
import json
import os
import time
from dotenv import load_dotenv
from engine.runner import BenchmarkRunner
from agent.main_agent2 import MainAgent
from engine.retrieval_eval import RetrievalEvaluator
from engine.llm_judge_2 import MultiModelJudge
from engine.ragas_eval import RagasEvaluator

async def run_benchmark_with_results(agent_version: str):
    print(f"\n🚀 Khởi động Benchmark cho {agent_version}...")

    # Load dataset
    dataset_path = "data/golden_set.jsonl"
    if not os.path.exists(dataset_path):
        print(f"❌ Thiếu {dataset_path}. Hãy chạy 'python data/synthetic_gen.py' trước.")
        return None, None

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    if not dataset:
        print(f"❌ File {dataset_path} rỗng.")
        return None, None

    # Khởi tạo hỗ trợ xử lý lỗi UTF-8 cho console
    if os.name == 'nt':
        import sys
        sys.stdout.reconfigure(encoding='utf-8')

    # Khởi tạo components
    agent = MainAgent()
    retrieval_eval = RetrievalEvaluator()
    llm_judge = MultiModelJudge()
    ragas_eval = RagasEvaluator()
    
    runner = BenchmarkRunner(agent, retrieval_eval, llm_judge)
    
    # 1. Chạy Benchmark cơ bản
    results = await runner.run_all(dataset)

    # 2. Chạy Đánh giá RAGAS (Bổ sung Faithfulness & Relevancy)
    ragas_scores = await ragas_eval.calculate_metrics(results)

    # Tính toán Metrics tổng thể
    total = len(results)
    if total == 0:
        return results, {}

    avg_latency = sum(r.get("latency", 0) for r in results) / total
    avg_hit_rate = sum(r.get("retrieval", {}).get("hit_rate", 0) for r in results) / total
    avg_mrr = sum(r.get("retrieval", {}).get("mrr", 0) for r in results) / total
    avg_judge_score = sum(r.get("judge", {}).get("final_score", 0) for r in results) / total
    avg_agreement = sum(r.get("judge", {}).get("agreement_rate", 0) for r in results) / total
    
    summary = {
        "metadata": {
            "version": agent_version, 
            "total": total, 
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "metrics": {
            "avg_latency": avg_latency,
            "hit_rate": avg_hit_rate,
            "avg_mrr": avg_mrr,
            "avg_score": avg_judge_score,
            "agreement_rate": avg_agreement,
            "avg_faithfulness": ragas_scores.get("avg_faithfulness", 0),
            "avg_relevancy": ragas_scores.get("avg_relevancy", 0)
        }
    }
    
    return results, summary

def print_report(summary: dict):
    if not summary:
        return
    
    m = summary["metrics"]
    meta = summary["metadata"]
    
    print("\n" + "="*40)
    print(f"       BENCHMARK REPORT: {meta['version']}")
    print("="*40)
    print(f"Thời gian:       {meta['timestamp']}")
    print(f"Tổng số case:    {meta['total']}")
    print("-" * 40)
    print(f"RETRIEVAL STAGE:")
    print(f"  - Avg Hit Rate: {m['hit_rate']:.2%}")
    print(f"  - Avg MRR:      {m['avg_mrr']:.4f}")
    print("-" * 40)
    print(f"GENERATION STAGE:")
    print(f"  - Avg Score:    {m['avg_score']:.2f}/5.0")
    print(f"  - Faithfulness: {m.get('avg_faithfulness', 0):.2%}")
    print(f"  - Relevancy:     {m.get('avg_relevancy', 0):.2%}")
    print(f"  - Avg Latency:  {m['avg_latency']:.2f}s")
    print(f"  - Agreement:    {m['agreement_rate']:.1%}")
    print("="*40 + "\n")

async def main():
    load_dotenv(override=True)
    
    # Chạy benchmark cho phiên bản hiện tại
    results, summary = await run_benchmark_with_results("Agent_V1_Current")
    
    if summary:
        print_report(summary)
        
        # Lưu kết quả
        os.makedirs("reports", exist_ok=True)
        with open("reports/summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        with open("reports/results_detail.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Đã lưu báo cáo chi tiết vào thư mục 'reports/'.")

if __name__ == "__main__":
    asyncio.run(main())
