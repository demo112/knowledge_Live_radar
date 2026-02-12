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
  description?: string;
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
