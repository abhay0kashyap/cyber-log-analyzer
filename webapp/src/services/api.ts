/**
 * Cyber Log Analyzer - API Service
 * Handles all API communication with the backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface Event {
  id: number;
  timestamp: string;
  event_type: string;
  ip_address: string;
  country?: string;
  city?: string;
  isp?: string;
  asn?: string;
  latitude?: number;
  longitude?: number;
  is_proxy: boolean;
  is_hosting: boolean;
}

export interface Alert {
  id: number;
  timestamp: string;
  alert_type: string;
  severity: string;
  source_ip: string;
  description: string;
  is_active: boolean;
  acknowledged: boolean;
}

export interface Intelligence {
  id: number;
  ip_address: string;
  first_seen: string;
  last_seen: string;
  total_attempts: number;
  country?: string;
  city?: string;
  isp?: string;
  asn?: string;
  is_proxy: boolean;
  is_hosting: boolean;
  latitude?: number;
  longitude?: number;
  threat_level: string;
}

export interface Stats {
  total_events: number;
  total_attacks: number;
  unique_ips: number;
  active_alerts: number;
  events_today: number;
  attacks_today: number;
  top_countries: { country: string; count: number }[];
  recent_activity: { timestamp: string; type: string; ip: string; country?: string }[];
}

export interface MonitorStatus {
  is_running: boolean;
}

class ApiService {
  private baseUrl = API_BASE_URL;

  // Health Check
  async healthCheck(): Promise<{ status: string; monitoring_active: boolean }> {
    const response = await fetch(`${this.baseUrl}/api/health`);
    return response.json();
  }

  // Events
  async getEvents(params?: { 
    event_type?: string; 
    ip?: string; 
    limit?: number; 
    offset?: number 
  }): Promise<Event[]> {
    const queryParams = new URLSearchParams();
    if (params?.event_type) queryParams.append('event_type', params.event_type);
    if (params?.ip) queryParams.append('ip', params.ip);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());

    const response = await fetch(
      `${this.baseUrl}/api/events?${queryParams.toString()}`
    );
    return response.json();
  }

  async getEventsStats(): Promise<{
    total_events: number;
    events_today: number;
    top_attacking_ips: { ip: string; count: number }[];
  }> {
    const response = await fetch(`${this.baseUrl}/api/events/stats`);
    return response.json();
  }

  // Alerts
  async getAlerts(params?: { active_only?: boolean; severity?: string }): Promise<Alert[]> {
    const queryParams = new URLSearchParams();
    if (params?.active_only !== undefined) 
      queryParams.append('active_only', params.active_only.toString());
    if (params?.severity) queryParams.append('severity', params.severity);

    const response = await fetch(
      `${this.baseUrl}/api/alerts?${queryParams.toString()}`
    );
    return response.json();
  }

  async acknowledgeAlert(alertId: number): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/api/alerts/${alertId}/acknowledge`, {
      method: 'POST',
    });
    return response.json();
  }

  // Intelligence
  async getIntelligence(limit?: number): Promise<Intelligence[]> {
    const url = limit 
      ? `${this.baseUrl}/api/intelligence?limit=${limit}`
      : `${this.baseUrl}/api/intelligence`;
    const response = await fetch(url);
    return response.json();
  }

  async getIpDetails(ip: string): Promise<{
    ip: string;
    cached: boolean;
    country?: string;
    city?: string;
    isp?: string;
    asn?: string;
    latitude?: number;
    longitude?: number;
    is_proxy?: boolean;
    is_hosting?: boolean;
    map_url?: string;
  }> {
    const response = await fetch(`${this.baseUrl}/api/intelligence/${ip}`);
    return response.json();
  }

  // Dashboard Stats
  async getStats(): Promise<Stats> {
    const response = await fetch(`${this.baseUrl}/api/stats`);
    return response.json();
  }

  // Monitor Control
  async startMonitoring(threshold?: number): Promise<MonitorStatus> {
    const url = threshold 
      ? `${this.baseUrl}/api/monitor/start?threshold=${threshold}`
      : `${this.baseUrl}/api/monitor/start`;
    const response = await fetch(url, { method: 'POST' });
    return response.json();
  }

  async stopMonitoring(): Promise<MonitorStatus> {
    const response = await fetch(`${this.baseUrl}/api/monitor/stop`, {
      method: 'POST',
    });
    return response.json();
  }

  async getMonitorStatus(): Promise<MonitorStatus> {
    const response = await fetch(`${this.baseUrl}/api/monitor/status`);
    return response.json();
  }

  // Analysis
  async analyzeLogFile(threshold?: number): Promise<{ message: string; threshold: number }> {
    const url = threshold 
      ? `${this.baseUrl}/api/analyze?threshold=${threshold}`
      : `${this.baseUrl}/api/analyze`;
    const response = await fetch(url, { method: 'POST' });
    return response.json();
  }

  // Reports
  async exportReport(): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/reports/export`);
    return response.blob();
  }
}

export const api = new ApiService();
export default api;

