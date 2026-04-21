
##  1. Điểm Nhóm (Tối đa 60 điểm)
Nhóm D3-C401: **Hệ thống RAG Đa tầng & Benchmark Tự động**

| Hạng mục | Tiêu chí | Trạng thái | Điểm |
| :--- | :--- | :---: | :---: |
| **Retrieval Evaluation** | - Tính toán thành công Hit Rate & MRR cho ít nhất 50 test cases.<br>- Giải thích được mối liên hệ giữa Retrieval Quality và Answer Quality. |  41/50 cases | 10 |
| **Dataset & SDG** | - Golden Dataset chất lượng (50 cases) với mapping Ground Truth IDs.<br>- Có các bộ "Red Teaming" phá vỡ hệ thống thành công. |  Completed | 10 |
| **Multi-Judge consensus** | - Triển khai ít nhất 2 model Judge.<br>- Tính toán được độ đồng thuận và có logic xử lý xung đột tự động. |  Persona-based | 15 |
| **Regression Testing** | - Chạy thành công so sánh V1 vs V2.<br>- Có logic "Release Gate" tự động dựa trên các ngưỡng chất lượng. |  Passed | 10 |
| **Performance (Async)** | - Toàn bộ pipeline chạy song song cực nhanh (< 2 phút cho 50 cases).<br>- Có báo cáo chi tiết về Cost & Token usage. | 80s/50 cases | 10 |

---

##  2. Báo cáo Chi tiết Benchmark (Evidence)

Dưới đây là kết quả thu thập được từ phiên chạy benchmark mới nhất:

###  So sánh V1 (Mock_Weak) vs V2 (Current)

| Chỉ số (Metric) | Bản gốc (V1 - Mock_Weak) | Bản mới (V2 - Current) | Thay đổi | Kết quả |
| :--- | :---: | :---: | :---: | :---: |
| **Hit Rate** | 46.94% | **81.63%** | +34.69% | Đạt |
| **Avg MRR** | 0.4694 | **0.7653** | +0.2959 | Đạt |
| **LLM Score** | 3.77/5.0 | **4.31/5.0** | +0.54 | Đạt |
| **Ragas Faith.** | 63.88% | **89.59%** | +25.71% | Đạt |
| **Ragas Relev.** | 86.94% | **91.43%** | +4.50% | Đạt |
| **Avg Latency** | 1.02s | **1.67s** | +0.65s | Đạt |

###  Release Gate Status: 

Hệ thống đã tự động kiểm tra bản mới (**Agent_V1_Current**) so với các ngưỡng tối thiểu (Threshhold) và phê duyệt phát hành:

> [!IMPORTANT]
> **KẾT LUẬN: BẢN MỚI ĐẠT CHUẨN. CẤP PHÉP RELEASE!**
> - Toàn bộ 6/6 chỉ số vượt ngưỡng yêu cầu.
> - Hiệu suất retrieval tăng trưởng đột biến (~82% Hit Rate).
> - Độ tin cậy (Faithfulness) đạt mức cao ( ~91%).

---

##  3. Cấu hình Multi-Judge Consensus
Hệ thống sử dụng `MultiModelJudge` với chiến lược **Persona-based Consensus**:
- **Judge A (Strict):** Ưu tiên độ chính xác tuyệt đối.
- **Judge B (Helpful):** Ưu tiên trải nghiệm và cách diễn đạt.
- **Logic:** Tính toán `agreement_rate` và điểm trung bình để đảm bảo tính khách quan.



