import api from '@/lib/api';
import { UUID } from 'crypto';

export interface KnowledgeNode {
  id: string;
  name: string;
  description?: string;
  node_type: string;
  ai_model?: any;
  status: string;
  health_score: number;
  content_count: number;
  last_content_at?: string;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeCluster {
  id: string;
  name: string;
  description?: string;
  cluster_type: string;
  center_node_id?: string;
  status: string;
  health_score: number;
  node_count: number;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeRelation {
  id: string;
  source_node_id: string;
  target_node_id: string;
  relation_type: string;
  weight: number;
  confidence: number;
  created_at: string;
}

export interface KnowledgeGraphData {
  root_id: string;
  nodes: KnowledgeNode[];
  edges: KnowledgeRelation[];
}

export const knowledgeApi = {
  getNodes: async (params?: { skip?: number; limit?: number }) => {
    const response = await api.get('/knowledge/nodes', { params });
    return response.data;
  },

  getClusters: async (params?: { skip?: number; limit?: number }) => {
    const response = await api.get('/knowledge/clusters', { params });
    return response.data;
  },

  getGraph: async (nodeId: string, depth: number = 2) => {
    const response = await api.get(`/knowledge/nodes/${nodeId}/graph`, {
      params: { depth },
    });
    return response.data;
  },
  
  getNode: async (id: string) => {
    const response = await api.get(`/knowledge/nodes/${id}`);
    return response.data;
  },
};
