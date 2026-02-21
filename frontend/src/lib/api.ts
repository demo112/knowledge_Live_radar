import axios from 'axios';
import { MergeRequest, SplitRequest, LinkRequest, SynonymCreate, DouyinConvertResponse } from '../types';
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

export const toolsApi = {
  convertDouyin: async (url: string): Promise<DouyinConvertResponse> => {
    const response = await api.post('/tools/douyin/convert', { url });
    return response.data;
  },
  convertDouyinStream: async (url: string, onProgress: (event: any) => void, cookies?: string): Promise<DouyinConvertResponse> => {
    const response = await fetch(`${baseURL}/tools/douyin/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url, cookies }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let result: DouyinConvertResponse | null = null;
    let buffer = '';

    if (reader) {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        const lines = buffer.split('\n\n');
        
        // The last element is either empty (if string ended with \n\n) or incomplete
        buffer = lines.pop() || '';
        
        for (const line of lines) {
          if (line.trim().startsWith('data: ')) {
            let data;
            try {
              const jsonStr = line.trim().substring(6);
              data = JSON.parse(jsonStr);
              if (data.stage === 'error') {
                throw new Error(data.message || 'Conversion failed');
              }
              onProgress(data);
              if (data.stage === 'completed') {
                result = data.data;
              }
            } catch (e: any) {
              // If it's our own error from above, re-throw it to break the loop
              if (e.message && data?.stage === 'error') {
                 throw e;
              }
              console.error('Failed to parse SSE data', e);
            }
          }
        }
      }
    }
    
    if (!result) throw new Error('Stream ended without completion');
    return result;
  }
};

/**
 * @deprecated Legacy Pyramid API. Use knowledgeApi instead.
 */
export const pyramidApi = {
  getAll: async () => {
    const response = await api.get('/pyramids/');
    return response.data;
  },
  getById: async (id: string) => {
    const response = await api.get(`/pyramids/${id}`);
    return response.data;
  },
  create: async (data: Record<string, unknown>) => {
    const response = await api.post('/pyramids/', data);
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
    const response = await api.post(`/pyramids/${pyramidId}/snapshots/${snapshotId}/rollback`);
    return response.data;
  }
};

/**
 * @deprecated Legacy Node API (PyramidNode). Use knowledgeApi instead.
 */
export const nodeApi = {
  update: async (pyramidId: string, nodeId: string, data: Record<string, unknown>) => {
    const response = await api.put(`/nodes/${nodeId}`, data);
    return response.data;
  },
  delete: async (pyramidId: string, nodeId: string) => {
    const response = await api.delete(`/nodes/${nodeId}`);
    return response.data;
  },
  split: async (pyramidId: string, nodeId: string, data: SplitRequest) => {
    const response = await api.post(`/nodes/${nodeId}/split`, data);
    return response.data;
  },
  link: async (pyramidId: string, nodeId: string, data: LinkRequest) => {
    const response = await api.post(`/nodes/${nodeId}/link`, data);
    return response.data;
  },
  unlink: async (pyramidId: string, nodeId: string, targetId: string) => {
    const response = await api.delete(`/nodes/${nodeId}/link/${targetId}`);
    return response.data;
  },
  move: async (pyramidId: string, nodeId: string, targetParentId: string) => {
    const response = await api.post(`/nodes/${nodeId}/move`, { new_parent_id: targetParentId });
    return response.data;
  },
  getContents: async (nodeId: string) => {
    const response = await api.get(`/nodes/${nodeId}/contents`);
    return response.data;
  },
  unlinkContent: async (nodeId: string, contentId: string) => {
    const response = await api.delete(`/nodes/${nodeId}/contents/${contentId}`);
    return response.data;
  }
};

export const sourceApi = {
  getAll: async () => {
    const response = await api.get('/sources/');
    return response.data;
  },
  create: async (data: Record<string, unknown>) => {
    const response = await api.post('/sources/', data);
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
  check: async (id: string) => {
    const response = await api.post(`/sources/${id}/check`);
    return response.data;
  },
  crawl: async (id: string) => {
    const response = await api.post(`/sources/${id}/crawl`);
    return response.data;
  },
  getCrawlHistory: async (id: string) => {
    const response = await api.get(`/sources/${id}/crawl-history`);
    return response.data;
  },
  getDiscovered: async () => {
    const response = await api.get('/discovery/sources');
    return response.data;
  },
  getTemplates: async () => {
    const response = await api.get('/sources/templates');
    return response.data;
  },
  renderTemplate: async (templateId: string, params: Record<string, unknown>) => {
    const response = await api.post(`/sources/templates/${templateId}/render`, params);
    return response.data;
  },
  addToWhitelist: async (domain: string) => {
    const response = await api.post('/whitelist/', { domain, status: 'trusted' });
    return response.data;
  },
  ignoreDiscovered: async (domain: string) => {
    const response = await api.post(`/sources/discovered/${domain}/ignore`);
    return response.data;
  },
  test: async (id: string) => {
    const response = await api.post(`/sources/${id}/test`);
    return response.data;
  }
};

export const contentApi = {
  getAll: async (params?: Record<string, unknown>) => {
    const response = await api.get('/contents/', { params });
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
  search: async (query: string) => {
    const response = await api.get('/contents/search', { params: { q: query } });
    return response.data;
  },
  submitUrl: async (url: string) => {
    const response = await api.post('/input/url', { url });
    return response.data;
  },
  submitText: async (content: string, title: string) => {
    const response = await api.post('/input/text', { content, title });
    return response.data;
  },
  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/input/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  getMetabolismStats: async () => {
    const response = await api.get('/content-management/metabolism/stats');
    return response.data;
  },
  archiveContent: async (contentId: string, reason: string) => {
    const response = await api.post(`/content-management/contents/${contentId}/archive`, { reason });
    return response.data;
  },
  restoreContent: async (contentId: string) => {
    const response = await api.post(`/content-management/contents/${contentId}/restore`);
    return response.data;
  },
  deleteContent: async (contentId: string) => {
    const response = await api.delete(`/content-management/contents/${contentId}`);
    return response.data;
  },
  cleanupArchived: async (days: number) => {
    const response = await api.post('/content-management/metabolism/cleanup', { retention_days: days });
    return response.data;
  }
};

export const approvalApi = {
  getAll: async (status?: string) => {
    const params = status ? { status } : {};
    const response = await api.get('/approvals/', { params });
    return response.data;
  },
  getPending: async () => {
    const response = await api.get('/approvals/pending');
    return response.data;
  },
  getHistory: async () => {
    const response = await api.get('/approvals/');
    return response.data;
  },
  approve: async (id: string) => {
    const response = await api.post(`/approvals/${id}/review`, { status: 'approved' });
    return response.data;
  },
  reject: async (id: string, reason: string) => {
    const response = await api.post(`/approvals/${id}/review`, { status: 'rejected', review_comment: reason });
    return response.data;
  },
  review: async (id: string, status: 'approved' | 'rejected', comment?: string, reviewerId?: string) => {
    const response = await api.post(`/approvals/${id}/review`, { status, review_comment: comment, reviewer_id: reviewerId });
    return response.data;
  },
  batchReview: async (ids: string[], action: 'approve' | 'reject', reason?: string) => {
    const response = await api.post('/approvals/batch/review', { ids, action, reason });
    return response.data;
  },
  cleanup: async (reason: string = 'Batch Cleanup') => {
    const response = await api.post('/approvals/cleanup', { reason });
    return response.data;
  },
  rollback: async (id: string) => {
    const response = await api.post(`/approvals/${id}/rollback`);
    return response.data;
  },
  execute: async (id: string) => {
    const response = await api.post(`/approvals/${id}/execute`);
    return response.data;
  },
  getById: async (id: string) => {
    const response = await api.get(`/approvals/${id}`);
    return response.data;
  },
  getImpact: async (id: string) => {
    const response = await api.get(`/approvals/${id}/impact`);
    return response.data;
  }
};

export const healthApi = {
  getReport: async () => {
    const response = await api.get('/health/report');
    return response.data;
  },
  runCheck: async () => {
    const response = await api.post('/health/check');
    return response.data;
  },
  triggerDetection: async () => {
    const response = await api.post('/health/check');
    return response.data;
  },
  getIssues: async () => {
    const response = await api.get('/health/issues');
    return response.data;
  }
};

export const dashboardApi = {
  getStats: async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },
  getHotspots: async () => {
    const response = await api.get('/dashboard/hotspots');
    return response.data;
  },
  getRecentActivity: async () => {
    const response = await api.get('/dashboard/activity');
    return response.data;
  },
  getTrend: async (days: number = 7) => {
    const response = await api.get('/dashboard/trend', { params: { days } });
    return response.data;
  }
};

export const schedulerApi = {
  getTasks: async () => {
    const response = await api.get('/scheduler/tasks');
    return response.data;
  },
  getExecutions: async (taskId?: string, limit: number = 20) => {
    const params = { task_id: taskId, limit };
    const response = await api.get('/scheduler/executions', { params });
    return response.data;
  },
  runTask: async (taskId: string) => {
    const response = await api.post(`/scheduler/tasks/${taskId}/trigger`);
    return response.data;
  },
  pause: async (taskId: string) => {
    const response = await api.put(`/scheduler/tasks/${taskId}/pause`);
    return response.data;
  },
  resume: async (taskId: string) => {
    const response = await api.put(`/scheduler/tasks/${taskId}/resume`);
    return response.data;
  }
};

export const configApi = {
  getAll: async () => {
    const response = await api.get('/config/');
    return response.data;
  },
  update: async (key: string, value: unknown, description?: string) => {
    const response = await api.put(`/config/${key}`, { value, description });
    return response.data;
  },
  getHistory: async (key?: string) => {
    const params = key ? { key } : {};
    const response = await api.get('/config/history', { params });
    return response.data;
  },
  testAIConnection: async (target: string = 'auto') => {
    const response = await api.post('/config/ai/test', null, { params: { target } });
    return response.data;
  }
};

export const evolutionApi = {
  getDriftReport: async () => {
    const response = await api.get('/evolution/drift/report');
    return response.data;
  },
  getStrategy: async () => {
    const response = await api.get('/strategy/current');
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
  triggerOptimization: async () => {
    const response = await api.post('/strategy/optimize');
    return response.data;
  }
};

export const contributionApi = {
  getStats: async (days: number = 30) => {
    const response = await api.get('/contributions/stats', { params: { days } });
    return response.data;
  },
  getAll: async (limit: number = 20, offset: number = 0) => {
    const response = await api.get('/contributions/', { params: { limit, skip: offset } });
    return response.data;
  },
  getHistory: async (limit: number = 20, offset: number = 0) => {
    const response = await api.get('/contributions/', { params: { limit, skip: offset } });
    return response.data;
  },
  getById: async (id: string) => {
    const response = await api.get(`/contributions/${id}`);
    return response.data;
  }
};

export const synonymApi = {
  getAll: async (params?: { skip?: number; limit?: number }) => {
    const response = await api.get('/synonyms', { params });
    return response.data;
  },
  search: async (query: string) => {
    const response = await api.get('/synonyms/search', { params: { q: query } });
    return response.data;
  },
  create: async (data: SynonymCreate) => {
    const response = await api.post('/synonyms/', data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await api.delete(`/synonyms/${id}`);
    return response.data;
  },
  getStandardTerms: async () => {
    const response = await api.get('/synonyms/standard-terms');
    return response.data;
  }
};

export const whitelistApi = {
  getAll: async () => {
    const response = await api.get('/whitelist/');
    return response.data;
  },
  add: async (data: { domain: string; credibility: number; reason: string }) => {
    const response = await api.post('/whitelist/', data);
    return response.data;
  },
  remove: async (id: string) => {
    const response = await api.delete(`/whitelist/${id}`);
    return response.data;
  }
};

export const discoveryApi = {
  getAll: async () => {
    const response = await api.get('/sources/discovered');
    return response.data;
  },
  getDiscoveredDomains: async () => {
    const response = await api.get('/whitelist/discovered');
    return response.data;
  },
  ignore: async (domain: string) => {
    const response = await api.post(`/sources/discovered/${domain}/ignore`);
    return response.data;
  }
};

export const metabolismApi = {
  run: async () => {
    const response = await api.post('/content-management/metabolism/run');
    return response.data;
  },
  getSuggestions: async () => {
    const response = await api.get('/content-management/metabolism/suggestions');
    return response.data;
  },
  cleanup: async (ids: string[]) => {
    const response = await api.post('/content-management/metabolism/cleanup', { ids });
    return response.data;
  }
};

export const contentManagementApi = {
  batchClean: async (data: { dry_run?: boolean; chinese_ratio_threshold?: number } = {}) => {
    const response = await api.post('/contents/batch/clean', {
      dry_run: data.dry_run ?? false,
      chinese_ratio_threshold: data.chinese_ratio_threshold ?? 0.2
    });
    return response.data;
  },
  batchSummarize: async (target_ids: string[] | undefined, overwrite: boolean) => {
    const response = await api.post('/contents/batch/summarize', { target_ids, overwrite });
    return response.data;
  },
  batchDelete: async (ids: string[]) => {
    const response = await api.post('/contents/batch/delete', { ids });
    return response.data;
  }
};

export const hotspotApi = {
  getTrending: async () => {
    const response = await api.get('/hotspots/trending');
    return response.data;
  },
  ignore: async (id: string) => {
    const response = await api.post(`/hotspots/${id}/ignore`);
    return response.data;
  },
  getAll: async (params?: { limit?: number; offset?: number; status?: string }) => {
    const response = await api.get('/hotspots', { params });
    return response.data;
  }
};

export const aiMonitorApi = {
  getMetrics: async (filters: Partial<MetricFilters> = {}) => {
    const params = { page: 1, page_size: 20, ...filters };
    const response = await api.get<PaginatedAIMetrics>('/ai-monitor/metrics', { params });
    return response.data;
  },
  getStats: async (timeRange: string = '24h') => {
    const response = await api.get<AIStats>('/ai-monitor/stats', { params: { time_range: timeRange } });
    return response.data;
  },
  cleanMetrics: async (days: number) => {
    const response = await api.post<{ deleted_count: number }>('/ai-monitor/clean', { days });
    return response.data;
  }
};

export default api;
