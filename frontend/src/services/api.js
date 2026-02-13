import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://cyber-log-analyzer-3.onrender.com';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Request failed';
    return Promise.reject(new Error(message));
  }
);

export const api = {
  getHealth: async () => (await apiClient.get('/health')).data,
  getStats: async () => (await apiClient.get('/stats')).data,
  getDashboard: async (interval = '24h') =>
    (await apiClient.get('/stats/dashboard', { params: { interval } })).data,
  getTimeline: async (interval = '24h') =>
    (await apiClient.get('/stats/timeline', { params: { interval } })).data,
  getTopIps: async () => (await apiClient.get('/stats/top-ips')).data,
  getSeverityBreakdown: async () => (await apiClient.get('/stats/severity-breakdown')).data,

  getAlerts: async (params = {}) => (await apiClient.get('/alerts', { params })).data,
  getAlertDetails: async (alertId) => (await apiClient.get(`/alerts/${alertId}`)).data,
  updateAlertStatus: async (alertId, status) => (await apiClient.patch(`/alerts/${alertId}/status`, { status })).data,
  blockAlert: async (alertId) => (await apiClient.post(`/alerts/${alertId}/block`)).data,

  uploadLog: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return (
      await apiClient.post('/logs/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    ).data;
  },

  getSettings: async () => (await apiClient.get('/settings')).data,
  saveSettings: async (payload) => (await apiClient.post('/settings', payload)).data,

  getReport: async () => (await apiClient.get('/reports/download')).data,
  downloadReportCsv: async () =>
    (
      await apiClient.get('/reports/download.csv', {
        responseType: 'blob',
      })
    ).data,
};
