# BÁO CÁO CÁ NHÂN - LLM AGENT BENCHMARK
**Họ và tên:** Nguyễn Phương Nam  
**MSSV:** 2A202600194 

---

## 1. Bảng Tiêu chí Đánh giá

| Hạng mục | Tiêu chí | Điểm |
| :--- | :--- | :---: |
| **Engineering Contribution** | Đóng góp vào module phân tích lỗi và hỗ trợ debugging hệ thống benchmark | 15 |
| **Technical Depth** | Hiểu rõ Retrieval Metrics (Hit Rate, MRR) và vai trò của failure analysis. | 15 |
| **Problem Solving** | Giải quyết vấn đề xác định nguyên nhân lỗi trong pipeline RAG. | 10 |

---

## 2. Phần làm `export_failures.py`

Tôi phụ trách module **`export_failures.py`**, có nhiệm vụ phân tích và trích xuất các trường hợp Retrieval bị lỗi từ kết quả benchmark. Module này đóng vai trò quan trọng trong giai đoạn **`Failure Analysis`**, giúp nhóm nhanh chóng xác định các test case mà hệ thống Retrieval hoạt động không hiệu quả.

### A. Engineering Contribution

Trong `export_failures.py`, tôi đã triển khai các chức năng chính:

- **Đọc dữ liệu benchmark**: load file `results_detail.json`, chứa toàn bộ kết quả chi tiết của các test case.
- **Lọc retrieval failures**: xác định các trường hợp có `hit_rate == 0`, tức là hệ thống không retrieve được tài liệu đúng.
- **Xuất file riêng**: lưu các failure vào `retrieval_failures.json` để phục vụ phân tích sâu hơn.
- **Xử lý lỗi cơ bản**: kiểm tra sự tồn tại của file input để tránh crash khi chạy script.
- **Structured Filtering**: sử dụng `.get()` để tránh lỗi khi thiếu field trong JSON.

**Ý nghĩa trong hệ thống:**

- Giúp tách riêng lỗi Retrieval khỏi lỗi Generation.
- Hỗ trợ các thành viên khác (Retrieval Owner, Prompt Engineer) debug nhanh hơn.
- Là bước đầu để cải thiện chunking, embedding, hoặc query rewriting.

---

### B. Technical Depth

- **Hit Rate**: là tỷ lệ test case mà hệ thống retrieve được ít nhất một tài liệu đúng. Khi `hit_rate = 0`, nghĩa là Retrieval hoàn toàn thất bại.
- **MRR (Mean Reciprocal Rank)**: đo vị trí tài liệu đúng đầu tiên. Tuy nhiên trong module này, tôi tập trung vào các case cực đoan nhất (`MRR = 0`), vì đây là các lỗi nghiêm trọng cần ưu tiên xử lý.

**Failure Analysis trong RAG:**

- Nếu Retrieval fail → lỗi nằm ở embedding / search / chunking.
- Nếu Retrieval đúng nhưng answer sai → lỗi nằm ở LLM generation.

Script của tôi giúp phân tách rõ 2 loại lỗi này.

**Design Choice:**

- Không filter theo threshold (ví dụ `hit_rate < 0.5`) mà chỉ lấy `== 0` để tập trung vào lỗi nghiêm trọng nhất.
- Xuất JSON thay vì CSV để giữ nguyên cấu trúc nested (retrieval, judge, metadata).

---

### C. Problem Solving

Trong quá trình làm, tôi gặp và giải quyết các vấn đề sau:

- **Khó debug lỗi toàn hệ thống**: giải quyết bằng cách tách riêng các test case Retrieval fail ra file riêng.
- **Dữ liệu benchmark lớn và khó đọc**: xuất ra file JSON riêng giúp dễ inspect từng case.
- **Không rõ lỗi do Retrieval hay Generation**: dựa vào `hit_rate == 0` để xác định chắc chắn lỗi nằm ở Retrieval.
- **Thiếu tool hỗ trợ phân tích lỗi**: script này đóng vai trò như một công cụ nội bộ giúp nhóm phân tích nhanh hơn thay vì đọc thủ công.

---

## 3. Kết quả Benchmark & Ứng dụng

Sau khi chạy script trên file `results_detail.json`, tôi thu được:

- Danh sách các test case Retrieval thất bại hoàn toàn.
- **File output**: `reports/retrieval_failures.json`.

**Ứng dụng thực tế:**

- Phân tích các câu hỏi mà hệ thống không tìm được context phù hợp.
- Phát hiện vấn đề trong:
  - Chunking (chia đoạn chưa hợp lý).
  - Embedding (semantic chưa tốt).
  - Query (user question chưa được rewrite tốt).
- Là input cho bước cải thiện hệ thống RAG.

---

## 4. Kết luận

Module `export_failures.py` tuy nhỏ nhưng đóng vai trò quan trọng trong pipeline benchmark:

- Giúp tăng tốc debugging.
- Hỗ trợ failure analysis có hệ thống.
- Tạo nền tảng cho việc tối ưu Retrieval.

Đây là một bước cần thiết để chuyển từ việc “đo lường” sang “cải thiện” hệ thống LLM Agent.
