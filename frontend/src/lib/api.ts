import axios from 'axios';
import { MergeRequest, SplitRequest, LinkRequest, SynonymCreate } from '../types';
import { MetricFilters, PaginatedAIMetrics, AIStats } from '../types/ai-monitor';

const isServer = typeof window === 'undefined';
// Server-side calls should go directly to the backend
// Client-side calls should go through Next.js proxy (/api/v1 -> http://127.0.0.1:8000/api/v1)
const baseURL = isServer 
  ? (process.env.INTERNAL_API_URL || 'http://127.0.0.1:8000/api/v1') 
  : '/api/v1';

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const pyramidApi = {
  getAll: async () => {
    const response = await api.get('/pyramids');
    return response.data;
  },
  getById: async (id: string) => {
    const response = await api.get(`/pyramids/${id}`);
    return response.data;
  },
  create: async (data: Record<string, unknown>) => {
    const response = await api.post('/pyramids', data);
    return response.data;
  },
  getTemplates: async () => {
    const response = await api.get('/pyramids/templates');
    return response.data;
  },
  createFromTemplate: async (templateId: string, name?: string) => {
    const response = await api.post(`/pyramids/from-template/${templateId}`, null, { params: { name } });
    return response.data;
  },
  exportTemplate: async (id: string) => {
    const response = await api.get(`/pyramids/${id}/export`);
    return response.data;
  },
  importTemplate: async (data: Record<string, unknown>) => {
    const response = await api.post('/pyramids/import', data);
    return response.data;
  },
  update: async (id: string, data: Record<string, unknown>) => {
    const response = await api.put(`/pyramids/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await api.delete(`/pyramids/${id}`);
    return response.data;
  },
  addNode: async (pyramidId: string, data: Record<string, unknown>) => {
    const response = await api.post(`/pyramids/${pyramidId}/nodes`, data);
    return response.data;
  },
  mergeNodes: async (pyramidId: string, data: MergeRequest) => {
    const response = await api.post(`/pyramids/${pyramidId}/merge-nodes`, data);
    return response.data;
  },
  getHealth: async (pyramidId: string) => {
    const response = await api.get(`/pyramids/${pyramidId}/health`);
    return response.data;
  },
  analyze: async (pyramidId: string, mode: 'health' | 'structure' | 'all' = 'health') => {
    const response = await api.post(`/pyramids/${pyramidId}/analyze`, null, { params: { mode } });
    return response.data;
  },
  getSuggestions: async (pyramidId: string) => {
    const response = await api.get(`/pyramids/${pyramidId}/suggestions`);
    return response.data;
  },
  applySuggestion: async (pyramidId: string, suggestionId: string) => {
    const response = await api.post(`/pyramids/${pyramidId}/suggestions/${suggestionId}/apply`);
    return response.data;
  },
  rejectSuggestion: async (pyramidId: string, suggestionId: string, reason?: string) => {
    const response = await api.post(`/pyramids/${pyramidId}/suggestions/${suggestionId}/reject`, { reason });
    return response.data;
  },
  getVisualization: async (pyramidId: string) => {
    const response = await api.get(`/pyramids/${pyramidId}/visualization`);
    return response.data;
  },
  getHistory: async (pyramidId: string) => {
    const response = await api.get(`/pyramids/${pyramidId}/snapshots`);
    return response.data;
  },
  createSnapshot: async (pyramidId: string, reason: string) => {
    const response = await api.post(`/pyramids/${pyramidId}/snapshots`, { reason });
    return response.data;
  },
  getSnapshot: async (pyramidId: string, snapshotId: string) => {
    const response = await api.get(`/pyramids/${pyramidId}/snapshots/${snapshotId}`);
    return response.data;
  },
  rollback: async (pyramidId: string, snapshotId: string) => {
    const response = await api.post(`/pyramids/${pyramidId}/rollback/${snapshotId}`);
    return response.data;
  }
};

export const nodeApi = {
  split: async (id: string, data: SplitRequest) => {
    const response = await api.post(`/nodes/${id}/split`, data);
    return response.data;
  },
  link: async (id: string, data: LinkRequest) => {
    const response = await api.post(`/nodes/${id}/link`, data);
    return response.data;
  },
  move: async (id: string, data: { target_parent_id: string }) => {
    const response = await api.post(`/nodes/${id}/move`, data);
    return response.data;
  },
  get: async (id: string) => {
    const response = await api.get(`/nodes/${id}`);
    return response.data;
  },
  update: async (id: string, data: Record<string, unknown>) => {
    const response = await api.put(`/nodes/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await api.delete(`/nodes/${id}`);
    return response.data;
  },
  getContents: async (id: string) => {
    const response = await api.get(`/nodes/${id}/contents`);
    return response.data;
  },
  linkContent: async (id: string, contentId: string) => {
    const response = await api.post(`/nodes/${id}/contents/${contentId}`);
    return response.data;
  },
  unlinkContent: async (id: string, contentId: string) => {
    const response = await api.delete(`/nodes/${id}/contents/${contentId}`);
    return response.data;
  }
};

export const sourceApi = {
  getAll: async () => {
    const response = await api.get('/sources');
    return response.data;
  },
  create: async (data: Record<string, unknown>) => {
    const response = await api.post('/sources', data);
    return response.data;
  },
  update: async (id: string, data: Record<string, unknown>) => {
    const response = await api.put(`/sources/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await api.delete(`/sources/${id}`);
    return response.data;
  },
  crawl: async (id: string) => {
    const response = await api.post(`/sources/${id}/crawl`);
    return response.data;
  },
  getCrawlHistory: async (id: string) => {
    const response = await api.get(`/sources/${id}/history`);
    return response.data;
  },
  test: async (id: string) => {
    const response = await api.post(`/sources/${id}/test`);
    return response.data;
  },
  getTemplates: async () => {
    const response = await api.get('/sources/templates');
    return response.data;
  },
  renderTemplate: async (id: string, params: Record<string, unknown>) => {
    const response = await api.post(`/sources/templates/${id}/render`, params);
    return response.data;
  }
};

export const contentApi = {
  getAll: async (params?: Record<string, unknown>) => {
    const response = await api.get('/contents', { params });
    return response.data;
  },
  getById: async (id: string) => {
    const response = await api.get(`/contents/${id}`);
    return response.data;
  },
  getNodes: async (id: string) => {
    const response = await api.get(`/contents/${id}/nodes`);
    return response.data;
  },
  uploadFile: async (file: File, submitterId?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (submitterId) {
      formData.append('submitter_id', submitterId);
    }
    const response = await api.post('/contents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  submitUrl: async (url: string, submitterId?: string) => {
    const response = await api.post('/contents/url', { url, submitter_id: submitterId });
    return response.data;
  },
  submitText: async (text: string, title: string, submitterId?: string) => {
    const response = await api.post('/contents/text', { text, title, submitter_id: submitterId });
    return response.data;
  },
};

export const approvalApi = {
  getQueue: async () => {
    const response = await api.get('/approvals/queue');
    return response.data;
  },
  getPending: async () => {
    const response = await api.get('/approvals/pending');
    return response.data;
  },
  getAll: async (status?: string) => {
    const response = await api.get('/approvals', { params: { status } });
    return response.data;
  },
  approve: async (id: string, note?: string) => {
    const response = await api.post(`/approvals/${id}/approve`, { note });
    return response.data;
  },
  reject: async (id: string, note: string) => {
    const response = await api.post(`/approvals/${id}/reject`, { note });
    return response.data;
  },
  review: async (id: string, status: string, note?: string, reviewer_id?: string) => {
    const response = await api.post(`/approvals/${id}/review`, { status, note, reviewer_id });
    return response.data;
  },
  execute: async (id: string) => {
    const response = await api.post(`/approvals/${id}/execute`);
    return response.data;
  },
  getImpact: async (id: string) => {
    const response = await api.get(`/approvals/${id}/impact`);
    return response.data;
  },
  rollback: async (id: string) => {
    const response = await api.post(`/approvals/${id}/rollback`);
    return response.data;
  }
};

export const discoveryApi = {
  discover: async (url: string) => {
    const response = await api.post('/discovery/discover', { url });
    return response.data;
  },
  getDiscoveredDomains: async () => {
    const response = await api.get('/discovery/domains');
    return response.data;
  },
  approve: async (id: string) => {
    const response = await api.post(`/discovery/domains/${id}/approve`);
    return response.data;
  },
  reject: async (id: string) => {
    const response = await api.post(`/discovery/domains/${id}/reject`);
    return response.data;
  }
};

export const whitelistApi = {
  getAll: async () => {
    const response = await api.get('/whitelist');
    return response.data;
  },
  add: async (data: { domain: string; reason?: string; credibility?: number }) => {
    const response = await api.post('/whitelist', data);
    return response.data;
  },
  remove: async (id: string) => {
    const response = await api.delete(`/whitelist/${id}`);
    return response.data;
  },
  update: async (id: string, data: Record<string, unknown>) => {
    const response = await api.put(`/whitelist/${id}`, data);
    return response.data;
  },
};

export const dashboardApi = {
  getStats: async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },
  getTrend: async (days: number = 7) => {
    const response = await api.get(`/dashboard/trend?days=${days}`);
    return response.data;
  }
};

export const healthApi = {
  triggerDetection: async () => {
    const response = await api.post('/health/detect');
    return response.data;
  },
  getReport: async () => {
    const response = await api.get('/health/report/latest');
    return response.data;
  },
  getSystemHealth: async () => {
    const response = await api.get('/health/report/latest');
    return response.data;
  },
  getPyramidHealth: async (id: string) => {
    const response = await api.get(`/health/pyramids/${id}`);
    return response.data;
  }
};

export const contributionApi = {
  getAll: async (params?: { skip?: number; limit?: number; user_id?: string }) => {
    const response = await api.get('/contributions', { params });
    return response.data;
  },
  getById: async (id: string) => {
    const response = await api.get(`/contributions/${id}`);
    return response.data;
  },
  getStats: async (days: number = 30) => {
    const response = await api.get('/contributions/stats', { params: { days } });
    return response.data;
  }
};

export const synonymApi = {
  getAll: async (params?: { skip?: number; limit?: number }) => {
    const response = await api.get('/synonyms', { params });
    return response.data;
  },
  create: async (data: SynonymCreate) => {
    const response = await api.post('/synonyms', data);
    return response.data;
  },
  bulkCreate: async (data: SynonymCreate[]) => {
    const response = await api.post('/synonyms/bulk', data);
    return response.data;
  },
  delete: async (synonym: string) => {
    const response = await api.delete(`/synonyms/${encodeURIComponent(synonym)}`);
    return response.data;
  },
  getCanonical: async (term: string) => {
    const response = await api.get(`/synonyms/canonical/${encodeURIComponent(term)}`);
    return response.data;
  }
};

export const metabolismApi = {
  run: async () => {
    const response = await api.post('/content-management/metabolism/run');
    return response.data;
  },
  getSuggestions: async (limit: number = 50) => {
    const response = await api.get('/content-management/metabolism/suggestions', { params: { limit } });
    return response.data;
  },
  cleanup: async (ids: string[]) => {
    const response = await api.post('/content-management/metabolism/cleanup', { ids });
    return response.data;
  }
};

export const hotspotApi = {
  getAll: async () => {
    const response = await api.get('/hotspots');
    return response.data;
  },
  getHotspots: async () => {
    const response = await api.get('/hotspots');
    return response.data;
  }
};

export const evolutionApi = {
  triggerOptimization: async () => {
    const response = await api.post('/strategy/optimize');
    return response.data;
  },
  classifyContent: async (contentId: string) => {
    const response = await api.post(`/evolution/classify/${contentId}`);
    return response.data;
  },
  batchClassify: async () => {
    const response = await api.post('/evolution/classify/batch');
    return response.data;
  },
  getEvolution: async () => {
    return { success: true, data: [] };
  }
};

export const schedulerApi = {
  pause: async (taskId: string) => {
    const response = await api.post(`/scheduler/tasks/${taskId}/pause`);
    return response.data;
  },
  resume: async (taskId: string) => {
    const response = await api.post(`/scheduler/tasks/${taskId}/resume`);
    return response.data;
  },
  trigger: async (taskId: string) => {
    const response = await api.post(`/scheduler/tasks/${taskId}/run`);
    return response.data;
  },
  getExecutions: async () => {
    const response = await api.get('/scheduler/executions');
    return response.data;
  },
  getAll: async () => {
    const response = await api.get('/scheduler/tasks');
    return response.data;
  },
  getTasks: async () => {
    const response = await api.get('/scheduler/tasks');
    return response.data;
  },
  runTask: async (taskId: string) => {
    const response = await api.post(`/scheduler/tasks/${taskId}/run`);
    return response.data;
  },
};

export const configApi = {
  getHistory: async () => {
    const response = await api.get('/config/history');
    return response.data;
  },
  getAll: async () => {
    const response = await api.get('/config');
    return response.data;
  },
  update: async (key: string, value: unknown) => {
    const response = await api.put(`/config/${key}`, { value });
    return response.data;
  },
  testAIConnection: async (target: 'auto' | 'local' | 'cloud' = 'auto') => {
    const response = await api.post('/config/ai/test', null, { params: { target } });
    return response.data;
  }
};

export const suggestionApi = {
  getAll: async (params?: { pyramid_id?: string; source_id?: string; status?: string }) => {
    const response = await api.get('/suggestions', { params });
    return response.data;
  },
  approve: async (id: string) => {
    const response = await api.post(`/suggestions/${id}/approve`);
    return response.data;
  },
  reject: async (id: string, reason?: string) => {
    const response = await api.post(`/suggestions/${id}/reject`, null, { params: { reason } });
    return response.data;
  },
  execute: async (id: string) => {
    const response = await api.post(`/suggestions/${id}/execute`);
    return response.data;
  }
};

export const contentManagementApi = {
  batchClean: async (dryRun: boolean = false, chineseRatioThreshold: number = 0.2) => {
    const response = await api.post('/contents/batch/clean', { 
      dry_run: dryRun, 
      chinese_ratio_threshold: chineseRatioThreshold 
    });
    return response.data;
  },
  batchSummarize: async (targetIds?: string[], overwrite: boolean = true) => {
    const response = await api.post('/contents/batch/summarize', { 
      target_ids: targetIds, 
      overwrite 
    });
    return response.data;
  },
  batchDelete: async (ids: string[]) => {
    const response = await api.post('/contents/batch/delete', { ids });
    return response.data;
  }
};

export const aiMonitorApi = {
  getMetrics: async (params: MetricFilters) => {
    const response = await api.get<PaginatedAIMetrics>('/ai-monitor/metrics', { params });
    return response.data;
  },
  getStats: async (start_time?: string, end_time?: string) => {
    const params = { start_time, end_time };
    const response = await api.get<AIStats>('/ai-monitor/stats', { params });
    return response.data;
  },
  cleanMetrics: async (days: number) => {
    const response = await api.post('/ai-monitor/clean', { days });
    return response.data;
  }
};
