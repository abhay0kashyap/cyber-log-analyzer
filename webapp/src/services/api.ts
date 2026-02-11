/**
 * Cyber Log Analyzer – API Service
 * Centralized API layer for frontend ↔ backend communication
 */

const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

/* ===============================
   Types
================================ */

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
  latitude?: number;
  longitude?: number;
  is_proxy: boolean;
  is_hosting: boolean;
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
  recent_activity: {
    timestamp: string;
    type: string;
    ip: string;
    country?: string;
  }[];
}

export interface MonitorStatus {
  is_running: boolean;
}

/* ===============================
   Helper
================================ */

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "API request failed");
  }
  return response.json();
}

/* ===============================
   API Service
================================ */

class ApiService {
  private baseUrl = API_BASE_URL;

  /* ---------- Health ---------- */
  healthCheck() {
    return fetch(`${this.baseUrl}/api/health`).then((r) =>
      handleResponse<{ status: string; monitoring_active: boolean }>(r)
    );
  }

  /* ---------- Events ---------- */
  getEvents(params?: {
    event_type?: string;
    ip?: string;
    limit?: number;
    offset?: number;
  }) {
    const query = new URLSearchParams();

    if (params?.event_type) query.append("event_type", params.event_type);
    if (params?.ip) query.append("ip", params.ip);
    if (params?.limit) query.append("limit", String(params.limit));
    if (params?.offset) query.append("offset", String(params.offset));

    return fetch(`${this.baseUrl}/api/events?${query}`).then((r) =>
      handleResponse<Event[]>(r)
    );
  }

  getEventsStats() {
    return fetch(`${this.baseUrl}/api/events/stats`).then((r) =>
      handleResponse<{
        total_events: number;
        events_today: number;
        top_attacking_ips: { ip: string; count: number }[];
      }>(r)
    );
  }

  /* ---------- Alerts ---------- */
  getAlerts(params?: { active_only?: boolean; severity?: string }) {
    const query = new URLSearchParams();

    if (params?.active_only !== undefined)
      query.append("active_only", String(params.active_only));
    if (params?.severity) query.append("severity", params.severity);

    return fetch(`${this.baseUrl}/api/alerts?${query}`).then((r) =>
      handleResponse<Alert[]>(r)
    );
  }

  acknowledgeAlert(alertId: number) {
    return fetch(
      `${this.baseUrl}/api/alerts/${alertId}/acknowledge`,
      { method: "POST" }
    ).then((r) => handleResponse<{ message: string }>(r));
  }

  /* ---------- Intelligence ---------- */
  getIntelligence(limit?: number) {
    const url = limit
      ? `${this.baseUrl}/api/intelligence?limit=${limit}`
      : `${this.baseUrl}/api/intelligence`;

    return fetch(url).then((r) =>
      handleResponse<Intelligence[]>(r)
    );
  }

  getIpDetails(ip: string) {
    return fetch(`${this.baseUrl}/api/intelligence/${ip}`).then((r) =>
      handleResponse<{
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
      }>(r)
    );
  }

  /* ---------- Dashboard ---------- */
  getStats() {
    return fetch(`${this.baseUrl}/api/stats`).then((r) =>
      handleResponse<Stats>(r)
    );
  }

  /* ---------- Monitor ---------- */
  startMonitoring(threshold?: number) {
    const url = threshold
      ? `${this.baseUrl}/api/monitor/start?threshold=${threshold}`
      : `${this.baseUrl}/api/monitor/start`;

    return fetch(url, { method: "POST" }).then((r) =>
      handleResponse<MonitorStatus>(r)
    );
  }

  stopMonitoring() {
    return fetch(`${this.baseUrl}/api/monitor/stop`, {
      method: "POST",
    }).then((r) => handleResponse<MonitorStatus>(r));
  }

  getMonitorStatus() {
    return fetch(`${this.baseUrl}/api/monitor/status`).then((r) =>
      handleResponse<MonitorStatus>(r)
    );
  }

  /* ---------- Analysis ---------- */
  analyzeLogFile(threshold?: number) {
    const url = threshold
      ? `${this.baseUrl}/api/analyze?threshold=${threshold}`
      : `${this.baseUrl}/api/analyze`;

    return fetch(url, { method: "POST" }).then((r) =>
      handleResponse<{ message: string; threshold: number }>(r)
    );
  }

  /* ---------- Reports ---------- */
  async exportReport(): Promise<Blob> {
    const response = await fetch(
      `${this.baseUrl}/api/reports/export`
    );

    if (!response.ok) {
      throw new Error("Failed to export report");
    }

    return response.blob();
  }
}

/* ===============================
   Export
================================ */

const api = new ApiService();
export default api;
export { api };
