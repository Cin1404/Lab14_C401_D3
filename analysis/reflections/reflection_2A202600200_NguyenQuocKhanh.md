# BÁO CÁO CÁ NHÂN - TỐI ƯU HÓA LLM AGENT BENCHMARK (LAB 14)

**Họ và tên:** Nguyễn Quốc Khánh  
**MSSV:** 2A202600200

---

## 1. Bảng Tiêu chí Đánh giá (Rubric)

| Hạng mục                     | Tiêu chí                                                                                                       | Điểm |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------- | ---- |
| **Engineering Contribution** | - Đóng góp cụ thể vào pipeline tổng hợp và xuất kết quả Benchmark (Reports). - Chứng minh qua giải trình kỹ thuật. | 15   |
| **Technical Depth**          | - Giải thích được các chỉ số: Hit Rate, MRR, Avg Score, Agreement Rate. - Phân tích được sự chênh lệch giữa kết quả kỳ vọng và thực tế.    | 15   |
| **Problem Solving**          | - Cách xử lý dữ liệu thô từ pipeline để tạo ra các file báo cáo có cấu trúc. - Xác định và ghi lại các trường hợp thất bại (Retrieval Failures).                                        | 10   |

---

## 2. Chi tiết Đóng góp Kỹ thuật

Tôi chịu trách nhiệm chính trong việc hoàn thiện toàn bộ các file đầu ra trong thư mục `reports/`, bao gồm việc tổng hợp số liệu, chuẩn hóa định dạng JSON và đảm bảo tính nhất quán của dữ liệu xuyên suốt pipeline đánh giá.

### A. Engineering Contribution (Đóng góp Kỹ thuật)

Tôi đã trực tiếp xây dựng và hoàn thiện 4 file báo cáo cốt lõi:

- **`summary.json` (Báo cáo tổng hợp):** Tổng hợp toàn bộ chỉ số từ 50 test case thành một bản tóm tắt duy nhất, bao gồm: `avg_latency` (~0.107s/request), `hit_rate` (0.44), `avg_mrr` (0.44), `avg_score` (1.8/5.0) và `agreement_rate` (0.91). File này đóng vai trò là "bảng điều khiển" duy nhất để nhóm nắm bắt toàn cảnh hiệu suất của Agent phiên bản V1.

- **`benchmark_results.json` (Kết quả chi tiết từng case):** Chuẩn hóa và lưu trữ toàn bộ 50 cặp câu hỏi – câu trả lời, kèm theo điểm số từ hai Judge (`strict_judge`, `helpful_judge`), `agreement_rate`, `latency` và kết quả retrieval (các `retrieved_ids` vs `expected_retrieval_ids`). File này là nguồn dữ liệu gốc cho mọi phân tích sâu hơn.

- **`retrieval_failures.json` (Danh sách thất bại retrieval):** Lọc và xuất riêng 22 test case có `hit_rate == 0.0`, tức là Agent đã truy xuất sai tài liệu (`doc_easy` thay vì `doc_hard` hoặc `doc_adversarial`). File này cung cấp dữ liệu đầu vào trực tiếp cho bước Failure Analysis của nhóm.

- **`results_detail.json` (Kết quả phân tầng):** Hoàn thiện file báo cáo chi tiết phân tầng theo loại câu hỏi, giúp nhóm nhận diện rằng các câu hỏi thuộc loại `doc_hard` và `doc_adversarial` là điểm yếu chính của Agent V1 hiện tại.

### B. Technical Depth (Chiều sâu Kỹ thuật)

- **Phân tích Hit Rate và MRR:** Kết quả `hit_rate = 0.44` và `avg_mrr = 0.44` cho thấy Agent V1 chỉ truy xuất đúng tài liệu trong 22/50 trường hợp. Thông qua việc đối chiếu `retrieved_ids` và `expected_retrieval_ids` trong từng record, tôi xác định được pattern: Agent luôn ưu tiên `doc_easy`, bỏ sót hoàn toàn `doc_hard` và `doc_adversarial` – đây là biểu hiện điển hình của lỗi **Semantic Routing** khi embedding space không phân biệt được độ phức tạp của tài liệu.

- **Phân tích Avg Score và Agreement Rate:** Điểm trung bình `1.8/5.0` thấp phản ánh trực tiếp chất lượng câu trả lời còn là placeholder `[Câu trả lời mẫu]`. Tuy nhiên, `agreement_rate = 0.91` (91%) giữa Strict Judge và Helpful Judge là tín hiệu tích cực, cho thấy hệ thống đánh giá Multi-Judge hoạt động nhất quán và đáng tin cậy, bất kể chất lượng câu trả lời của Agent.

### C. Problem Solving (Giải quyết vấn đề)

- **Vấn đề:** Dữ liệu đầu ra từ pipeline Benchmark ở dạng thô, thiếu phân tầng, khó đọc và không thể dùng trực tiếp để viết báo cáo nhóm.
- **Giải pháp:** Tôi thiết kế schema JSON thống nhất cho cả 4 file output, đảm bảo mỗi field đều có kiểu dữ liệu xác định (số thực, chuỗi, mảng). Đặc biệt, tôi xây dựng logic lọc tự động cho `retrieval_failures.json`: chỉ ghi nhận các case mà `retrieval.hit_rate == 0.0`, giúp nhóm tiết kiệm thời gian phân tích thủ công và tập trung vào đúng 22 case bị lỗi nghiêm trọng nhất.

---

## 3. Kết quả đóng góp vào Benchmark Nhóm

Dựa trên kết quả thực tế tại các file `reports/`:

- **Tính minh bạch dữ liệu:** Toàn bộ 50 test case được ghi lại đầy đủ, không mất dữ liệu, với trung bình độ trễ chỉ **~107ms/request** – phản ánh pipeline hoạt động ổn định.
- **Cơ sở cho Failure Analysis:** File `retrieval_failures.json` do tôi tổng hợp đã trực tiếp chỉ ra **22 case thất bại hoàn toàn**, trong đó 100% đều do Agent truy xuất nhầm sang `doc_easy`, cho phép nhóm xây dựng kế hoạch cải tiến Metadata Filtering và Semantic Routing chính xác.
- **Hỗ trợ quyết định phiên bản:** Báo cáo `summary.json` với `avg_score = 1.8` và `hit_rate = 0.44` cung cấp ngưỡng định lượng rõ ràng để nhóm xác nhận Agent V1 cần được nâng cấp lên V2, đặt nền tảng cho roadmap cải tiến tiếp theo.

---
