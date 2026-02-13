export interface Pyramid {
  id: string;
  name: string;
  description?: string;
  created_at: string;
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

export interface HealthReport {
  id: string;
  report_type: string;
  overall_score: number;
  pyramid_scores: Record<string, number>;
  source_health_score: number;
  content_coverage_score: number;
  hotspot_distribution: Record<string, number>;
  approval_backlog: Record<string, any>;
  crawl_stats: Record<string, any>;
  issues: HealthIssue[];
  created_at: string;
}

export interface HealthIssue {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  entity_id?: string;
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
  is_active: boolean;
  last_run_at?: string;
  next_run_at?: string;
  created_at: string;
  updated_at: string;
}

export interface TaskExecution {
  id: string;
  task_id: string;
  status: 'running' | 'success' | 'failed';
  started_at: string;
  ended_at?: string;
  duration_seconds?: number;
  error_message?: string;
  result?: any;
}

export interface ConfigHistory {
  id: string;
  config_key: string;
  old_value?: any;
  new_value?: any;
  changed_by: string;
  created_at: string;
}

export interface DriftProposal {
  id: string;
  type: string;
  status: string;
  target_id: string;
  data: any;
  created_at: string;
}

export interface ChangeItem {
  id: string;
  type: string;
  created_at: string;
  applicant_id?: string;
  data?: any;
  status: string;
  reason?: string;
  impact_analysis?: any;
  original_data?: any;
}
