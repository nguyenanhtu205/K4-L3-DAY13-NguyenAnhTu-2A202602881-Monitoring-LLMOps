# Alerts và runbook

Ba alert gửi tới Slack `#llmops-alerts`; thời gian duy trì 5 phút giúp lọc spike ngắn. Điều kiện lấy từ `config/alert_rules.yaml` và guardrail/SLO trong `config/slo.yaml`.

## Alert 1

- **Tên:** User-visible latency elevated
- **Severity / duration:** warning / 5 phút
- **Kênh / owner:** Slack `#llmops-alerts` / LLM Platform on-call
- **SLI/SLO:** P95 latency ≤ 3000 ms trong SLO `fast_successful_requests`.
- **Điều kiện:** P95 `response_sent.latency_ms` > 3000 ms liên tục 5 phút.
- **Ảnh hưởng:** Người dùng phải chờ lâu hoặc request hết thời gian chờ.
- **Kiểm tra đầu tiên:** (1) xác nhận time range và P95/TTFT; (2) đối chiếu traffic, error rate và cost; (3) lấy `correlation_id` từ log request chậm rồi mở trace và so thời gian retrieval/generation.
- **Mitigation:** Nếu retrieval chiếm thời gian, giảm tải hoặc tạm giảm concurrency; nếu generation chậm, dùng prompt/model cấu hình ổn định gần nhất. Theo dõi P95 sau thay đổi.
- **Escalation:** Báo API on-call nếu kèm error rate tăng hoặc tiếp tục vượt ngưỡng sau mitigation.

## Alert 2

- **Tên:** Request failure rate elevated
- **Severity / duration:** critical / 5 phút
- **Kênh / owner:** Slack `#llmops-alerts` / API on-call
- **SLI/SLO:** Error rate tối đa 2%; lỗi cũng tiêu thụ error budget của SLO.
- **Điều kiện:** `request_failed / request_received` > 2% liên tục 5 phút.
- **Ảnh hưởng:** Một phần request không nhận được câu trả lời.
- **Kiểm tra đầu tiên:** (1) xác định `error_type` và mức tăng theo thời gian; (2) kiểm tra retrieval success và health/dependency; (3) nối log với trace bằng correlation ID để tìm observation lỗi.
- **Mitigation:** Tắt incident/feature gây lỗi nếu đã xác định, phục hồi dependency hoặc chuyển về cấu hình/model gần nhất đã hoạt động; giữ nguyên log và trace để hậu kiểm.
- **Escalation:** Gọi incident lead nếu error rate tiếp tục tăng hoặc lan rộng.

## Alert 3

- **Tên:** Retrieval success degraded
- **Severity / duration:** warning / 5 phút
- **Kênh / owner:** Slack `#llmops-alerts` / Retrieval on-call
- **SLI/SLO:** Retrieval success rate tối thiểu 90%.
- **Điều kiện:** Tỷ lệ `tool_success=true` trên retrieval calls < 90% liên tục 5 phút.
- **Ảnh hưởng:** Câu trả lời có thể thiếu tài liệu liên quan hoặc request thất bại.
- **Kiểm tra đầu tiên:** (1) xem breakdown lỗi `tool_name`/`error_type`; (2) kiểm tra log và trace của correlation ID lỗi; (3) xác nhận tình trạng index/vector store và thay đổi dữ liệu gần đây.
- **Mitigation:** Khôi phục index/dependency gần nhất còn tốt; nếu phù hợp, bật đường trả lời fallback và thông báo rõ giới hạn chất lượng.
- **Escalation:** Báo API on-call nếu retrieval lỗi làm error rate vượt 2%.
