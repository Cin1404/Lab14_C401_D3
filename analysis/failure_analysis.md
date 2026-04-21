# Báo cáo Phân tích Thất bại (Failure Analysis)

**Phiên bản Agent:** `Agent_V1_Current`  
**Ngày đánh giá:** 21/04/2026  
**Người đánh giá:** AI Auditor

---

## 📊 1. Tổng quan Chỉ số (Executive Summary)

| Chỉ số | Kết quả | Đánh giá | Ý nghĩa |
| :--- | :--- | :--- | :--- |
| **Avg Judge Score** | **1.70 / 5.0** | 🔴 **THẤT BẠI** | Câu trả lời không có nội dung thực tế. |
| **Avg Hit Rate** | **48.00%** | 🟠 **TRUNG BÌNH YẾU** | Hệ thống tìm kiếm chỉ đúng gần một nửa số case. |
| **Avg MRR** | **0.48** | 🟠 **TRUNG BÌNH YẾU** | Tài liệu đúng thường không nằm ở vị trí đầu. |
| **Avg Latency** | **0.11s** | 🟢 **RẤT NHANH** | Tốc độ cao nhưng do không xử lý thật. |

---

## 🔍 2. Phân tích Nguyên nhân Gốc rễ (Root Cause Analysis)

Dựa trên dữ liệu chi tiết từ `results_detail.json`, chúng ta xác định được 2 nguyên nhân cốt lõi gây ra điểm số thấp kỷ lục này:

### A. Lỗi Generation: "Mắc kẹt trong Placeholder" (Critical Fail)
- **Hiện tượng:** 100% câu trả lời của Agent đều có dạng: `Dựa trên tài liệu hệ thống... [Câu trả lời mẫu].`
- **Nguyên nhân:** File `agent/main_agent.py` hiện tại là một **MOCK AGENT**. Nó không thực sự gọi LLM hay xử lý Context, dẫn đến việc các Judge (GPT-4o-mini) trừ điểm nặng vì "thông tin không rõ ràng" và "sai lệch với Ground Truth".
- **Hành động:** Cần thay thế logic Mock bằng logic RAG thực tế (gọi OpenAI/Gemini).

### B. Lỗi Retrieval: "Cố định kết quả tìm kiếm"
- **Hiện tượng:** Hit Rate dừng lại ở mức 48%. Các câu hỏi loại `EASY` thường qua, nhưng `HARD` và `ADVERSARIAL` thì fail hoàn toàn.
- **Nguyên nhân:** Agent đang giả lập trả về `retrieved_ids = ["doc_easy"]`. Khi gặp các câu hỏi yêu cầu tài liệu `doc_hard` hoặc tài liệu khác, hệ thống tìm kiếm (giả lập) không trả về đúng ID yêu cầu.
- **Hành động:** Kết nối với Vector Database (ChromaDB) thật để thực hiện tìm kiếm ngữ nghĩa.

---

## 🛠️ 3. Đề xuất cải tiến (Action Plan)

1.  **Tích hợp RAG thực tế**: Đưa `rag_system.py` từ dự án `A20-App-041` vào để thay thế phần Mock trong `MainAgent`.
2.  **Cấu hình Multi-Judge**: Tận dụng bộ máy `llm_judge.py` vừa refactor sang OpenAI để bắt đầu đo lường sự đồng thuận (Agreement Rate) thật sự giữa các Judge khắt khe và các Judge tập trung vào UI/UX.
3.  **Tối ưu Prompt**: Sau khi có điểm thật, tiến hành phân tích "5 Whys" trên những case đạt điểm dưới 3 để chỉnh sửa Prompt của Agent.

---

## ⚖️ 4. Kết luận
**QUYẾT ĐỊNH: BLOCK RELEASE**

Bản Agent hiện tại chỉ là khung mã nguồn (Boilerplate). Hệ thống Evaluation đã làm rất tốt nhiệm vụ của nó là **"Bóc trần sự thật"**: Agent chưa sẵn sàng để phục vụ người dùng.
