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
| Dashboard validator | `evidence/03-dashboard-validator.png` (baseline); `evidence/03-dashboard-validator-cp2.png` (CP2) |
| Structured log CP1 | `evidence/04-structured-log.txt` |
| PII redaction CP1 | `evidence/05-pii-redaction.txt` |
| Trace list CP0 | `evidence/06-trace-list.png` |
| Trace list CP2 | `evidence/cp2-trace-list.png` |
| CP2 traces and tree validation (10 traces) | `evidence/cp2-generated-traces.csv`; `evidence/cp2-trace-validation.txt` |
| Trace waterfall screenshot | `evidence/07-trace-waterfall.png`; API verification: `evidence/cp2-trace-validation.txt` |
| Trace metadata | `evidence/08-trace-metadata.png`; API verification: `evidence/cp2-trace-validation.txt`; `evidence/cp2-prompt-versioning.txt` |
| Prompt versions and label runs | `evidence/09-prompt-versions.png`; `evidence/cp2-prompt-versioning.txt` |
| Prompt rollback | `evidence/10-prompt-rollback.png`; `evidence/cp2-prompt-versioning.txt` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` (full dashboard); split screenshots: `evidence/11-dashboard-overview-top.png`, `evidence/11-dashboard-overview-bottom.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100; 61 records, 60 thiếu required fields/enrichment, 0 unique correlation IDs | | Baseline trước CP1; PII scrubber pass |
| `validate_dashboard.py` | 6/6 panel hợp lệ | | Baseline |
| `pytest` | 22 passed | | Baseline |
| Số traces hợp lệ | 10 root traces hiển thị trong project cá nhân | 10 trace CP2 có root/retriever/generation hợp lệ | CP2 API verification: 10/10 cây span, metadata, prompt, usage/cost; input/output capture tắt |
| Số PII leak | 0 phát hiện trong 21 records | | Kết quả baseline validator |
| Latency P95 / TTFT P95 | | | |
| Retrieval success rate | | | |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Middleware xóa context cũ mỗi request; nhận `x-request-id` nếu khớp `req-<8-hex>`, nếu không thì sinh ID mới; bind vào structlog và trả lại qua `x-request-id` cùng `x-response-time-ms`.
- **Các metadata được ghi vào structured log:** `user_id_hash`, `session_id`, `feature`, `model`, `env` và `correlation_id` được bind trước `request_received`.
- **Cách bảo đảm PII được scrub trước khi ghi:** `scrub_event` duyệt chuỗi ở mọi trường/nesting trước JSON renderer và file writer; mẫu được kiểm tra gồm email, điện thoại Việt Nam, CCCD và thẻ.
- **Cách kiểm chứng kết quả:** CP0 baseline đạt 30/100; sau CP1, `validate_logs.py` đạt 100/100 trên 29 records, 14 correlation IDs, 0 thiếu trường/enrichment và 0 PII leak; `pytest` đạt 26 passed. Output và log mẫu nằm trong Evidence index.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Tự chạy `scripts/generate_traces.py` trong project `day13-k4-l3a-2A202602881`; API verification nằm tại `submission/evidence/cp2-trace-validation.txt`.
- **Cấu trúc root/retrieval/generation observations:** `lab-agent-run` là root; `document-retrieval` (retriever) và `fake-llm-generation` (generation) là child trực tiếp. Generation ghi model, prompt link, token usage và cost; các observation đều tắt input/output capture.
- **Cách nối trace với log:** Dùng cùng `correlation_id` trong metadata trace và structured log. Trace IDs/correlation IDs của 10 CP2 traces nằm trong CSV evidence.
- **Prompt name:** `day13-chat` (text prompt; giữ `Feature={{feature}}`, `Docs={{docs}}`, `Question={{message}}`).
- **Version/label baseline:** v1, labels `baseline` và `production` sau rollback.
- **Version/label candidate:** v2, label `candidate`; đã tạm chuyển `production` sang v2 rồi rollback về v1.
- **Trace ID của mỗi version:** baseline v1 `41225bd14f7ac91f2fc611e18c290023`; candidate v2 `8605981930a7213c874ecd8c3790f9c7`; production v2 sau promote `06dcbc7b5317bd7f93867015bc59a4f7`; production v1 sau rollback `c4a25d18217477ad7d4ab3e927605c1c`. Cả bốn cùng dùng input kiểm tra giống nhau.
- **Cách promote và rollback `production`:** Dùng `scripts/prompt_versions.py promote-v2`, xác nhận trace production version 2; sau đó `rollback-v1`, xác nhận label production trả về version 1. Evidence metadata: `submission/evidence/cp2-prompt-versioning.txt`.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Dashboard local đọc `data/logs.jsonl`, tự refresh 30 giây, cửa sổ 60 phút: latency P50/P95/P99 và TTFT P95; traffic; error breakdown/retrieval success; cost; tokens; quality proxy. Runtime screenshot: `submission/evidence/11-dashboard-overview.png`; chạy bằng `python scripts/dashboard.py --serve`.
- **SLO và lý do chọn:** `fast_successful_requests` yêu cầu 99.5% request thành công trong ≤3000 ms trên cửa sổ 28 ngày; baseline CP1 latency ứng dụng khoảng 2.2 giây nên còn headroom, cần xác nhận với workload dài hạn.
- **Cách tính error budget:** 100% − 99.5% = 0.5% request xấu; tương đương tối đa 50 request không đạt trên 10,000 request trong cửa sổ SLO.
- **Ba alert và runbook tương ứng:** P95 latency >3000 ms/5m (`docs/alerts.md#alert-1`); request failure rate >2%/5m (`#alert-2`); retrieval success <90%/5m (`#alert-3`). Cả ba gửi Slack `#llmops-alerts`, có severity và owner trong `config/alert_rules.yaml`.

> CP2 có API verification cho trace/prompt, screenshot dashboard runtime và các ảnh Langfuse cho waterfall, metadata, prompt versions/labels và trạng thái rollback `production`.

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3a-monitoring-llmops-v1` (K4; file challenge được giữ local và `.gitignore` bỏ qua).
- **Khoảng thời gian điều tra:** Dashboard 60 phút, `2026-09-29 10:12–11:12 UTC`; năm request challenge xảy ra `11:08:20.140–11:08:34.875 UTC`.
- **Triệu chứng từ metrics:** Panel latency hiển thị P95 `3568 ms` và P99 `3751 ms`, vượt threshold/SLO P95 `3000 ms`. Ảnh: `evidence/12-incident-metric.png`.
- **Log line và correlation ID liên quan:** Chọn `response_sent` cho `req-b5ce330e`, feature `monitoring`, `latency_ms=3797`, timestamp `2026-09-29T11:08:24.251658Z`; request nhận lúc `11:08:20.140571Z`. Ảnh: `evidence/13-incident-log.png`.
- **Trace ID và span gây ảnh hưởng:** Trace `a5beb1c14fd28ac81f51f1726634d221`, metadata cùng `correlation_id=req-b5ce330e`; root duration `3.80 s`, `document-retrieval` `2.50 s`, `fake-llm-generation` `0.15 s`. Retrieval là span chi phối latency. Ảnh: `evidence/14-incident-trace.png`.
- **Root cause:** Challenge bật `rag_slow`; retrieval giả lập chờ 2.5 giây. Trace cho thấy retrieval mất 2.50 giây, trong khi generation mất 0.15 giây, phù hợp với log latency 3.797 giây và P95 vượt ngưỡng.
- **Fix action:** Sau khi thu thập metric, log và trace, đã tắt incident qua `scripts/inject_incident.py --disable`; API xác nhận `rag_slow=false`, `tool_fail=false`, `cost_spike=false`.
- **Preventive measure:** Giữ SLO/alert P95 latency, theo dõi duration riêng của retrieval, đặt timeout cho retrieval và dùng circuit breaker/fallback để tránh một backend chậm kéo dài toàn request.
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




