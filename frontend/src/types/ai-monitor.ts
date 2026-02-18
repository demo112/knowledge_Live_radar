export interface AIMetric {
  id: string;
  timestamp: string;
  module?: string;
  model: string;
  provider: string;
  latency: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  status: "success" | "error";
  error_message?: string;
}

export interface PaginatedAIMetrics {
  items: AIMetric[];
  total: number;
  page: number;
  page_size: number;
}

export interface ModelStat {
  model: string;
  count: number;
  avg_latency: number;
  total_tokens: number;
  success_rate: number;
}

export interface AIStats {
  total_requests: number;
  success_rate: number;
  total_tokens: number;
  avg_latency: number;
  models: ModelStat[];
}

export interface MetricFilters {
  page: number;
  page_size: number;
  module?: string;
  model?: string;
  provider?: string;
  status?: string;
  start_time?: string;
  end_time?: string;
}
