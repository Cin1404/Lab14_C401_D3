# Reflection cá nhân - Lưu Thị Ngọc Quỳnh

## 1. Vai trò của em trong dự án

Trong Lab 14, em phụ trách chính phần `engine/runner.py`, tức module điều phối benchmark cho toàn bộ hệ thống đánh giá AI Agent. Đây là phần đứng giữa các thành phần khác nhau: Agent sinh câu trả lời, Retrieval Evaluator tính chất lượng truy xuất, và Multi-Judge đánh giá chất lượng câu trả lời cuối cùng.

Mục tiêu của em không chỉ là chạy từng test case, mà còn phải thiết kế một luồng đánh giá có thể mở rộng, chạy bất đồng bộ, ghi lại đủ thông tin để phân tích lỗi và phục vụ báo cáo sau benchmark.

## 2. Engineering Contribution

### Đóng góp chính trong Runner

Em xây dựng class `BenchmarkRunner` với ba trách nhiệm chính:

1. Nhận các dependency từ bên ngoài gồm `agent`, `retrieval_eval` và `llm_judge`.
2. Chạy một test case theo pipeline: Agent -> Retrieval Eval -> Multi-Judge.
3. Chạy toàn bộ dataset bằng async để benchmark nhanh hơn nhưng vẫn kiểm soát số request đồng thời.

Trong `run_single_test`, em triển khai luồng xử lý:

- Gọi `agent.query(question)` để lấy câu trả lời và metadata truy xuất.
- Đo `latency` bằng `time.perf_counter()` để có chỉ số hiệu năng.
- Lấy `retrieved_ids` từ metadata của Agent và so sánh với `expected_retrieval_ids`.
- Tính `hit_rate` và `mrr` thông qua `retrieval_eval`.
- Gọi `llm_judge.evaluate_multi_judge()` để đánh giá generation output.
- Trả về một object kết quả gồm câu hỏi, câu trả lời của agent, ground truth, latency, retrieval metrics, judge result và các ID phục vụ phân tích lỗi.

Trong `run_all`, em dùng `asyncio.as_completed()` kết hợp với `tqdm` để:

- Các test case được chạy bất đồng bộ thay vì tuần tự.
- Kết quả nào xong trước thì được thu thập trước, giúp tiết kiệm thời gian benchmark.
- Người chạy có progress bar để theo dõi tiến độ thực tế.

Ngoài ra, em thêm `asyncio.Semaphore(5)` để giới hạn tối đa 5 request đồng thời. Đây là điểm quan trọng vì benchmark AI thường dễ gặp rate limit hoặc tăng chi phí nếu gửi quá nhiều request cùng lúc.

### Bằng chứng qua Git commits

Commit chính thể hiện phần đóng góp của em:

- `aedce98 runner` - Author: Quynh Luu

Trong commit này, em chuyển Runner từ dạng chạy batch đơn giản sang kiến trúc rõ hơn:

- Tách evaluator thành `retrieval_eval` và `llm_judge`.
- Thêm semaphore để kiểm soát concurrency.
- Thêm pipeline đánh giá đầy đủ cho từng test case.
- Thêm output phục vụ báo cáo gồm `retrieval`, `judge`, `expected_retrieval_ids`, `retrieved_ids`.
- Thêm progress bar cho quá trình benchmark.

## 3. Technical Depth

### MRR

MRR là viết tắt của Mean Reciprocal Rank. Chỉ số này đo xem tài liệu đúng đầu tiên xuất hiện ở vị trí thứ mấy trong danh sách retrieved documents.

Công thức cho một test case là:

```text
MRR = 1 / rank
```

Nếu tài liệu đúng đứng đầu danh sách, MRR = 1.0. Nếu tài liệu đúng đứng thứ 2, MRR = 0.5. Nếu không tìm thấy tài liệu đúng, MRR = 0.

Trong Runner, em không chỉ kiểm tra câu trả lời cuối cùng hay hay dở, mà còn đưa `expected_retrieval_ids` và `retrieved_ids` vào `retrieval_eval.calculate_mrr()`. Điều này giúp biết lỗi đến từ retrieval hay từ generation. Nếu MRR thấp nhưng judge score cũng thấp, nguyên nhân có thể là Agent không nhận đúng context ngay từ đầu.

### Cohen's Kappa

Cohen's Kappa là chỉ số đo mức độ đồng thuận giữa hai judge nhưng có tính đến khả năng đồng thuận ngẫu nhiên. Công thức tổng quát là:

```text
kappa = (Po - Pe) / (1 - Pe)
```

Trong đó:

- `Po` là tỷ lệ đồng thuận quan sát được.
- `Pe` là tỷ lệ đồng thuận kỳ vọng nếu hai judge chọn ngẫu nhiên.

Trong dự án, phần Multi-Judge hiện trả về `agreement_rate`, là cách đo đồng thuận trực tiếp và dễ triển khai hơn. Tuy nhiên, nếu muốn đánh giá nghiêm túc hơn, Cohen's Kappa sẽ tốt hơn vì nó phân biệt được trường hợp hai judge thật sự nhất quán với trường hợp chỉ tình cờ cho cùng điểm.

### Position Bias

Position Bias là thiên lệch xảy ra khi judge ưu tiên câu trả lời ở một vị trí nhất định, ví dụ luôn thích response A hơn response B chỉ vì A được đặt trước. Đây là rủi ro thường gặp khi dùng LLM làm evaluator.

Runner của em được thiết kế để gọi judge qua một interface riêng (`llm_judge.evaluate_multi_judge`) thay vì viết logic judge trực tiếp trong Runner. Cách tách này giúp sau này có thể thêm bước kiểm tra position bias, ví dụ đảo thứ tự response A/B và so sánh điểm, mà không cần sửa lại toàn bộ benchmark pipeline.

### Trade-off giữa chi phí và chất lượng

Em nhận thấy benchmark bằng Multi-Judge cho chất lượng đánh giá khách quan hơn single judge, nhưng chi phí và latency cũng tăng lên. Vì vậy Runner cần chạy async để giảm thời gian chờ, nhưng vẫn phải có semaphore để không gửi request quá mức.

Trade-off em áp dụng trong phần Runner là:

- Chạy song song để tiết kiệm thời gian.
- Giới hạn concurrency ở mức 5 để tránh rate limit và kiểm soát chi phí.
- Tách retrieval eval ra khỏi LLM judge vì Hit Rate và MRR có thể tính bằng code, không cần gọi model.
- Chỉ dùng LLM judge cho phần cần đánh giá ngữ nghĩa của câu trả lời.

## 4. Problem Solving

### Vấn đề 1: Benchmark tuần tự chạy chậm

Nếu chạy từng test case tuần tự, thời gian benchmark sẽ tăng rất nhanh vì mỗi case đều phải chờ Agent và Judge. Em giải quyết bằng cách dùng `asyncio.as_completed()` để chạy nhiều test case cùng lúc và nhận kết quả ngay khi từng task hoàn thành.

### Vấn đề 2: Nguy cơ rate limit khi chạy async

Async giúp nhanh hơn, nhưng nếu tạo quá nhiều request cùng lúc thì dễ bị rate limit hoặc làm chi phí tăng khó kiểm soát. Vì vậy em thêm `asyncio.Semaphore(5)` để giới hạn số request đồng thời. Đây là cách cân bằng giữa tốc độ và độ ổn định.

### Vấn đề 3: Khó phân biệt lỗi Retrieval và lỗi Generation

Nếu chỉ nhìn judge score cuối cùng, nhóm sẽ không biết câu trả lời sai vì Agent không lấy đúng tài liệu hay vì LLM trả lời kém. Em giải quyết bằng cách để Runner trả về cả `retrieval` metrics lẫn `judge` result trong cùng một record.

Nhờ vậy, khi phân tích failure, nhóm có thể chia lỗi thành các nhóm rõ hơn:

- Retrieval sai: Hit Rate thấp, MRR thấp.
- Retrieval đúng nhưng generation sai: Hit Rate/MRR tốt nhưng judge score thấp.
- Judge chưa ổn định: agreement rate thấp giữa các judge.

### Vấn đề 4: Cần output đủ thông tin cho báo cáo

Runner không chỉ trả điểm tổng, mà còn giữ lại `question`, `agent_answer`, `expected_answer`, `latency`, `expected_retrieval_ids` và `retrieved_ids`. Việc giữ lại dữ liệu trung gian giúp nhóm có thể export report, debug từng case và viết failure analysis cụ thể hơn.

## 5. Bài học cá nhân

Qua phần Runner, em hiểu rõ hơn rằng một hệ thống evaluation tốt không chỉ là gọi model rồi lấy điểm. Nó cần một pipeline có khả năng quan sát được từng bước: truy xuất gì, trả lời gì, mất bao lâu, judge đồng thuận ra sao và lỗi xuất hiện ở tầng nào.

Em cũng học được rằng async programming rất hữu ích trong các hệ thống AI vì phần lớn thời gian là chờ network/model response. Tuy nhiên, async phải đi kèm giới hạn concurrency, logging và schema output rõ ràng thì mới dùng được trong thực tế.

Nếu phát triển tiếp, em muốn cải thiện Runner theo ba hướng:

1. Chuẩn hóa schema kết quả để các file report đọc cùng một format.
2. Thêm retry/backoff khi Agent hoặc Judge gặp lỗi tạm thời.
3. Bổ sung thống kê chi phí theo từng test case để nhóm đánh giá được cost/quality trade-off rõ hơn.

## 6. Tự đánh giá theo rubric cá nhân

| Hạng mục | Tự đánh giá |
| :--- | :--- |
| Engineering Contribution | Em đóng góp trực tiếp vào module Runner, là phần điều phối các module phức tạp như Async, Retrieval Metrics và Multi-Judge. Commit `aedce98` là bằng chứng chính cho phần này. |
| Technical Depth | Em hiểu và áp dụng được MRR trong retrieval evaluation, hiểu vai trò của agreement/Cohen's Kappa trong multi-judge, nhận diện được position bias và trade-off giữa chi phí với chất lượng. |
| Problem Solving | Em xử lý các vấn đề thực tế như benchmark chạy chậm, nguy cơ rate limit, khó phân tách lỗi retrieval/generation và nhu cầu lưu output đủ chi tiết cho failure analysis. |

## 7. Kết luận

Phần `Runner.py` giúp em thấy rõ vai trò của engineering trong AI evaluation: muốn đánh giá Agent tốt thì phải xây được một pipeline đo lường đáng tin cậy, có khả năng mở rộng và đủ dữ liệu để giải thích kết quả. Đây là phần em đóng góp chính trong dự án và cũng là phần giúp em hiểu sâu hơn về cách biến một hệ thống AI từ demo thành một quy trình kiểm thử có thể dùng được trong thực tế.
