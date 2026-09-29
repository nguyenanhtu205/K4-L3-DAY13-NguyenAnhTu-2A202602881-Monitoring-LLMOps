# Báo cáo cá nhân — K4-L3A Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Nguyễn Anh Tú
- **MSSV:** 2A202602881
- **Lớp:** K4-L3A
- **Repository URL:** https://github.com/nguyenanhtu205/K4-L3-DAY13-NguyenAnhTu-2A202602881-Monitoring-LLMOps
- **Commit SHA cuối:**
- **Challenge ID:** day13-k4-l3a-monitoring-llmops-v1
- **Tên project Langfuse cá nhân:** `day13-k4-l3a-2A202602881`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

> CP0 baseline (2026-09-29): API `/health` trả `ok: true` và `tracing_enabled: true`; load test hoàn thành 10 request, tất cả HTTP 200; log validator `30/100` (61 records, 60 thiếu trường bắt buộc/enrichment, 0 correlation ID duy nhất, 0 PII leak); dashboard validator `6/6`; pytest `22 passed`; ảnh Langfuse xác nhận 10 root traces trong project `day13-k4-l3a-2A202602881`. Điểm log thấp là baseline trước CP1 và được hướng dẫn là bình thường.

| Evidence | Đường dẫn |
|---|---|
| API health CP0 | [00-health.png](evidence/00-health.png) |
| Load test CP0 | [00-load-test.png](evidence/00-load-test.png) |
| Pytest CP0 / CP1 / final | [01-pytest.png](evidence/01-pytest.png); [01-pytest-cp1.txt](evidence/01-pytest-cp1.txt); [01-pytest-final.txt](evidence/01-pytest-final.txt) |
| Log validator CP0 / CP1 / final | [02-log-validator.png](evidence/02-log-validator.png); [02-log-validator-cp1.txt](evidence/02-log-validator-cp1.txt); [02-log-validator-final.txt](evidence/02-log-validator-final.txt) |
| Dashboard validator | [03-dashboard-validator.png](evidence/03-dashboard-validator.png) (baseline); [03-dashboard-validator-cp2.png](evidence/03-dashboard-validator-cp2.png) (CP2); [03-dashboard-validator-final.txt](evidence/03-dashboard-validator-final.txt) |
| Structured log CP1 | [04-structured-log.txt](evidence/04-structured-log.txt) |
| PII redaction CP1 | [05-pii-redaction.txt](evidence/05-pii-redaction.txt) |
| Trace list CP0 | [06-trace-list.png](evidence/06-trace-list.png) |
| Trace list CP2 | [cp2-trace-list.png](evidence/cp2-trace-list.png) |
| CP2 traces and tree validation (10 traces) | [cp2-generated-traces.csv](evidence/cp2-generated-traces.csv); [cp2-trace-validation.txt](evidence/cp2-trace-validation.txt) |
| Trace waterfall screenshot | [07-trace-waterfall.png](evidence/07-trace-waterfall.png); API verification: [cp2-trace-validation.txt](evidence/cp2-trace-validation.txt) |
| Trace metadata | [08-trace-metadata.png](evidence/08-trace-metadata.png); API verification: [cp2-trace-validation.txt](evidence/cp2-trace-validation.txt); [cp2-prompt-versioning.txt](evidence/cp2-prompt-versioning.txt) |
| Prompt versions and label runs | [09-prompt-versions.png](evidence/09-prompt-versions.png); [cp2-prompt-versioning.txt](evidence/cp2-prompt-versioning.txt) |
| Prompt rollback | [10-prompt-rollback.png](evidence/10-prompt-rollback.png); [cp2-prompt-versioning.txt](evidence/cp2-prompt-versioning.txt) |
| Dashboard runtime | [11-dashboard-overview.png](evidence/11-dashboard-overview.png) (full dashboard); split screenshots: [11-dashboard-overview-top.png](evidence/11-dashboard-overview-top.png), [11-dashboard-overview-bottom.png](evidence/11-dashboard-overview-bottom.png) |
| Incident metric | [12-incident-metric.png](evidence/12-incident-metric.png) |
| Incident log | [13-incident-log.png](evidence/13-incident-log.png) |
| Incident trace | [14-incident-trace.png](evidence/14-incident-trace.png) |
| CP3 challenge load and incident cleanup | [cp3-load-test.txt](evidence/cp3-load-test.txt); [cp3-incident-control.txt](evidence/cp3-incident-control.txt) |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100; 61 records, 60 thiếu required fields/enrichment, 0 unique correlation IDs | 100/100; 42 records, 21 correlation IDs, 0 thiếu required fields/enrichment, 0 PII leak | Kiểm tra CP4; output: `evidence/02-log-validator-final.txt` |
| `validate_dashboard.py` | 6/6 panel hợp lệ | 6/6 panel hợp lệ | Kiểm tra CP4; output: `evidence/03-dashboard-validator-final.txt` |
| `pytest` | 22 passed | 26 passed in 1.56s | Kiểm tra CP4; output: `evidence/01-pytest-final.txt` |
| Số traces hợp lệ | 10 root traces hiển thị trong project cá nhân | 10 trace CP2 có root/retriever/generation hợp lệ | CP2 API verification: 10/10 cây span, metadata, prompt, usage/cost; input/output capture tắt |
| Số PII leak | 0 phát hiện trong 21 records | 0 trong 42 records ở lần validate CP4 | Challenge dùng query tổng hợp; không ghi PII thô |
| Latency P95 / TTFT P95 | | 3568 ms / 50 ms trong cửa sổ challenge 10:12–11:12 UTC | P95 vượt threshold 3000 ms; evidence `12-incident-metric.png` |
| Retrieval success rate | | 100% (5/5 challenge request thành công) | Output load test ghi nhận cả năm request HTTP 200; log mẫu tại `evidence/13-incident-log.png` xác nhận retrieval thành công cho request được điều tra |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Middleware xóa context cũ mỗi request; nhận `x-request-id` nếu khớp `req-<8-hex>`, nếu không thì sinh ID mới; bind vào structlog và trả lại qua `x-request-id` cùng `x-response-time-ms`.
- **Các metadata được ghi vào structured log:** `user_id_hash`, `session_id`, `feature`, `model`, `env` và `correlation_id` được bind trước `request_received`.
- **Cách bảo đảm PII được scrub trước khi ghi:** `scrub_event` duyệt chuỗi ở mọi trường/nesting trước JSON renderer và file writer; mẫu được kiểm tra gồm email, điện thoại Việt Nam, CCCD và thẻ.
- **Cách kiểm chứng kết quả:** CP0 baseline đạt 30/100; sau CP1, `validate_logs.py` đạt 100/100 trên 29 records, 14 correlation IDs, 0 thiếu trường/enrichment và 0 PII leak; `pytest` đạt 26 passed. Output và log mẫu nằm trong Evidence index.
- **Source:** [app/middleware.py](../app/middleware.py), [app/main.py](../app/main.py), [app/logging_config.py](../app/logging_config.py), [app/pii.py](../app/pii.py), [tests/test_pii.py](../tests/test_pii.py).

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Tự chạy [scripts/generate_traces.py](../scripts/generate_traces.py) trong project `day13-k4-l3a-2A202602881`; ảnh danh sách hiện tên project tại [cp2-trace-list.png](evidence/cp2-trace-list.png), API verification tại [cp2-trace-validation.txt](evidence/cp2-trace-validation.txt).
- **Cấu trúc root/retrieval/generation observations:** `lab-agent-run` là root; `document-retrieval` (retriever) và `fake-llm-generation` (generation) là child trực tiếp. Generation ghi model, prompt link, token usage và cost; các observation đều tắt input/output capture.
- **Cách nối trace với log:** Dùng cùng `correlation_id` trong metadata trace và structured log. Trace IDs/correlation IDs của 10 CP2 traces nằm trong CSV evidence.
- **Prompt name:** `day13-chat` (text prompt; giữ `Feature={{feature}}`, `Docs={{docs}}`, `Question={{message}}`).
- **Version/label baseline:** v1, labels `baseline` và `production` sau rollback.
- **Version/label candidate:** v2, label `candidate`; đã tạm chuyển `production` sang v2 rồi rollback về v1.
- **Trace ID của mỗi version:** baseline v1 `41225bd14f7ac91f2fc611e18c290023`; candidate v2 `8605981930a7213c874ecd8c3790f9c7`; production v2 sau promote `06dcbc7b5317bd7f93867015bc59a4f7`; production v1 sau rollback `c4a25d18217477ad7d4ab3e927605c1c`. Cả bốn cùng dùng input kiểm tra giống nhau.
- **Cách promote và rollback `production`:** Dùng [scripts/prompt_versions.py](../scripts/prompt_versions.py) với `promote-v2`, xác nhận trace production version 2; sau đó `rollback-v1`, xác nhận label production trả về version 1. Evidence metadata: [cp2-prompt-versioning.txt](evidence/cp2-prompt-versioning.txt).
- **Source và tests:** [app/agent.py](../app/agent.py), [app/prompt_management.py](../app/prompt_management.py), [tests/test_agent_prompt_trace.py](../tests/test_agent_prompt_trace.py), [scripts/generate_traces.py](../scripts/generate_traces.py).

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Dashboard local đọc `data/logs.jsonl`, tự refresh 30 giây, cửa sổ 60 phút: latency P50/P95/P99 và TTFT P95; traffic; error breakdown/retrieval success; cost; tokens; quality proxy. Runtime screenshot: [11-dashboard-overview.png](evidence/11-dashboard-overview.png); chạy bằng `python scripts/dashboard.py --serve` ([source](../scripts/dashboard.py)).
- **SLO và lý do chọn:** [`config/slo.yaml`](../config/slo.yaml) đặt `fast_successful_requests` yêu cầu 99.5% request thành công trong ≤3000 ms trên cửa sổ 28 ngày; baseline CP1 latency ứng dụng khoảng 2.2 giây nên còn headroom, cần xác nhận với workload dài hạn.
- **Cách tính error budget:** 100% − 99.5% = 0.5% request xấu; tương đương tối đa 50 request không đạt trên 10,000 request trong cửa sổ SLO.
- **Ba alert và runbook tương ứng:** P95 latency >3000 ms/5m ([runbook 1](../docs/alerts.md#alert-1)); request failure rate >2%/5m ([runbook 2](../docs/alerts.md#alert-2)); retrieval success <90%/5m ([runbook 3](../docs/alerts.md#alert-3)). Cả ba gửi Slack `#llmops-alerts`, có severity và owner trong [`config/alert_rules.yaml`](../config/alert_rules.yaml). Dashboard source: [scripts/dashboard.py](../scripts/dashboard.py); contract: [config/dashboard.yaml](../config/dashboard.yaml).

> CP2 có API verification cho trace/prompt, screenshot dashboard runtime và các ảnh Langfuse cho waterfall, metadata, prompt versions/labels và trạng thái rollback `production`.

## 7. Điều tra challenge

- **Challenge ID:** `day13-k4-l3a-monitoring-llmops-v1` (K4; file challenge được giữ local và `.gitignore` bỏ qua).
- **Khoảng thời gian điều tra:** Dashboard 60 phút, `2026-09-29 10:12–11:12 UTC`; năm request challenge xảy ra `11:08:20.140–11:08:34.875 UTC`.
- **Triệu chứng từ metrics:** Panel latency hiển thị P95 `3568 ms` và P99 `3751 ms`, vượt threshold/SLO P95 `3000 ms`. Ảnh: `evidence/12-incident-metric.png`.
- **Log line và correlation ID liên quan:** Chọn `response_sent` cho `req-b5ce330e`, feature `monitoring`, `latency_ms=3797`, timestamp `2026-09-29T11:08:24.251658Z`; request nhận lúc `11:08:20.140571Z`. Ảnh: `evidence/13-incident-log.png`.
- **Trace ID và span gây ảnh hưởng:** Trace `a5beb1c14fd28ac81f51f1726634d221`, metadata cùng `correlation_id=req-b5ce330e`; root duration `3.80 s`, `document-retrieval` `2.50 s`, `fake-llm-generation` `0.15 s`. Retrieval là span chi phối latency. Ảnh: `evidence/14-incident-trace.png`.
- **Root cause:** Challenge bật `rag_slow`; retrieval giả lập chờ 2.5 giây trong [app/mock_rag.py](../app/mock_rag.py). Trace cho thấy retrieval mất 2.50 giây, trong khi generation mất 0.15 giây, phù hợp với log latency 3.797 giây và P95 vượt ngưỡng.
- **Fix action:** Sau khi thu thập metric, log và trace, đã tắt incident qua `scripts/inject_incident.py --disable`; API xác nhận `rag_slow=false`, `tool_fail=false`, `cost_spike=false`.
- **Preventive measure:** Giữ SLO/alert P95 latency, theo dõi duration riêng của retrieval, đặt timeout cho retrieval và dùng circuit breaker/fallback để tránh một backend chậm kéo dài toàn request.
## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Truyền cùng `correlation_id` qua log và trace để lần theo một request; đồng thời tắt capture input/output và scrub PII trước khi ghi log để giữ khả năng điều tra mà không lưu nội dung nhạy cảm.
- **Một lỗi/blocker đã gặp:** Lần bật challenge đầu tiên gặp `ConnectError` vì API chưa chạy ở `127.0.0.1:8000`. Khởi động Uvicorn trong terminal riêng rồi chạy lại injector và load test thì nhận HTTP 200.
- **Cách tìm nguyên nhân và xử lý:** Bắt đầu từ latency P95 3568 ms vượt 3000 ms, chọn log `req-b5ce330e` có latency 3797 ms, rồi mở trace cùng correlation ID. Span retrieval mất 2.50 s so với generation 0.15 s, khớp với fault `rag_slow`; tắt incident sau khi lưu evidence.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metric chỉ ra thời điểm/triệu chứng; `correlation_id` định vị request trong log; trace chia request thành spans để xác định retrieval là phần gây chậm.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Prompt version/label cho biết request dùng cấu hình nào và hỗ trợ rollback; usage/cost giúp theo dõi chi phí từng generation; SLO và error budget định lượng mức latency/lỗi còn chấp nhận được.
- **Điều quan trọng nhất đã học:** Không kết luận nguyên nhân từ metric đơn lẻ; cần nối metric, log và trace của cùng request trước khi chọn biện pháp xử lý.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** RAG và LLM trong lab là mô phỏng; metrics là dữ liệu lab, chưa chứng minh tải dài hạn. Alert rules có cấu hình Slack/runbook nhưng chưa tích hợp gửi cảnh báo vào Slack thật.

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence được đưa vào commit CP4.
- [x] Các link evidence trong report dùng đường dẫn tương đối và đã được kiểm tra.
- [x] Incident evidence nối metric → log → trace cùng `correlation_id`.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân; public key trong ảnh metadata đã được che.
- [x] Repository tests và validators chạy thành công trong môi trường `.venv`.
- [x] Không đưa `.env`, `config/challenge.json`, PII thô hoặc evidence lớp khác vào commit.
- [ ] URL repo và SHA nộp cuối đã được gửi lên LMS/Codelabs.




