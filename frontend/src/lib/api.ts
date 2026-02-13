import axios from 'axios';
import { HealthReport, Hotspot, ScheduledTask, TaskExecution, ConfigHistory, DriftProposal, VisualizationData, MergeRequest, SplitRequest, LinkRequest, NodeRelation, PyramidNode } from '../types';

const api = axios.create({
  // Use relative path to leverage Next.js rewrites in development
  // In production, prioritize environment variable, fallback to relative path if same-origin
  baseURL: process.env.NODE_ENV === 'production' 
    ? (process.env.NEXT_PUBLIC_API_URL || '/api/v1')
    : '/api/v1',
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
  create: async (data: any) => {
    const response = await api.post('/pyramids', data);
    return response.data;
  },
  update: async (id: string, data: any) => {
    const response = await api.put(`/pyramids/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await api.delete(`/pyramids/${id}`);
    return response.data;
  },
  addNode: async (pyramidId: string, data: any) => {
    const response = await api.post(`/pyramids/${pyramidId}/nodes`, data);
    return response.data;
  },
  mergeNodes: async (pyramidId: string, data: any) => {
    const response = await api.post(`/pyramids/${pyramidId}/merge-nodes`, data);
    return response.data;
  },
  getHealth: async (pyramidId: string) => {
    const response = await api.get(`/pyramids/${pyramidId}/health`);
    return response.data;
  },
  getVisualization: async (pyramidId: string) => {
    const response = await api.get(`/pyramids/${pyramidId}/visualization`);
    return response.data;
  },
  getHistory: async (pyramidId: string) => {
    const response = await api.get(`/pyramids/${pyramidId}/snapshots`);
    return response.data;
  }
};

export const nodeApi = {
  split: async (id: string, data: any) => {
    const response = await api.post(`/nodes/${id}/split`, data);
    return response.data;
  },
  link: async (id: string, data: any) => {
    const response = await api.post(`/nodes/${id}/link`, data);
    return response.data;
  },
  move: async (id: string, data: any) => {
    const response = await api.post(`/nodes/${id}/move`, data);
    return response.data;
  },
  get: async (id: string) => {
    const response = await api.get(`/nodes/${id}`);
    return response.data;
  },
  update: async (id: string, data: any) => {
    const response = await api.put(`/nodes/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await api.delete(`/nodes/${id}`);
    return response.data;
  }
};

export const sourceApi = {
  getAll: async () => {
    const response = await api.get('/sources');
    return response.data;
  },
  create: async (data: any) => {
    const response = await api.post('/sources', data);
    return response.data;
  },
  update: async (id: string, data: any) => {
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
  test: async (id: string) => {
    const response = await api.post(`/sources/${id}/test`);
    return response.data;
  }
};

export const contentApi = {
  getAll: async (params?: any) => {
    const response = await api.get('/contents', { params });
    return response.data;
  },
  getById: async (id: string) => {
    const response = await api.get(`/contents/${id}`);
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
  add: async (data: any) => {
    const response = await api.post('/whitelist', data);
    return response.data;
  },
  remove: async (id: string) => {
    const response = await api.delete(`/whitelist/${id}`);
    return response.data;
  },
  update: async (id: string, data: any) => {
    const response = await api.put(`/whitelist/${id}`, data);
    return response.data;
  },
};

export const dashboardApi = {
  getStats: async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  }
};

export const healthApi = {
  triggerDetection: async () => {
    const response = await api.post('/health/detection');
    return response.data;
  },
  getReport: async () => {
    const response = await api.get('/health/report');
    return response.data;
  },
  getSystemHealth: async () => {
    const response = await api.get('/health/system');
    return response.data;
  },
  getPyramidHealth: async (id: string) => {
    const response = await api.get(`/health/pyramids/${id}`);
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
    const response = await api.post('/evolution/optimize');
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
  update: async (key: string, value: any) => {
    const response = await api.put(`/config/${key}`, { value });
    return response.data;
  }
};
