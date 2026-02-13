export interface Pyramid {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface PyramidNode {
  id: string;
  pyramid_id: string;
  parent_id?: string;
  name: string;
  content?: string;
  description?: string;
  node_type: string;
  level: number;
  path: string;
  health_score: number;
  sort_order: number;
  children?: PyramidNode[];
}

export interface PyramidDetail extends Pyramid {
  nodes: PyramidNode[];
}

export interface InformationSource {
  id: string;
  name: string;
  type: string;
  url: string;
  config: any;
  status: string;
  health_score: number;
  last_crawled_at?: string;
  check_interval: number;
  created_at: string;
  updated_at: string;
}

export interface ContentItem {
  id: string;
  source_id?: string;
  url: string;
  title: string;
  summary?: string;
  content_text?: string;
  publish_time?: string;
  status: string;
  created_at: string;
  tags?: string[];
  concepts?: Array<{ name: string; type: string }>;
  ai_processed?: boolean;
}

export interface ContentWithRelation extends ContentItem {
  relation_source: string;
  relation_confidence: number;
  relation_created_at: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: {
    items: T[];
    total: number;
    page: number;
    page_size: number;
  };
}

export interface SuccessResponse<T> {
  success: boolean;
  data: T;
}

export interface DomainWhitelist {
  id: string;
  domain: string;
  credibility: number;
  reason?: string;
  created_at: string;
  updated_at: string;
}

export interface DiscoveredDomain {
  id: string;
  domain: string;
  occurrence_count: number;
  first_seen_at: string;
  last_seen_at: string;
  evaluation_status: string;
  has_rss: boolean;
  proposal_id?: string;
}

// --- New Types for Core Management Enhancement ---

export interface NodeRelation {
  id: string;
  source_node_id: string;
  target_node_id: string;
  relation_type: string;
  created_at: string;
}

export interface HealthMetrics {
  depth_score: number;
  coverage_score: number;
  activity_score: number;
}

export interface HealthReport {
  score: number;
  details: HealthMetrics;
  suggestions: string[];
}

export interface ReactFlowNode {
  id: string;
  type?: string;
  data: { label: string; [key: string]: any };
  position: { x: number; y: number };
  style?: any;
}

export interface ReactFlowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  type?: string;
  animated?: boolean;
}

export interface VisualizationData {
  nodes: ReactFlowNode[];
  edges: ReactFlowEdge[];
}

export interface NodeCreate {
  name: string;
  content?: string;
  node_type: string;
}

export interface SplitRequest {
  sub_nodes: NodeCreate[];
  delete_original: boolean;
}

export interface MergeRequest {
  source_node_ids: string[];
  target_node_name: string;
  target_node_content?: string;
  strategy: 'create_new' | 'merge_to_first';
}

export interface LinkRequest {
  target_node_id: string;
  relation_type: string;
}

export interface Hotspot {
  id: string;
  title: string;
  summary?: string;
  score: number;
  keywords: string[];
  created_at: string;
  status: string;
}

export interface ScheduledTask {
  id: string;
  name: string;
  task_type: string;
  cron_expression: string;
  is_active: boolean;
  last_run_at?: string;
  next_run_at?: string;
}

export interface TaskExecution {
  id: string;
  task_id: string;
  status: string;
  start_time: string;
  end_time?: string;
  result?: string;
  error?: string;
}

export interface ConfigHistory {
  id: string;
  key: string;
  old_value: any;
  new_value: any;
  changed_by: string;
  changed_at: string;
}

export interface DriftProposal {
  id: string;
  type: string;
  status: string;
  data: any;
  created_at: string;
}

export interface Approval {
  id: string;
  type: string;
  status: string;
  data: any;
  created_at: string;
  applicant_id?: string;
  reason?: string;
  confidence_score?: number;
  review_comment?: string;
  reviewer_id?: string;
  reviewed_at?: string;
  executed_at?: string;
}
