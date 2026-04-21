from typing import List, Dict

class RetrievalEvaluator:
    def __init__(self):
        pass

    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
        """
        Calculates if at least one of the expected_ids is present in the top_k retrieved_ids.
        
        Hit Rate @ K = 1 if any expected_id in retrieved_ids[:K] else 0.
        """
        if not expected_ids or not retrieved_ids:
            return 0.0
            
        top_retrieved = retrieved_ids[:top_k]
        # Check if there is any intersection between expected and retrieved
        hit = any(doc_id in top_retrieved for doc_id in expected_ids)
        return 1.0 if hit else 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        """
        Calculates Mean Reciprocal Rank (MRR).
        Finds the rank of the first relevant document in the retrieved list.
        
        MRR = 1 / rank (1-indexed). Returns 0.0 if no relevant document is found.
        """
        if not expected_ids or not retrieved_ids:
            return 0.0
            
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return 1.0 / (i + 1)
        return 0.0

    async def evaluate_batch(self, results: List[Dict], top_k: int = 3) -> Dict:
        """
        Runs evaluation for a batch of results.
        
        Args:
            results: List of dicts containing 'expected_retrieval_ids' and 'retrieved_ids'.
            top_k: The K value for Hit Rate calculation.
            
        Returns:
            Dict containing aggregated metrics.
        """
        if not results:
            return {f"avg_hit_rate_at_{top_k}": 0.0, "avg_mrr": 0.0}
            
        total_hit_rate = 0.0
        total_mrr = 0.0
        count = 0
        
        for res in results:
            expected = res.get("expected_retrieval_ids", [])
            retrieved = res.get("retrieved_ids", [])
            
            total_hit_rate += self.calculate_hit_rate(expected, retrieved, top_k=top_k)
            total_mrr += self.calculate_mrr(expected, retrieved)
            count += 1
            
        return {
            f"avg_hit_rate_at_{top_k}": total_hit_rate / count if count > 0 else 0,
            "avg_mrr": total_mrr / count if count > 0 else 0
        }

if __name__ == "__main__":
    evaluator = RetrievalEvaluator()
    
    # Dữ liệu mẫu để kiểm tra
    sample_results = [
        {
            "expected_retrieval_ids": ["doc_1"],
            "retrieved_ids": ["doc_1", "doc_2", "doc_3"] # Hit @ Rank 1
        },
        {
            "expected_retrieval_ids": ["doc_5"],
            "retrieved_ids": ["doc_2", "doc_5", "doc_1"] # Hit @ Rank 2
        },
        {
            "expected_retrieval_ids": ["doc_9"],
            "retrieved_ids": ["doc_1", "doc_2", "doc_3"] # Miss
        }
    ]
    
    import asyncio
    async def run_test():
        metrics = await evaluator.evaluate_batch(sample_results, top_k=3)
        print("\n[ KIỂM TRA RETRIEVAL EVALUATOR ]")
        print("====================================")
        print(f"Sample Results: {len(sample_results)} cases")
        print(f"Avg Hit Rate @ 3: {metrics['avg_hit_rate_at_3']:.2%}")
        print(f"Avg MRR:         {metrics['avg_mrr']:.4f}")
        print("------------------------------------\n")
        
    asyncio.run(run_test())
