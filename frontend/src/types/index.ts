export interface Pyramid {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface DouyinConvertResponse {
  video_info: {
    title: string;
    url: string;
    author: string;
    duration: number;
    cover: string;
    description: string;
    create_time: string;
  };
  content: {
    audio_text: string;
    summary: string;
    keywords: string[];
    sentiment: string;
  };
  markdown: string;
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

export interface LinkedNode extends PyramidNode {
  relation_source: string;
  relation_confidence: number;
}

export interface PyramidDetail extends Pyramid {
  nodes: PyramidNode[];
}

export interface PyramidTemplate {
  id: string;
  name: string;
  description: string;
  structure: unknown;
  created_at: string;
}

export interface InformationSource {
  id: string;
  name: string;
  type: string;
  url: string;
  config: Record<string, unknown>;
  status: string; // 'ACTIVE' | 'INACTIVE' | 'MONITORING' | 'ADJUSTING'
  health_score: number;
  error_count: number;
  last_error_at?: string;
  last_crawled_at?: string;
  next_crawl_at?: string;
  check_interval: number;
  template_id?: string;
  created_at: string;
  updated_at: string;
}

export interface DiscoveredSource {
  id: string;
  url: string;
  name: string;
  description?: string;
  source_type: string;
  reason?: string;
  created_at: string;
  status: 'pending' | 'approved' | 'rejected';
}

export interface SourceTemplateConfigField {
  name: string;
  label: string;
  type: string; // text, number, boolean, select
  required: boolean;
  default?: unknown;
  options?: Array<{ label: string; value: string }>;
  description?: string;
}

export interface SourceTemplate {
  id: string;
  name: string;
  description: string;
  source_type: string;
  config_schema: SourceTemplateConfigField[];
  default_config: Record<string, unknown>;
}

export interface ValidationResult {
  overall_score?: number;
  hard_result?: Record<string, unknown>;
  soft_result?: Record<string, unknown>;
  verified_at: string;
}

export interface ContentNodeInfo {
  id: string;
  name: string;
  pyramid_id: string;
  pyramid_name: string;
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
  validation_result?: ValidationResult;
  nodes?: ContentNodeInfo[];
  lifecycle_status?: string; // ACTIVE, DEPRECATED, ARCHIVED, DELETED
  metabolism_score?: number;
  last_accessed_at?: string;
  access_count?: number;
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
  updated_at?: string;
}

export interface HealthMetrics {
  depth_score: number;
  coverage_score: number;
  activity_score: number;
}

export interface AISuggestion {
  id: string;
  action_type: string;
  target_type: string;
  target_id?: string;
  target_name?: string;
  reason: string;
  params: Record<string, unknown>;
  confidence: number;
  status: string;
  pyramid_id?: string;
  source_id?: string;
  created_at: string;
  expires_at?: string;
}

export interface HealthReport {
  score: number;
  details: HealthMetrics;
  suggestions: AISuggestion[];
  analysis?: Record<string, unknown>;
}

export interface ReactFlowNode {
  id: string;
  type?: string;
  data: { label: string; [key: string]: unknown };
  position: { x: number; y: number };
  style?: Record<string, unknown>;
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

export interface MetabolismRunStats {
  processed: number;
  to_deprecated: number;
  to_archived: number;
}

export interface MetabolismSuggestion {
  id: string;
  title: string;
  score: number;
  age_days: number;
  reason: string;
}

export interface DashboardStats {
  active_sources: number;
  total_sources: number;
  discovered_domains: number;
  whitelisted_domains: number;
  total_contents: number;
  validation_pass_rate: number;
}

export interface TrendPoint {
  date: string;
  pass_rate: number;
  total_validations: number;
}

export interface DashboardTrend {
  trends: TrendPoint[];
}

export interface MergeRequest {
  source_node_ids: string[];
  target_node_name?: string;
  target_node_content?: string;
  strategy: 'create_new' | 'merge_to_first';
}

export interface LinkRequest {
  target_node_id: string;
  relation_type: string;
}

export interface Synonym {
  id: string;
  canonical_term: string;
  synonym: string;
  source: string;
  confidence: number;
  is_active: boolean;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export interface SynonymCreate {
  canonical_term: string;
  synonym: string;
  source?: string;
  confidence?: number;
  is_active?: boolean;
}

export interface Approval {
  id: string;
  type: string;
  target_id?: string;
  data?: Record<string, unknown>;
  applicant_id?: string;
  source_content_id?: string;
  generated_by?: string;
  reason?: string;
  confidence_score?: number;
  status: string;
  reviewer_id?: string;
  review_comment?: string;
  created_at: string;
  updated_at: string;
}
