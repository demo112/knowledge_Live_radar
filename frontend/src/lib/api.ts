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
  }
};

export const discoveryApi = {
  discover: async (url: string) => {
    const response = await api.post('/discovery/discover', { url });
    return response.data;
  }
};

export default api;
