# BÁO CÁO CÁ NHÂN - LLM AGENT BENCHMARK
**Họ và tên:** Lưu Thị Ngọc Quỳnh  
**MSSV:** 2A202600122  

---

## 1. Bảng Tiêu chí Đánh giá

| Hạng mục | Tiêu chí | Điểm |
| :--- | :--- | :---: |
| **Engineering Contribution** | Đóng góp vào module phức tạp: Async, Metrics, Multi-Judge. Có giải trình kỹ thuật và Git commit. | 15 |
| **Technical Depth** | Hiểu MRR, Cohen's Kappa, Position Bias và trade-off giữa chi phí với chất lượng. | 15 |
| **Problem Solving** | Giải quyết vấn đề khi xây dựng hệ thống benchmark phức tạp. | 10 |

---

## 2. Phần làm `runner.py`

Tôi phụ trách module **`engine/runner.py`**, đây là phần điều phối benchmark chính của hệ thống. Runner kết nối các thành phần: **Agent -> Retrieval Evaluation -> Multi-Judge**, sau đó trả về kết quả để tạo báo cáo và phân tích lỗi.

### A. Engineering Contribution

Trong `BenchmarkRunner`, tôi đã triển khai các chức năng chính:

- **Async Runner**: dùng `asyncio.as_completed()` để chạy nhiều test case cùng lúc, giúp benchmark nhanh hơn so với chạy tuần tự.
- **Giới hạn concurrency**: dùng `asyncio.Semaphore(5)` để tránh gửi quá nhiều request cùng lúc, giảm nguy cơ rate limit.
- **Retrieval Metrics**: lấy `retrieved_ids` từ Agent và so sánh với `expected_retrieval_ids` để tính `hit_rate` và `mrr`.
- **Multi-Judge Evaluation**: gọi `llm_judge.evaluate_multi_judge()` để đánh giá chất lượng câu trả lời cuối cùng.
- **Latency Tracking**: dùng `time.perf_counter()` để đo thời gian xử lý từng test case.
- **Structured Output**: kết quả trả về có đủ `question`, `agent_answer`, `expected_answer`, `retrieval`, `judge`, `latency`, `retrieved_ids`, giúp nhóm dễ debug và viết failure analysis.

**Bằng chứng Git commit:** `aedce98 runner` - Author: Quynh Luu.

---

### B. Technical Depth

- **MRR**: Mean Reciprocal Rank đo vị trí đầu tiên mà tài liệu đúng xuất hiện trong danh sách retrieval. Nếu tài liệu đúng đứng đầu thì MRR = 1.0, đứng thứ hai thì MRR = 0.5, không tìm thấy thì bằng 0.

- **Cohen's Kappa**: là chỉ số đo độ đồng thuận giữa các judge, có tính đến khả năng đồng thuận ngẫu nhiên. Trong project hiện tại dùng `agreement_rate`; nếu nâng cấp có thể dùng Kappa để đánh giá độ tin cậy chặt chẽ hơn.

- **Position Bias**: là hiện tượng LLM Judge thiên vị câu trả lời ở vị trí A/B. Runner được tách riêng khỏi logic judge nên sau này có thể thêm bước đảo vị trí câu trả lời để kiểm tra bias.

- **Trade-off Cost vs Quality**: Multi-Judge giúp đánh giá khách quan hơn nhưng tốn chi phí và latency hơn. Vì vậy tôi dùng async để giảm thời gian chạy, semaphore để kiểm soát request, và chỉ dùng LLM Judge cho phần đánh giá ngữ nghĩa; còn Hit Rate/MRR được tính bằng code để tiết kiệm chi phí.

---

### C. Problem Solving

- **Benchmark chậm**: giải quyết bằng async runner để chạy nhiều test case song song.
- **Nguy cơ rate limit**: giải quyết bằng `Semaphore(5)` để giới hạn request đồng thời.
- **Khó xác định lỗi nằm ở đâu**: Runner trả về cả retrieval metrics và judge result, nhờ đó phân biệt được lỗi do retrieval hay generation.
- **Một test case lỗi có thể làm dừng toàn bộ benchmark**: thêm `try-except` để case lỗi trả về `error` thay vì làm dừng cả hệ thống.

---

## 3. Kết quả Benchmark

Dựa trên `reports/summary.json`:

- **Total test cases:** 50
- **Avg Latency:** 0.108s/test case
- **Hit Rate:** 44%
- **Avg MRR:** 44%
- **Avg Score:** 1.80 / 5.0
- **Agreement Rate:** 91%

Kết quả cho thấy Runner đã thu thập đủ các chỉ số quan trọng để nhóm tiếp tục phân tích lỗi và tối ưu Agent.
