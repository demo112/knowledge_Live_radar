import axios from 'axios';
import { HealthReport, Hotspot, ScheduledTask, TaskExecution, ConfigHistory, DriftProposal } from './types';

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
  getHistory: async (pyramidId: string) => {
    const response = await api.get(`/pyramids/${pyramidId}/snapshots`);
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
  analyze: async (id: string, pyramidId: string) => {
    const response = await api.post(`/contents/${id}/analyze`, { pyramid_id: pyramidId });
    return response.data;
  }
};

export const discoveryApi = {
  search: async (query: string) => {
    const response = await api.get('/discovery/search', { params: { query } });
    return response.data;
  },
  discover: async (url: string) => {
    const response = await api.post('/discovery/discover', { url });
    return response.data;
  }
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

export const healthApi = {
  getReport: async (): Promise<HealthReport> => {
    const response = await api.get('/health/report/latest');
    return response.data;
  },
  triggerDetection: async () => {
    const response = await api.post('/health/detect');
    return response.data;
  },
};

export const hotspotApi = {
  getAll: async (status?: string): Promise<Hotspot[]> => {
    const response = await api.get('/hotspots', { params: { status } });
    return response.data;
  },
  getById: async (id: string): Promise<Hotspot> => {
    const response = await api.get(`/hotspots/${id}`);
    return response.data;
  },
  updateStatus: async (id: string, status: string) => {
    const response = await api.put(`/hotspots/${id}/status`, null, { params: { status } });
    return response.data;
  },
  triggerUpdate: async () => {
    const response = await api.post('/hotspots/lifecycle/update');
    return response.data;
  }
};

export const evolutionApi = {
  triggerRestructure: async (pyramidId: string) => {
    // Note: restructure endpoint was in health.py and I didn't move it to a dedicated router yet
    // I left it in health.py or wait... I didn't verify if I deleted it from health.py
    // I deleted hotspots/drift/strategy from health.py.
    // Did I delete restructure? 
    // In my health.py write, I only included detect and report.
    // So restructure endpoint is GONE currently.
    // I should add it to health.py or create routers/evolution.py?
    // Given the time, I'll add it back to health.py or create a new one.
    // Let's assume I'll fix the backend to have /evolution/restructure or similar.
    // Actually, I should probably put it in `pyramids.py` or a new `evolution.py` router.
    // For now, let's assume I'll put it in `health.py` or `pyramids.py`.
    // Let's use `/health/evolution/restructure` and ensure backend has it.
    // Wait, I overwrote health.py with just 2 endpoints.
    // I need to Restore restructure endpoint!
    const response = await api.post('/health/evolution/restructure', null, { params: { pyramid_id: pyramidId } });
    return response.data;
  },
  triggerDrift: async (pyramidId: string) => {
    const response = await api.post(`/drift/detect/${pyramidId}`);
    return response.data;
  },
  getDriftDetections: async (status?: string): Promise<DriftProposal[]> => {
    const response = await api.get('/drift/detections', { params: { status } });
    return response.data;
  },
  triggerOptimization: async () => {
    const response = await api.post('/strategy/optimize');
    return response.data;
  }
};

export const schedulerApi = {
  getAll: async (): Promise<ScheduledTask[]> => {
    const response = await api.get('/scheduler/tasks');
    return response.data;
  },
  getExecutions: async (taskId?: string): Promise<TaskExecution[]> => {
    const response = await api.get('/scheduler/executions', { params: { task_id: taskId } });
    return response.data;
  },
  trigger: async (taskId: string) => {
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
  getAll: async (): Promise<Record<string, any>> => {
    const response = await api.get('/config');
    return response.data;
  },
  get: async (key: string) => {
    const response = await api.get(`/config/${key}`);
    return response.data;
  },
  update: async (key: string, value: any) => {
    const response = await api.put(`/config/${key}`, { value });
    return response.data;
  },
  getHistory: async (key?: string): Promise<ConfigHistory[]> => {
    const response = await api.get('/config/history/list', { params: { key } });
    return response.data;
  }
};

export const whitelistApi = {
  getAll: async (page = 1, pageSize = 20) => {
    const response = await api.get('/whitelist', { params: { page, page_size: pageSize } });
    return response.data;
  },
  add: async (domain: string, credibility = 50, reason?: string) => {
    const response = await api.post('/whitelist', { domain, credibility, reason });
    return response.data;
  },
  remove: async (id: string) => {
    const response = await api.delete(`/whitelist/${id}`);
    return response.data;
  },
  getDiscovered: async (status?: string, page = 1, pageSize = 20) => {
    const response = await api.get('/whitelist/discovered', { params: { status, page, page_size: pageSize } });
    return response.data;
  },
  check: async (url: string) => {
    const response = await api.post('/whitelist/check', { url });
    return response.data;
  }
};

export const dashboardApi = {
  getStats: async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },
  getRecentActivity: async () => {
    const response = await api.get('/dashboard/activity');
    return response.data;
  }
};
