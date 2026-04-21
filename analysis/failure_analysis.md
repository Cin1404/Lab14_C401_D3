# Báo cáo Phân tích Thất bại (Failure Analysis Report)

## 1. Tổng quan Benchmark
- **Tổng số cases:** 50
- **Tỉ lệ Pass/Fail:** 41/09 (82% Pass)
- **Điểm RAGAS trung bình:**
    - Faithfulness:  89.59%
    - Relevancy: 91.43%
- **Điểm LLM-Judge trung bình:** 4.31 / 5.0

## 2. Phân nhóm lỗi (Failure Clustering)
| Nhóm lỗi | Số lượng | Nguyên nhân dự kiến |
|----------|----------|---------------------|
| Retrieval Failure - Cross-document Contamination | 4 | Vector search lấy nhầm đoạn văn bản của tài liệu khác có cấu trúc tương tự (ví dụ: lấy ngày hiệu lực của Policy hoàn tiền thay vì Policy nghỉ phép). |
| Retrieval Failure - Missing Context | 3 | Không truy xuất được chunk ở phần giới thiệu của tài liệu (chunk 0) chứa các thông tin tổng quan, dẫn đến agent không có thông tin (vd: ngày ban hành, đối tượng). |
| Generation Failure - Semantic/Vocabulary Gap | 2 | Chunk lấy về chứa kết quả nhưng LLM không liên kết được từ vựng tiếng Việt với thuật ngữ chuyên môn (ví dụ không hiểu "hệ thống vé" tương đương với "Jira" / "Ticket"). |

## 3. Phân tích 5 Whys (Chọn 3 case tệ nhất)

### Case #1: Trả lời sai ngày hiệu lực do lấy nhầm Document
1. **Symptom:** Câu hỏi "Chính sách nghỉ phép có hiệu lực từ ngày nào?" nhưng Agent trả lời ngày "01/02/2026" (Đây là ngày ban hành của policy_refund_v4).
2. **Why 1:** Agent thấy mốc thời gian này trong context và tin rằng đó là câu trả lời.
3. **Why 2:** Vector DB đã truy xuất nhầm chunk từ tài liệu `policy_refund_v4` về hoàn tiền thay vì tài liệu `hr_leave_policy`.
4. **Why 3:** Hệ thống Vector Search gặp tình trạng "semantic confusion", đánh giá độ tương đồng của cụm "có hiệu lực từ ngày" mạnh hơn từ khoá "nghỉ phép".
5. **Why 4:** Câu hỏi quá ngắn, dẫn đến search query thiếu chiều sâu ngữ nghĩa.
6. **Root Cause:** Vector search bị nhầm lẫn ngữ nghĩa chéo giữa các documents (Cross-document contamination) và thiếu cơ chế Metadata filtering (xác định nguồn document liên quan trước).

### Case #2: Trả lời sai đối tượng áp dụng (Hallucination dựa trên Grounding sai)
1. **Symptom:** Câu hỏi "Ai có quyền truy cập vào tài liệu về chính sách nghỉ phép?", Agent trả lời "tất cả nhân viên, contractor, third-party vendor" (Sai hoàn toàn, đây là phạm vi của SOP).
2. **Why 1:** Agent đã đọc thông tin "Áp dụng cho tất cả nhân viên, contractor..." trong context cung cấp và tự tin trích xuất.
3. **Why 2:** Vector DB trả về chunk 1 của `access_control_sop` thay vì trang tổng quan `hr_leave_policy_0`.
4. **Why 3:** Cụm từ "quyền truy cập" được nhắc nhiều trong `access_control_sop`, làm cho chunk đó có điểm vector distance cao hơn chunk thực sự chứa đáp án.
5. **Why 4:** Nội dung các chunk thiếu thông tin định danh (Tên tài liệu gốc), khiến chunk đứng độc lập trở nên mập mờ ngữ nghĩa.
6. **Root Cause:** Dense Retrieval ưu tiên các từ khoá hành động (quyền truy cập) mạnh hơn thực thể (chính sách nghỉ phép), và chiến lược Chunking chưa chèn Document Title vào nội dung Chunk.

### Case #3: Không nhận diện được đáp án do Khoảng trống từ vựng (Semantic Gap)
1. **Symptom:** Câu hỏi "Hệ thống vé được sử dụng trong dự án nào?", Agent trả lời "Tôi không biết" dù điểm số đánh giá truy xuất các chunk liên quan có chứa keyword.
2. **Why 1:** LLM không nhận thấy các chuỗi tương đồng với "hệ thống vé" và "dự án" trực tiếp trong văn bản context.
3. **Why 2:** Văn bản context chứa "Jira: project IT-SUPPORT", nhưng LLM không map được cụm từ "hệ thống vé" sang "Jira" (Ticket system).
4. **Why 3:** Instruction prompt cho LLM quá nghiêm ngặt khi yêu cầu chỉ trả lời dựa vào văn bản, kết hợp việc thiếu năng lực ánh xạ thuật ngữ Tiếng Anh - Tiếng Việt.
5. **Why 4:** Query chưa được dịch/giải nghĩa các thuật ngữ IT sang đồng nghĩa hệ thống trước khi gửi.
6. **Root Cause:** Khoảng trống từ vựng (Vocabulary gap / Semantic mismatch) không được xử lý bằng Query Expansion, dẫn đến Generation Failure.

## 4. Kế hoạch cải tiến (Action Plan)
- [ ] **Metadata Filtering / Query Routing:** Thêm bước tiền xử lý để phân loại Intent/Topic câu hỏi và chỉ định tài liệu cần search.
- [ ] **Data Pipeline (Chunking):** Chèn động tên tài liệu và nội dung tóm tắt (Document Title + Summary) vào từng Chunk để giữ bối cảnh khi truy xuất độc lập.
- [ ] **Retrieval:** Tích hợp Reranking (Cross-Encoder) để đánh giá lại mức độ phù hợp giữa truy vấn gốc và chunk lấy về, loại bỏ False Positives nghiêm trọng.
- [ ] **Query Processing:** Áp dụng Query Expansion & Translation để dịch ngôn ngữ tự nhiên (Tiếng Việt) sang thuật ngữ hệ thống (Jira, Ticket, Remote, v.v.).
