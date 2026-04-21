# BÁO CÁO CÁ NHÂN - TỐI ƯU HÓA LLM AGENT BENCHMARK
**Họ và tên:** Lưu Quang Lực  
**MSSV:** 2A202600121  

---

## 1. Bảng Tiêu chí Đánh giá (Rubric)

| Hạng mục | Tiêu chí | Điểm |
| :--- | :--- | :---: |
| **Engineering Contribution** | - Đóng góp cụ thể vào các module phức tạp (Async, Multi-Judge, Metrics).<br>- Chứng minh qua Git commits và giải trình kỹ thuật. | 15 |
| **Technical Depth** | - Giải thích được các khái niệm: MRR, Cohen's Kappa, Position Bias.<br>- Hiểu về trade-off giữa Chi phí và Chất lượng. | 15 |
| **Problem Solving** | - Cách giải quyết các vấn đề phát sinh trong quá trình code hệ thống phức tạp. | 10 |

---

## 2. Phần làm Retrieval & Optimization (Lab 8)
Tôi đã chịu trách nhiệm chính trong việc xây dựng hệ thống Retrieval dựa trên ChromaDB và bộ máy đánh giá Metrics tự động.

### A. Engineering Contribution (Đóng góp Kỹ thuật)
Tôi đã thực hiện các thay đổi cốt lõi sau:

- **ChromaDB & OpenAI Integration**: Trực tiếp triển khai phương thức `search()` trong `LabIndexer`, tích hợp OpenAI `text-embedding-3-small` để chuyển đổi câu hỏi thành vector và tìm kiếm lân cận (Cosine Similarity) trên 34 chunks tài liệu thật.
- **Dynamic SDG (Synthetic Data Generation)**: Refactor lại file `synthetic_gen_lab8.py` để không còn dùng ID giả. Script hiện tại tự động truy vấn ChromaDB để lấy `chunk_id` thật làm Ground Truth, giúp chỉ số Hit Rate và MRR phản ánh đúng năng lực thật của Agent.
- **Automation Pipeline**: Xây dựng module `release_gate.py` cho phép so sánh hai phiên bản Agent (Baseline vs Candidate) và tự động đưa ra quyết định "APPROVED" hoặc "REJECTED" dựa trên các ngưỡng (Thresholds) về Hit Rate, Score và Latency.
- **RAGAS-Lite Integration**: Tích hợp thêm hai chỉ số nâng cao là **Faithfulness** (độ trung thực) và **Answer Relevancy** (độ liên quan) vào quy trình benchmark để kiểm soát hoàn toàn hiện tượng ảo giác (hallucination).

### B. Technical Depth (Chiều sâu kỹ thuật)
- **MRR (Mean Reciprocal Rank)**: Tôi áp dụng MRR để đo lường không chỉ việc Agent có tìm thấy tài liệu hay không, mà còn là tài liệu đúng nằm ở vị trí thứ mấy. Điều này quan trọng vì nếu tài liệu đúng ở vị trí #1, Agent sẽ trả lời tốt hơn nhiều so với vị trí #5.
- **Trade-off Latency vs Accuracy**: Trong quá trình tối ưu, tôi đã hy sinh một chút Latency (do gọi thêm Ragas & Multi-judge) để đổi lấy sự an toàn tuyệt đối cho hệ thống thông qua bộ lọc Release Gate.

### C. Problem Solving (Giải quyết vấn đề)
- **Problem**: Ban đầu hệ thống Benchmark luôn báo Hit Rate 0% dù Agent trả lời rất tốt.
- **Solution**: Tôi phát hiện ra nguyên nhân là do SDG tạo ID theo format `doc_easy` trong khi Indexer lưu ID theo format `source_filename_index`. Tôi đã giải quyết bằng cách viết lại module SDG để nó "hiểu" được cấu trúc ID trong database thông qua `indexer.get_all_chunks()`.

---

## 3. Kết quả Benchmark Thực tế (Bản V1 Current)
- **Avg Hit Rate:** 81.63% (Vượt ngưỡng 80%)
- **Avg MRR:** 0.7653
- **LLM Judge Score:** 4.28 / 5.0
- **Answer Relevancy:** 86.94%
