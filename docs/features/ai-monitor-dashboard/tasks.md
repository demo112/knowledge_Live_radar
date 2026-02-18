# Tasks

- [x] Task 1: Backend - AI Metrics Data Model
    - [x] Define `AIMetric` model in `backend/app/models/ai_metric.py` with fields: id, timestamp, module, model, provider, latency, prompt_tokens, completion_tokens, total_tokens, status, error_message.
    - [x] Create Alembic migration for `ai_metrics` table.
    - [x] Run migration.

- [x] Task 2: Backend - AI Client Instrumentation
    - [x] Modify `backend/app/core/ai/client.py` to record metrics after each `chat_completion` call.
    - [x] Ensure metrics recording is non-blocking (async) and handles database errors gracefully.

- [x] Task 3: Backend - AI Monitor API
    - [x] Create `AIMonitorService` in `backend/app/services/ai_monitor_service.py` to aggregate metrics (daily stats, recent logs) and handle config updates.
    - [x] Create `AIMonitorRouter` in `backend/app/routers/ai_monitor.py` with endpoints:
        - `GET /stats`: Returns aggregated stats (total requests, tokens, error rate, etc.).
        - `GET /logs`: Returns paginated list of `AIMetric` records.
        - `GET /config`: Returns current AI configuration.
        - `POST /config`: Updates AI configuration (model, temperature, enabled status).
    - [x] Register router in `backend/app/main.py`.

- [x] Task 4: Frontend - AI Monitor Dashboard Page
    - [x] Create `frontend/src/app/(dashboard)/ai-monitor/page.tsx`.
    - [x] Implement `StatsCards` component to show key metrics.
    - [x] Implement `UsageChart` component (using Recharts or similar) to show trends.
    - [x] Implement `RequestLogTable` component to list recent calls.
    - [x] Implement `ControlPanel` component for configuration management.

- [x] Task 5: Integration & Testing
    - [x] Verify that AI calls from existing modules (e.g., crawl, validate) are correctly recorded in the metrics table.
    - [x] Verify that the dashboard displays correct data.
    - [x] Verify that configuration changes in the dashboard effectively change AI behavior.
