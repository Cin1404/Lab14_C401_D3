# Báo cáo Phân tích Thất bại (Failure Analysis Report)

## 1. Tổng quan Benchmark
- **Tổng số cases:** 50
- **Tỉ lệ Pass/Fail:** 44/06 (88% Pass)
- **Điểm RAGAS trung bình:**
    - Faithfulness:  99.60%
    - Relevancy: 99.40%
- **Điểm LLM-Judge trung bình:** 4.45 / 5.0

## 2. Phân nhóm lỗi (Failure Clustering)
| Nhóm lỗi | Số lượng | Nguyên nhân dự kiến |
|----------|----------|---------------------|
| Hallucination | 6 |Keyword matching chưa bao phủ hết các biến thể câu hỏi khó (Dẫn đến nguy cơ Hallucination). |
| Incomplete | 6 |Agent tìm đúng tài liệu nhưng bỏ sót các chi tiết nhỏ hoặc do Prompt chưa yêu cầu trả lời sâu. |

## 3. Phân tích 5 Whys (Chọn 3 case tệ nhất)

### Case #1: [Mô tả ngắn]
1. **Symptom:** Agent trả lời sai về...
2. **Why 1:** LLM không thấy thông tin trong context.
3. **Why 2:** Vector DB không tìm thấy tài liệu liên quan nhất.
4. **Why 3:** Chunking size quá lớn làm loãng thông tin quan trọng.
5. **Why 4:** ...
6. **Root Cause:** Chiến lược Chunking không phù hợp với dữ liệu bảng biểu.

## 4. Kế hoạch cải tiến (Action Plan)
- [ ] Thay đổi Chunking strategy từ Fixed-size sang Semantic Chunking.
- [ ] Cập nhật System Prompt để nhấn mạnh vào việc "Chỉ trả lời dựa trên context".
- [ ] Thêm bước Reranking vào Pipeline.
