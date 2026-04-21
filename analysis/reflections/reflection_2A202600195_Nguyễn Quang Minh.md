# BÁO CÁO CÁ NHÂN - TỐI ƯU HÓA LLM AGENT BENCHMARK (LAB 14)

**Họ và tên:** Nguyễn Quang Minh 
**MSSV:** 2A202600195

---

## 1. Bảng Tiêu chí Đánh giá (Rubric)


| Hạng mục                     | Tiêu chí                                                                                                       | Điểm |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------- | ---- |
| **Engineering Contribution** | - Đóng góp cụ thể vào các module phức tạp (Async, Multi-Judge, Metrics). - Chứng minh qua giải trình kỹ thuật. | 15   |
| **Technical Depth**          | - Giải thích được các khái niệm: MRR, Cost vs Quality Trade-off. - Hiểu về cơ chế Consensus và Calibration.    | 15   |
| **Problem Solving**          | - Cách giải quyết các vấn đề phát sinh (JSON Parsing, Cost Monitoring).                                        | 10   |


---

## 2. Chi tiết Đóng góp Kỹ thuật

Tôi chịu trách nhiệm chính trong việc xây dựng "hệ thống xương sống" cho việc đo lường và tối ưu hóa chi phí vận hành của hệ thống Benchmark.

### A. Engineering Contribution (Đóng góp Kỹ thuật)

Tôi đã trực tiếp xây dựng và refactor các module cốt lõi:

- **Multi-Judge Consensus Engine (`llm_judge_2.py`):** Triển khai cơ chế đánh giá đa nhân vật (Persona-based). Tôi đã thiết lập logic để tính toán `agreement_rate` (độ đồng thuận) giữa hai Judge (Strict vs Helpful), đảm bảo tính khách quan cho điểm số trung bình 4.31/5.0 của nhóm.
- **Real-time Cost Monitoring:** Tích hợp bộ đếm token và tính toán chi phí trực tiếp trên mỗi request (`usage_cost`). Điều này giúp nhóm kiểm soát ngân sách và đưa ra báo cáo chi tiết về "Giá tiền cho mỗi lần Eval" – một tiêu chí Expert trong Lab.
- **Async Agent Wrapper (`agent/main_agent.py`):** Cấu hình Agent chạy hoàn toàn bất đồng bộ. Đóng góp này giúp pipeline của nhóm đạt tốc độ ấn tượng: **80 giây cho 50 test cases**, vượt xa yêu cầu về hiệu suất.
- **Automated Failure Exporter (`scratch/export_failures_mock_lab8.py`):** Viết script tự động lọc các case có `hit_rate == 0`, cung cấp dữ liệu đầu vào cho bước phân tích "5 Whys" trong báo cáo thất bại của nhóm.

### B. Technical Depth (Chiều sâu Kỹ thuật)

- **Trade-off Chi phí và Chất lượng:** Tôi đã chứng minh rằng việc sử dụng `gpt-4o-mini` phối hợp với một Rubric chấm điểm chặt chẽ và cơ chế `json_object` có thể thay thế hoàn toàn các model đắt tiền hơn mà vẫn duy trì độ đồng thuận (Agreement Rate) lên tới 91%.
- **Khắc phục Position Bias:** Bằng cách tách biệt các Persona đánh giá, tôi giúp hệ thống giảm thiểu sự thiên vị trong việc chấm điểm, tập trung vào tính Faithfulness (Độ trung thực) đạt 89.59%.

### C. Problem Solving (Giải quyết vấn đề)

- **Vấn đề:** Các lỗi Parsing JSON thường xuyên xảy ra khi Judge trả về văn bản tự do.
- **Giải pháp:** Tôi đã áp dụng **JSON Enforcement** thông qua cấu hình `response_format` của OpenAI API kết hợp với kỹ thuật **Defensive Programming** (khối try-except), giúp hệ thống tự động hồi phục (Graceful degradation) và không bị ngắt quãng khi chạy 50 cases liên tục.

---

## 3. Kết quả đóng góp vào Benchmark Nhóm

Dựa trên kết quả thực tế tại `Group_report.md`:

- **Tốc độ xử lý:** Góp phần đạt 80s/50 cases nhờ tối ưu Async.
- **Độ tin cậy:** Hệ thống Multi-Judge do tôi thiết lập đã phê duyệt "Release" cho bản V2 với chỉ số Faithfulness tăng đột biến (+25.71%).
- **Phân tích lỗi:** Script export lỗi của tôi đã chỉ ra chính xác 4 case bị "Cross-document Contamination", giúp nhóm xây dựng kế hoạch cải tiến Metadata Filtering.

---

