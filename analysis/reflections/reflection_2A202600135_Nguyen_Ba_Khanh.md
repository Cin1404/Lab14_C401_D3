# BÁO CÁO CÁ NHÂN - TỐI ƯU HÓA LLM AGENT BENCHMARK
**Họ và tên:** Nguyễn Bá Khánh  
**MSSV:** 2A202600135  

---

## 1. Bảng Tiêu chí Đánh giá (Rubric)

| Hạng mục | Tiêu chí | Điểm |
| :--- | :--- | :---: |
| **Engineering Contribution** | - Đóng góp cụ thể vào các module phức tạp (Async, Multi-Judge, Metrics).<br>- Chứng minh qua Git commits và giải trình kỹ thuật. | 15 |
| **Technical Depth** | - Giải thích được các khái niệm: MRR, Cohen's Kappa, Position Bias.<br>- Hiểu về trade-off giữa Chi phí và Chất lượng. | 15 |
| **Problem Solving** | - Cách giải quyết các vấn đề phát sinh trong quá trình code hệ thống phức tạp. | 10 |

---

## 2. Phần làm `llm_judge_2.py`
**`llm_judge_2.py`** - bộ máy đánh giá AI đa chiều. Dưới đây là giải trình chi tiết cho các hạng mục đóng góp:

### A. Engineering Contribution (Đóng góp Kỹ thuật)
Tôi đã xây dựng Module `llm_judge_2.py` với các tính năng:

- **Cost Calculation System**: Tôi đã trực tiếp triển khai hàm tính toán chi phí (Cost estimation) dựa trên lượng Token thực tế tiêu thụ (Input/Output tokens) từ mô hình `gpt-4o-mini`, với tỷ giá thực tế $0.15/1M input và $0.60/1M output. Mỗi lượt chấm điểm hiện đều trả về trường `usage_cost`.

- **JSON Structured Output**: Ép buộc mô hình trả về kết quả theo cấu trúc JSON định sẵn thông qua `response_format={"type": "json_object"}`, giúp việc tích hợp vào hệ thống báo cáo `summary.json` cực kỳ ổn định.


### B
**Trade-off Cost vs Quality**: Tôi đã thực hiện tối ưu hóa chi phí bằng cách cấu hình mô hình `gpt-4o-mini` cho các tác vụ chấm điểm cơ bản, vì qua thực nghiệm của tôi, chất lượng chấm điểm của nó tương đương `gpt-4` nhưng rẻ hơn 20 lần nếu có Rubric tốt.

### C. Problem Solving (Giải quyết vấn đề)
- **Problem**: Ban đầu, các LLM Judge thường trả về định dạng text không thống nhất, gây lỗi khi phân tích dữ liệu (Parsing error).
- **Solution**: Tôi đã giải quyết bằng cách áp dụng **System Prompt Engineering** kết hợp với **JSON Schema**, đồng thời thêm các khối `try-except` bọc quanh quá trình gọi API để đảm bảo Benchmark không bị dừng lại khi gặp lỗi lẻ (Graceful degradation).

---

## 3. Kết quả Benchmark Thực tế
- **Tỉ lệ Pass/Fail:** 44/6 (88% Pass)
- **Faithfulness:** 99.60% (Độ trung thực cao) | **Relevancy:** 99.40% (Độ liên quan cao)
- **Avg Score:** 4.45 / 5.0
