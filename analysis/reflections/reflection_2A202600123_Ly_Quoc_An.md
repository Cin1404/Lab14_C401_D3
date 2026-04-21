# BÁO CÁO CÁ NHÂN - TỐI ƯU HÓA LLM AGENT BENCHMARK
**Họ và tên:** Lý Quốc An  
**MSSV:** 2A202600123  

---

## 1. Bảng Tiêu chí Đánh giá (Rubric)

| Hạng mục | Tiêu chí | Điểm |
| :--- | :--- | :---: |
| **Engineering Contribution** | - Đóng góp cụ thể vào các module phức tạp (Async, Multi-Judge, Metrics).<br>- Chứng minh qua Git commits và giải trình kỹ thuật. | 15 |
| **Technical Depth** | - Giải thích được các khái niệm: MRR, Cohen's Kappa, Position Bias.<br>- Hiểu về trade-off giữa Chi phí và Chất lượng. | 15 |
| **Problem Solving** | - Cách giải quyết các vấn đề phát sinh trong quá trình code hệ thống phức tạp. | 10 |

---

## 2. Chi tiết Đóng góp Kỹ thuật
Tôi đã chịu trách nhiệm chính toàn tuyến từ đánh giá Agent, chia task , xử lý Dữ liệu thực tế, sinh bộ test , triển khai bộ Đánh giá (Evaluation) cho đến chốt chặn Phát hành (Release Gate).

### A. Engineering Contribution (Đóng góp chi tiết)
Dưới đây là 4 mảng cốt lõi mà tôi đã trực tiếp code và hoàn thiện:

- **Xử lý Dữ liệu Thực & Chunking (Data/Chunking):** Xây dựng pipeline tiền xử lý để làm sạch dữ liệu thật (các tài liệu SOP, Policy, FAQ thực tế), thực hiện phân chia văn bản (chunking) bảo toàn ngữ nghĩa và đẩy vào Vector DB (ChromaDB) thông qua OpenAI Embeddings.
- **Sinh Bối cảnh & Bộ Test (Synthetic Data Generation):** Viết module sinh dữ liệu giả lập (`synthetic_gen`). Script có khả năng quét qua các chunk thật trong ChromaDB để tự động rèn luyện các câu hỏi đa dạng, và map ngược `chunk_id` thực tế làm Ground Truth để phục vụ đánh giá chính xác.
- **Phát triển Hệ thống Đánh giá (Evaluation Module):** Cài đặt toàn diện quy trình chạy Eval tự động. Tôi đã tích hợp LLM-as-a-Judge đi kèm các chỉ số tiên tiến như **Faithfulness** (Độ trung thực) và **Answer Relevancy** (Độ liên quan) để lượng hoá chính xác hiện tượng ảo giác (Hallucination) từ Agent.
- **Cơ chế Chốt chặn Phát hành (Release Gate):** Code script `release_gate.py` đóng vai trò rào chắn tự động. Hệ thống sẽ so sánh toàn diện các Metrics (Hit Rate, Latency, Score) giữa phiên bản Candidate và Baseline trước khi đưa ra phán quyết tự động "APPROVED" hoặc "REJECTED".

### B. Technical Depth (Chiều sâu kỹ thuật)
- **MRR (Mean Reciprocal Rank)**: Tôi áp dụng MRR để đo lường không chỉ việc Agent có tìm thấy tài liệu hay không, mà còn là tài liệu đúng nằm ở vị trí thứ mấy. Điều này quan trọng vì nếu tài liệu đúng ở vị trí #1, Agent sẽ trả lời tốt hơn nhiều so với vị trí #5.
- **Trade-off Latency vs Accuracy**: Trong quá trình tối ưu, tôi đã hy sinh một chút Latency (do gọi thêm Ragas & Multi-judge) để đổi lấy sự an toàn tuyệt đối cho hệ thống thông qua bộ lọc Release Gate.

### C. Problem Solving (Giải quyết vấn đề)
- **Problem**: Ban đầu hệ thống Benchmark luôn báo Hit Rate 0% dù Agent trả lời rất tốt.
- **Solution**: Tôi phát hiện ra nguyên nhân là do SDG tạo ID không khớp với format trong ChromaDB. Tôi đã giải quyết bằng cách viết lại module SDG để nó truy vấn trực tiếp danh sách IDs từ database thông qua `indexer.get_all_chunks()`, đảm bảo tính đồng nhất dữ liệu.

---

## 3. Kết quả Benchmark Thực tế (Bản V1 Current)
- **Avg Hit Rate:** 81.63% (Vượt ngưỡng 80%)
- **Avg MRR:** 0.7653
- **LLM Judge Score:** 4.28 / 5.0
- **Answer Relevancy:** 86.94%
