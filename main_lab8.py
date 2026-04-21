import asyncio
import json
import os
import time
import argparse
from dotenv import load_dotenv
from engine.runner import BenchmarkRunner
from agent.main_agent_lab8 import MainAgent
from engine.retrieval_eval_lab8 import RetrievalEvaluator
from engine.llm_judge_lab8 import MultiModelJudge
from engine.ragas_eval import RagasEvaluator

async def run_benchmark_with_results(agent_version: str, dataset_path: str):
    print(f"\n🚀 Khởi động Benchmark cho {agent_version}...")

    # Load dataset
    if not os.path.isabs(dataset_path):
        # Neu la duong dan tuong doi, ưu tiên tim so voi file main.py
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dataset_path = os.path.join(base_dir, dataset_path)
    
    if not os.path.exists(dataset_path):
        print(f"❌ Thiếu {dataset_path}. Hãy chạy 'python data/synthetic_gen.py' trước.")
        return None, None

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    if not dataset:
        print(f"❌ File {dataset_path} rỗng.")
        return None, None

    # Khởi tạo components
    agent = MainAgent()
    retrieval_eval = RetrievalEvaluator()
    llm_judge = MultiModelJudge()
    ragas_eval = RagasEvaluator()
    
    runner = BenchmarkRunner(agent, retrieval_eval, llm_judge)
    
    # Chạy Benchmark
    results = await runner.run_all(dataset)

    # Chạy RAGAS Evaluation (Faithfulness, Relevancy)
    ragas_metrics = await ragas_eval.calculate_metrics(results)

    # Tính toán Metrics
    total = len(results)
    if total == 0:
        return results, {}

    avg_latency = sum(r.get("latency", 0) for r in results) / total
    avg_hit_rate = sum(r.get("retrieval", {}).get("hit_rate", 0) for r in results) / total
    avg_mrr = sum(r.get("retrieval", {}).get("mrr", 0) for r in results) / total
    avg_judge_score = sum(r.get("judge", {}).get("final_score", 0) for r in results) / total
    avg_agreement_rate = sum(r.get("judge", {}).get("agreement_rate", 0) for r in results) / total
    
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
            "agreement_rate": avg_agreement_rate,
            "avg_faithfulness": ragas_metrics.get("avg_faithfulness", 0),
            "avg_relevancy": ragas_metrics.get("avg_relevancy", 0)
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
    print(f"  - Ragas Faith:  {m.get('avg_faithfulness', 0):.2%}")
    print(f"  - Ragas Relev:  {m.get('avg_relevancy', 0):.2%}")
    print(f"  - Avg Latency:  {m['avg_latency']:.2f}s")
    print("="*40 + "\n")

async def main():
    load_dotenv(override=True)
    
    parser = argparse.ArgumentParser(description="AI Evaluation Factory Benchmark Runner")
    parser.add_argument("--dataset", type=str, default="data/golden_set_lab8.jsonl", help="Đường dẫn đến file golden_set.jsonl")
    args = parser.parse_args()

    # Chạy benchmark cho phiên bản hiện tại
    results, summary = await run_benchmark_with_results("Agent_V1_Current", args.dataset)
    
    if summary:
        print_report(summary)
        
        # Lưu kết quả
        os.makedirs("reports", exist_ok=True)
        with open("reports/summary_lab8.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        with open("reports/benchmark_results_lab8.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Đã lưu báo cáo chi tiết vào thư mục 'reports/'.")

if __name__ == "__main__":
    asyncio.run(main())
