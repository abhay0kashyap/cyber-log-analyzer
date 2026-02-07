/**
 * Cyber Log Analyzer - Main Dashboard Component
 * SIEM-style security monitoring dashboard
 */

import React, { useState, useEffect, useCallback, ChangeEvent } from 'react';
import { Container, Row, Col, Card, Badge, Button, Table, Form, Alert, Spinner } from 'react-bootstrap';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import api, { Stats, Alert as AlertType, Intelligence } from '../services/api';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [alerts, setAlerts] = useState<AlertType[]>([]);
  const [intelligence, setIntelligence] = useState<Intelligence[]>([]);
  const [monitorStatus, setMonitorStatus] = useState<{ is_running: boolean }>({ is_running: false });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [threshold, setThreshold] = useState(3);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'events' | 'alerts' | 'intelligence'>('dashboard');

  // Fetch all data
  const fetchData = useCallback(async () => {
    try {
      const [statsData, alertsData, intelData, monitorData] = await Promise.all([
        api.getStats(),
        api.getAlerts({ active_only: true }),
        api.getIntelligence(50),
        api.getMonitorStatus()
      ]);
      setStats(statsData);
      setAlerts(alertsData);
      setIntelligence(intelData);
      setMonitorStatus(monitorData);
      setError(null);
    } catch (err) {
      setError('Failed to fetch data from API. Make sure the backend is running.');
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch and auto-refresh
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [fetchData]);

  // Monitor control handlers
  const handleStartMonitor = async () => {
    try {
      await api.startMonitoring(threshold);
      setMonitorStatus({ is_running: true });
    } catch (err) {
      setError('Failed to start monitoring');
    }
  };

  const handleStopMonitor = async () => {
    try {
      await api.stopMonitoring();
      setMonitorStatus({ is_running: false });
    } catch (err) {
      setError('Failed to stop monitoring');
    }
  };

  const handleAnalyze = async () => {
    try {
      await api.analyzeLogFile(threshold);
      fetchData();
    } catch (err) {
      setError('Failed to analyze log file');
    }
  };

  const handleAcknowledgeAlert = async (alertId: number) => {
    try {
      await api.acknowledgeAlert(alertId);
      fetchData();
    } catch (err) {
      setError('Failed to acknowledge alert');
    }
  };

  const getSeverityVariant = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'danger';
      case 'high': return 'warning';
      case 'medium': return 'info';
      default: return 'secondary';
    }
  };

  const getThreatLevelVariant = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical': return 'danger';
      case 'high': return 'warning';
      case 'medium': return 'info';
      default: return 'success';
    }
  };

  // Generate chart data from stats
  const chartData = stats?.recent_activity?.slice(0, 10).reverse().map((item, index) => ({
    time: new Date(item.timestamp).toLocaleTimeString(),
    attacks: index + 1,
    events: index + 1
  })) || [];

  if (loading) {
    return (
      <div className="loading-container">
        <Spinner animation="border" variant="primary" />
        <p className="mt-3">Loading Cyber Log Analyzer...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <Container fluid>
          <Row className="align-items-center">
            <Col md={6}>
              <h1 className="dashboard-title">
                🛡️ Cyber Log Analyzer <small className="text-muted">SIEM System</small>
              </h1>
            </Col>
            <Col md={6}>
              <div className="header-controls">
                <Badge bg={monitorStatus.is_running ? 'success' : 'secondary'} className="me-3">
                  {monitorStatus.is_running ? '● Live Monitoring' : '○ Monitoring Off'}
                </Badge>
                <Button 
                  variant={monitorStatus.is_running ? 'danger' : 'success'} 
                  size="sm"
                  onClick={monitorStatus.is_running ? handleStopMonitor : handleStartMonitor}
                >
                  {monitorStatus.is_running ? 'Stop' : 'Start'} Monitor
                </Button>
              </div>
            </Col>
          </Row>
        </Container>
      </header>

      {/* Error Alert */}
      {error && (
        <Container fluid className="px-4">
          <Alert variant="danger" dismissible onClose={() => setError(null)}>
            {error}
          </Alert>
        </Container>
      )}

      {/* Navigation Tabs */}
      <Container fluid className="px-4 mt-3">
        <Row>
          <Col>
            <nav className="dashboard-nav">
              <Button 
                variant={activeTab === 'dashboard' ? 'primary' : 'outline-primary'}
                className="me-2"
                onClick={() => setActiveTab('dashboard')}
              >
                Dashboard
              </Button>
              <Button 
                variant={activeTab === 'events' ? 'primary' : 'outline-primary'}
                className="me-2"
                onClick={() => setActiveTab('events')}
              >
                Events
              </Button>
              <Button 
                variant={activeTab === 'alerts' ? 'primary' : 'outline-primary'}
                className="me-2"
                onClick={() => setActiveTab('alerts')}
              >
                Alerts
                {alerts.length > 0 && <Badge bg="danger" className="ms-2">{alerts.length}</Badge>}
              </Button>
              <Button 
                variant={activeTab === 'intelligence' ? 'primary' : 'outline-primary'}
                onClick={() => setActiveTab('intelligence')}
              >
                Intelligence
              </Button>
            </nav>
          </Col>
        </Row>
      </Container>

      {/* Dashboard Content */}
      <Container fluid className="px-4 mt-4">
        
        {/* STATS CARDS */}
        <Row className="mb-4">
          <Col md={3}>
            <Card className="stat-card">
              <Card.Body>
                <Card.Title>Total Events</Card.Title>
                <div className="stat-value">{stats?.total_events || 0}</div>
                <small className="text-muted">{stats?.events_today || 0} today</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stat-card">
              <Card.Body>
                <Card.Title>Total Attacks</Card.Title>
                <div className="stat-value">{stats?.total_attacks || 0}</div>
                <small className="text-muted">{stats?.attacks_today || 0} today</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stat-card">
              <Card.Body>
                <Card.Title>Unique IPs</Card.Title>
                <div className="stat-value">{stats?.unique_ips || 0}</div>
                <small className="text-muted">attackers detected</small>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stat-card alert-card">
              <Card.Body>
                <Card.Title>Active Alerts</Card.Title>
                <div className="stat-value text-danger">{stats?.active_alerts || 0}</div>
                <small className="text-muted">requiring attention</small>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* MONITORING CONTROLS */}
        <Row className="mb-4">
          <Col md={12}>
            <Card>
              <Card.Body>
                <Row className="align-items-center">
                  <Col md={4}>
                    <h5>⚙️ Monitoring Configuration</h5>
                  </Col>
                  <Col md={3}>
                  <Form.Group>
                    <Form.Label>Failed Attempts Threshold</Form.Label>
                    <Form.Control 
                      type="number" 
                      value={threshold}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => setThreshold(Number(e.target.value))}
                      min={1}
                      max={20}
                    />
                  </Form.Group>
                  </Col>
                  <Col md={5}>
                    <Button variant="primary" onClick={handleAnalyze} className="me-2">
                      📊 Analyze Logs
                    </Button>
                    <Button 
                      variant={monitorStatus.is_running ? 'danger' : 'success'}
                      onClick={monitorStatus.is_running ? handleStopMonitor : handleStartMonitor}
                    >
                      {monitorStatus.is_running ? '⏹ Stop' : '▶ Start'} Real-time
                    </Button>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* MAIN CONTENT AREA */}
        {activeTab === 'dashboard' && (
          <Row>
            {/* Chart */}
            <Col md={8}>
              <Card>
                <Card.Header>
                  <Card.Title>Attack Activity Over Time</Card.Title>
                </Card.Header>
                <Card.Body>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="events" stroke="#8884d8" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </Card.Body>
              </Card>
            </Col>

            {/* Top Countries */}
            <Col md={4}>
              <Card>
                <Card.Header>
                  <Card.Title>🌍 Top Attacking Countries</Card.Title>
                </Card.Header>
                <Card.Body>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={stats?.top_countries?.slice(0, 5) || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="country" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#82ca9d" />
                    </BarChart>
                  </ResponsiveContainer>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        )}

        {/* EVENTS TAB */}
        {activeTab === 'events' && (
          <Row>
            <Col md={12}>
              <Card>
                <Card.Header>
                  <Card.Title>📋 Security Events Log</Card.Title>
                </Card.Header>
                <Card.Body>
                  <Table striped bordered hover responsive>
                    <thead>
                      <tr>
                        <th>Timestamp</th>
                        <th>Type</th>
                        <th>IP Address</th>
                        <th>Country</th>
                        <th>City</th>
                        <th>ISP</th>
                        <th>Proxy</th>
                        <th>Hosting</th>
                      </tr>
                    </thead>
                    <tbody>
                      {intelligence.map((intel) => (
                        <tr key={intel.id}>
                          <td>{new Date(intel.last_seen).toLocaleString()}</td>
                          <td>
                            <Badge bg="info">Attack</Badge>
                          </td>
                          <td className="font-monospace">{intel.ip_address}</td>
                          <td>{intel.country || 'Unknown'}</td>
                          <td>{intel.city || 'Unknown'}</td>
                          <td>{intel.isp || 'Unknown'}</td>
                          <td>
                            {intel.is_proxy ? (
                              <Badge bg="warning">Yes</Badge>
                            ) : (
                              <Badge bg="secondary">No</Badge>
                            )}
                          </td>
                          <td>
                            {intel.is_hosting ? (
                              <Badge bg="danger">Yes</Badge>
                            ) : (
                              <Badge bg="secondary">No</Badge>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        )}

        {/* ALERTS TAB */}
        {activeTab === 'alerts' && (
          <Row>
            <Col md={12}>
              <Card>
                <Card.Header>
                  <Card.Title>🚨 Active Security Alerts</Card.Title>
                </Card.Header>
                <Card.Body>
                  {alerts.length === 0 ? (
                    <Alert variant="success">
                      ✅ No active alerts. Your system is secure.
                    </Alert>
                  ) : (
                    <Table striped bordered hover responsive>
                      <thead>
                        <tr>
                          <th>Timestamp</th>
                          <th>Type</th>
                          <th>Severity</th>
                          <th>Source IP</th>
                          <th>Description</th>
                          <th>Status</th>
                          <th>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {alerts.map((alert) => (
                          <tr key={alert.id}>
                            <td>{new Date(alert.timestamp).toLocaleString()}</td>
                            <td>
                              <Badge bg="primary">{alert.alert_type}</Badge>
                            </td>
                            <td>
                              <Badge bg={getSeverityVariant(alert.severity)}>
                                {alert.severity}
                              </Badge>
                            </td>
                            <td className="font-monospace">{alert.source_ip}</td>
                            <td>{alert.description}</td>
                            <td>
                              {alert.acknowledged ? (
                                <Badge bg="success">Acknowledged</Badge>
                              ) : (
                                <Badge bg="warning">Pending</Badge>
                              )}
                            </td>
                            <td>
                              {!alert.acknowledged && (
                                <Button 
                                  variant="outline-primary" 
                                  size="sm"
                                  onClick={() => handleAcknowledgeAlert(alert.id)}
                                >
                                  Acknowledge
                                </Button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>
        )}

        {/* INTELLIGENCE TAB */}
        {activeTab === 'intelligence' && (
          <Row>
            <Col md={12}>
              <Card>
                <Card.Header>
                  <Card.Title>🕵️ Attacker Intelligence</Card.Title>
                </Card.Header>
                <Card.Body>
                  <Table striped bordered hover responsive>
                    <thead>
                      <tr>
                        <th>IP Address</th>
                        <th>Total Attempts</th>
                        <th>Threat Level</th>
                        <th>Country</th>
                        <th>City</th>
                        <th>ISP / ASN</th>
                        <th>Proxy</th>
                        <th>Hosting</th>
                        <th>First Seen</th>
                        <th>Last Seen</th>
                      </tr>
                    </thead>
                    <tbody>
                      {intelligence.map((intel) => (
                        <tr key={intel.id}>
                          <td className="font-monospace fw-bold">{intel.ip_address}</td>
                          <td>
                            <Badge bg="danger">{intel.total_attempts}</Badge>
                          </td>
                          <td>
                            <Badge bg={getThreatLevelVariant(intel.threat_level)}>
                              {intel.threat_level}
                            </Badge>
                          </td>
                          <td>{intel.country || 'Unknown'}</td>
                          <td>{intel.city || 'Unknown'}</td>
                          <td>
                            <small>
                              {intel.isp}<br />
                              <span className="text-muted">{intel.asn}</span>
                            </small>
                          </td>
                          <td>
                            {intel.is_proxy ? (
                              <Badge bg="warning">Proxy</Badge>
                            ) : (
                              <Badge bg="secondary">No</Badge>
                            )}
                          </td>
                          <td>
                            {intel.is_hosting ? (
                              <Badge bg="danger">Hosting</Badge>
                            ) : (
                              <Badge bg="secondary">No</Badge>
                            )}
                          </td>
                          <td>{new Date(intel.first_seen).toLocaleDateString()}</td>
                          <td>{new Date(intel.last_seen).toLocaleDateString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        )}

        {/* Recent Activity Footer */}
        <Row className="mt-4">
          <Col md={12}>
            <Card>
              <Card.Header>
                <Card.Title>📊 Recent Activity Feed</Card.Title>
              </Card.Header>
              <Card.Body>
                {stats?.recent_activity && stats.recent_activity.length > 0 ? (
                  <div className="activity-feed">
                    {stats.recent_activity.slice(0, 5).map((activity, index) => (
                      <div key={index} className="activity-item">
                        <Badge 
                          bg={activity.type === 'attack_detected' ? 'danger' : 'info'}
                          className="me-2"
                        >
                          {activity.type === 'attack_detected' ? '⚠️ Attack' : '🔒 Login'}
                        </Badge>
                        <span className="font-monospace">{activity.ip}</span>
                        <span className="text-muted ms-2">
                          {activity.country || 'Unknown'} • {new Date(activity.timestamp).toLocaleString()}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <Alert variant="info">No recent activity to display.</Alert>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>

      </Container>

      {/* Footer */}
      <footer className="dashboard-footer">
        <Container fluid>
          <Row>
            <Col className="text-center text-muted">
              🛡️ Cyber Log Analyzer • SIEM System • Built with React & FastAPI
            </Col>
          </Row>
        </Container>
      </footer>
    </div>
  );
};

export default Dashboard;

