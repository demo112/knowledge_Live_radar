import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
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

export const approvalApi = {
  getAll: async (status?: string) => {
    const response = await api.get('/approvals', { params: { status } });
    return response.data;
  },
  getPending: async () => {
    const response = await api.get('/approvals/pending');
    return response.data;
  },
  getById: async (id: string) => {
    const response = await api.get(`/approvals/${id}`);
    return response.data;
  },
  review: async (id: string, status: 'approved' | 'rejected', comment?: string, reviewerId?: string) => {
    const response = await api.post(`/approvals/${id}/review`, { 
      status, 
      review_comment: comment,
      reviewer_id: reviewerId 
    });
    return response.data;
  },
  execute: async (id: string) => {
    const response = await api.post(`/approvals/${id}/execute`);
    return response.data;
  }
};

export const discoveryApi = {
  discover: async (url: string) => {
    const response = await api.post('/discovery/discover', { url });
    return response.data;
  }
};

export default api;
