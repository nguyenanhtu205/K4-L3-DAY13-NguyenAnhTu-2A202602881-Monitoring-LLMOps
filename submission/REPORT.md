# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:**
- **MSSV:**
- **Lớp:** K4-L3A
- **Repository URL:**
- **Commit SHA cuối:**
- **Challenge ID:**
- **Tên project Langfuse cá nhân:** `day13-k4-l3a-<MSSV>`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

> CP0 baseline (2026-09-29): API `/health` trả `ok: true` và `tracing_enabled: true`; load test hoàn thành 10 request, tất cả HTTP 200; log validator `30/100` (61 records, 60 thiếu trường bắt buộc/enrichment, 0 correlation ID duy nhất, 0 PII leak); dashboard validator `6/6`; pytest `22 passed`; ảnh Langfuse xác nhận 10 root traces trong project `day13-k4-l3a-2A202602881`. Điểm log thấp là baseline trước CP1 và được hướng dẫn là bình thường.

| Evidence | Đường dẫn |
|---|---|
| API health CP0 | `evidence/00-health.png` |
| Load test CP0 | `evidence/00-load-test.png` |
| Pytest CP0 / CP1 | `evidence/01-pytest.png`; `evidence/01-pytest-cp1.txt` |
| Log validator CP0 / CP1 | `evidence/02-log-validator.png`; `evidence/02-log-validator-cp1.txt` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log CP1 | `evidence/04-structured-log.txt` |
| PII redaction CP1 | `evidence/05-pii-redaction.txt` |
| Trace list CP0 | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100; 61 records, 60 thiếu required fields/enrichment, 0 unique correlation IDs | | Baseline trước CP1; PII scrubber pass |
| `validate_dashboard.py` | 6/6 panel hợp lệ | | Baseline |
| `pytest` | 22 passed | | Baseline |
| Số traces hợp lệ | 10 root traces hiển thị trong project cá nhân | | Ảnh trace list xác nhận; chưa xác minh span tree ở CP0 |
| Số PII leak | 0 phát hiện trong 21 records | | Kết quả baseline validator |
| Latency P95 / TTFT P95 | | | |
| Retrieval success rate | | | |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Middleware xóa context cũ mỗi request; nhận `x-request-id` nếu khớp `req-<8-hex>`, nếu không thì sinh ID mới; bind vào structlog và trả lại qua `x-request-id` cùng `x-response-time-ms`.
- **Các metadata được ghi vào structured log:** `user_id_hash`, `session_id`, `feature`, `model`, `env` và `correlation_id` được bind trước `request_received`.
- **Cách bảo đảm PII được scrub trước khi ghi:** `scrub_event` duyệt chuỗi ở mọi trường/nesting trước JSON renderer và file writer; mẫu được kiểm tra gồm email, điện thoại Việt Nam, CCCD và thẻ.
- **Cách kiểm chứng kết quả:** CP0 baseline đạt 30/100; sau CP1, `validate_logs.py` đạt 100/100 trên 29 records, 14 correlation IDs, 0 thiếu trường/enrichment và 0 PII leak; `pytest` đạt 26 passed. Output và log mẫu nằm trong Evidence index.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:**
- **Cấu trúc root/retrieval/generation observations:**
- **Cách nối trace với log:**
- **Prompt name:**
- **Version/label baseline:**
- **Version/label candidate:**
- **Trace ID của mỗi version:**
- **Cách promote và rollback `production`:**

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:**
- **SLO và lý do chọn:**
- **Cách tính error budget:**
- **Ba alert và runbook tương ứng:**

## 7. Điều tra challenge

- **Challenge ID:**
- **Khoảng thời gian điều tra:**
- **Triệu chứng từ metrics:**
- **Log line và correlation ID liên quan:**
- **Trace ID và span gây ảnh hưởng:**
- **Root cause:**
- **Fix action:**
- **Preventive measure:**

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:**
- **Một lỗi/blocker đã gặp:**
- **Cách tìm nguyên nhân và xử lý:**
- **Cách hiểu luồng Metrics → Logs → Traces:**
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:**
- **Điều quan trọng nhất đã học:**
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:**

## 9. Checklist trước khi nộp

- [ ] Kết quả và evidence thuộc commit SHA cuối.
- [ ] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [ ] Incident evidence nối đúng metric → log → trace.
- [ ] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [ ] Repository chạy lại được theo README.
- [ ] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [ ] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
