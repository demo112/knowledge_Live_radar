
export interface Pyramid {
  id: string;
  name: string;
  description?: string;
  created_at: string;
}

export interface PyramidTemplate {
  id: string;
  name: string;
  description?: string;
  [key: string]: unknown;
}

export interface InformationSource {
  id: string;
  name: string;
  type: string;
  url: string;
  check_interval: number;
  last_checked?: string;
  status: string;
  consecutive_failures: number;
}

export interface ApprovalBacklogData {
  pending_count: number;
  backlog_penalty?: number;
  oldest_pending_days?: number;
  [key: string]: unknown;
}

export interface CrawlStatsData {
  total_crawled?: number;
  success_rate?: number;
  avg_processing_time?: number;
  validated_count?: number;
  rejected_count?: number;
  active_tasks?: number;
  success_rate_24h?: number;
  total_pages_crawled?: number;
  avg_latency?: number;
  [key: string]: unknown;
}

export interface HealthReport {
  id: string;
  report_type: string;
  overall_score: number;
  pyramid_scores: Record<string, number>;
  source_health_score: number;
  content_coverage_score: number;
  hotspot_distribution: Record<string, number>;
  approval_backlog: ApprovalBacklogData;
  crawl_stats: CrawlStatsData;
  issues: HealthIssue[];
  created_at: string;
}

export interface HealthIssue {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  entity_id?: string;
  category?: string;
}

export interface ContributionStats {
  total: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  period_days: number;
}

export interface Contribution {
  id: string;
  user_id?: string;
  input_type: string;
  original_input: string;
  status: string;
  extracted_concepts?: Record<string, unknown>[];
  extracted_content?: string;
  created_at: string;
  rejection_reason?: string;
}

export interface Hotspot {
  id: string;
  keyword: string;
  status: 'new' | 'emerging' | 'trending' | 'mature' | 'cooling' | 'archived';
  heat_score: number;
  first_seen_at: string;
  last_seen_at: string;
  recent_7d_count: number;
  growth_rate: number;
}

export interface ScheduledTask {
  id: string;
  task_name: string;
  task_type: string;
  cron_expression: string;
  next_run_at?: string;
  last_run_at?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskExecution {
  id: string;
  task_id: string;
  status: string;
  started_at: string;
  ended_at?: string;
  duration_seconds?: number;
  error_message?: string;
}

export interface ContentItem {
  id: string;
  title: string;
  url: string;
  content_type: string;
  summary?: string;
  publish_date?: string;
  author?: string;
  status: string;
  quality_score?: number;
  chinese_ratio?: number;
  created_at: string;
}

export interface ChangeItem {
  id: string;
  type: string;
  status: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
  user_id?: string;
  details?: any;
  applicant_id?: string;
  reason?: string;
  impact_analysis?: {
    risk_level: string;
    affected_nodes_count: number;
    description: string;
  };
  data?: any;
  original_data?: any;
}

export interface MetricFilters {
  start_date?: string;
  end_date?: string;
  metric_type?: string;
  limit?: number;
}

export interface AIMetrics {
  id: string;
  timestamp: string;
  model: string;
  tokens_input: number;
  tokens_output: number;
  cost: number;
  latency_ms: number;
  success: boolean;
  error_type?: string;
}

export interface PaginatedAIMetrics {
  items: AIMetrics[];
  total: number;
  page: number;
  page_size: number;
}

export interface AIStats {
  total_requests: number;
  total_tokens: number;
  total_cost: number;
  avg_latency: number;
  error_rate: number;
  daily_usage: Record<string, number>;
  model_usage: Record<string, number>;
}

export interface SynonymCreate {
  term: string;
  synonyms: string[];
  language?: string;
}

export interface ConfigHistory {
  id: string;
  config_key: string;
  old_value: unknown;
  new_value: unknown;
  changed_by: string;
  created_at: string;
}
