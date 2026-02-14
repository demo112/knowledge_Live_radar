# Requirements: LLM Service Fallback Mechanism

## Overview

Implement a dual-engine AI service architecture that prioritizes a local LLM (Ollama) for cost efficiency and data privacy, while automatically falling back to a cloud-based LLM (SiliconFlow) when the local service is unavailable, overloaded, or encounters errors.

## User Stories

### Story 1: Local First Strategy

As a **System Administrator**, I want the system to prioritize using the local Ollama service, so that I can reduce API costs and utilize local hardware.

**Acceptance Criteria:**

- [ ] AC1: Prioritize Local Execution
  - **Given**: Local Ollama is running and configured, Cloud service is configured
  - **When**: An AI task is requested
  - **Then**: System attempts to call Ollama first

- [ ] AC2: Successful Local Response
  - **Given**: Local Ollama is healthy
  - **When**: Ollama returns a valid response
  - **Then**: The result is returned, and Cloud service is NOT called

### Story 2: Automatic Fallback

As a **Developer**, I want the system to switch to the cloud service when local fails, so that the application remains reliable.

**Acceptance Criteria:**

- [ ] AC1: Fallback on Connection Error
  - **Given**: Local Ollama is down (connection refused)
  - **When**: An AI task is requested
  - **Then**: System detects the error, logs a warning, and successfully calls the Cloud service

- [ ] AC2: Fallback on Timeout/Busy
  - **Given**: Local Ollama is overloaded (times out)
  - **When**: An AI task is requested
  - **Then**: System switches to Cloud service after the timeout

### Story 3: Configuration Management

As a **User**, I want to configure both services independently, so that I can choose different models for local and cloud.

**Acceptance Criteria:**

- [ ] AC1: Independent Configuration
  - **Given**: `config.yaml` or `.env`
  - **When**: User sets `ai.local.base_url`, `ai.local.model`, `ai.cloud.api_key`, `ai.cloud.model`
  - **Then**: System respects these settings

## Constraints

- **Latency**: Fallback mechanism should not introduce excessive latency (fail fast on local).
- **Consistency**: Both services should support OpenAI-compatible API formats (which Ollama and SiliconFlow both do).

## Out of Scope

- Load balancing between multiple local instances.
- Complex routing based on task type (e.g., "use cloud for reasoning, local for summary") - *Future feature*.

## Assumptions

- Ollama is running in an OpenAI-compatible mode (default).
- SiliconFlow is used as the cloud provider (compatible with OpenAI SDK).
