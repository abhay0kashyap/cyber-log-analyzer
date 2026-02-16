import axios from 'axios';

const API_BASE_URL = 'https://cyber-log-analyzer-5.onrender.com';
const WS_BASE_URL = import.meta.env.VITE_WS_URL || '';

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

function resolveWsUrl() {
  if (WS_BASE_URL) {
    return `${WS_BASE_URL.replace(/\/+$/, '')}/ws/updates`;
  }

  const base = API_BASE_URL.replace(/\/+$/, '');
  if (!base) {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    return `${protocol}://${window.location.host}/ws/updates`;
  }
  if (base.startsWith('https://')) {
    return `${base.replace('https://', 'wss://')}/ws/updates`;
  }
  if (base.startsWith('http://')) {
    return `${base.replace('http://', 'ws://')}/ws/updates`;
  }
  return `ws://${base}/ws/updates`;
}

export const api = {
  getHealth: async () => (await apiClient.get('/health')).data,

  getMetrics: async (range = '24h') => (await apiClient.get('/api/metrics', { params: { range } })).data,
  getSocAlerts: async (range = 'all') => (await apiClient.get('/api/alerts', { params: { range } })).data,
  getSocReport: async (range = '24h') => (await apiClient.get('/api/reports', { params: { range } })).data,
  getGeoFeed: async (range = '24h') => (await apiClient.get('/api/geo-feed', { params: { range } })).data,

  uploadLog: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return (
      await apiClient.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    ).data;
  },

  connectUpdates: (onUpdate) => {
    let socket;
    try {
      socket = new WebSocket(resolveWsUrl());
    } catch {
      return null;
    }

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'metrics_update') {
          onUpdate?.(payload);
        }
      } catch {
        // Ignore malformed WS payloads.
      }
    };

    return socket;
  },

  // Legacy endpoints retained for existing pages.
  getStats: async () => (await apiClient.get('/stats')).data,
  getDashboard: async (interval = '24h') => (await apiClient.get('/stats/dashboard', { params: { interval } })).data,
  getTimeline: async (interval = '24h') => (await apiClient.get('/stats/timeline', { params: { interval } })).data,
  getTopIps: async () => (await apiClient.get('/stats/top-ips')).data,
  getSeverityBreakdown: async () => (await apiClient.get('/stats/severity-breakdown')).data,

  getAlerts: async (params = {}) => (await apiClient.get('/alerts', { params })).data,
  getAlertDetails: async (alertId) => (await apiClient.get(`/alerts/${alertId}`)).data,
  updateAlertStatus: async (alertId, status) => (await apiClient.patch(`/alerts/${alertId}/status`, { status })).data,
  blockAlert: async (alertId) => (await apiClient.post(`/alerts/${alertId}/block`)).data,

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
