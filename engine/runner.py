import asyncio
import time
from typing import List, Dict
from tqdm import tqdm

class BenchmarkRunner:
    def __init__(self, agent, retrieval_eval, llm_judge):
        self.agent = agent
        self.retrieval_eval = retrieval_eval
        self.llm_judge = llm_judge
        self.semaphore = asyncio.Semaphore(5) # Giới hạn 5 request đồng thời

    async def run_single_test(self, test_case: Dict) -> Dict:
        """
        Thực hiện một lượt loop: Agent -> Retrieval Eval -> LLM Judge
        """
        async with self.semaphore:
            start_time = time.perf_counter()
            try:
                # 1. Gọi Agent
                response = await self.agent.query(test_case["question"])
                latency = time.perf_counter() - start_time
                
                # Lấy retrieved_ids từ metadata của Agent
                retrieved_ids = response.get("metadata", {}).get("retrieved_ids", [])
                expected_ids = test_case.get("expected_retrieval_ids", [])

                # 2. Chạy Retrieval Eval
                retrieval_scores = {
                    "hit_rate": self.retrieval_eval.calculate_hit_rate(expected_ids, retrieved_ids),
                    "mrr": self.retrieval_eval.calculate_mrr(expected_ids, retrieved_ids)
                }
                
                # 3. Chạy Multi-Judge (Generation Eval)
                judge_result = await self.llm_judge.evaluate_multi_judge(
                    test_case["question"], 
                    response["answer"], 
                    test_case["expected_answer"]
                )
                
                return {
                    "question": test_case["question"],
                    "agent_answer": response["answer"],
                    "expected_answer": test_case["expected_answer"],
                    "latency": latency,
                    "retrieval": retrieval_scores,
                    "judge": judge_result,
                    "expected_retrieval_ids": expected_ids,
                    "retrieved_ids": retrieved_ids
                }
            except Exception as e:
                print(f"Error running test case: {e}")
                return {"error": str(e)}

    async def run_all(self, dataset: List[Dict]) -> List[Dict]:
        """
        Chạy toàn bộ dataset với progress bar.
        """
        tasks = [self.run_single_test(case) for case in dataset]
        results = []
        
        # Sử dụng tqdm để theo dõi tiến độ
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="🚀 Benchmarking"):
            res = await f
            results.append(res)
            
        return results
