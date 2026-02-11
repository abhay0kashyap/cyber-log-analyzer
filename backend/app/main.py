"""
Cyber Log Analyzer - SIEM System Backend
FastAPI-based backend for real-time security monitoring and log analysis.
"""

import asyncio
import os
import sys
import csv
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import Counter

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uvicorn
import re

# Import existing log analysis modules
from src.parser import get_failed_login_ips
from src.detector import detect_bruteforce
from src.geoip import get_ip_details as get_ip_info
from src.alert import send_email_alert as send_alert_email

# ============================================================================
# DATABASE SETUP
# ============================================================================

DATABASE_URL = "sqlite:///./cyber_logs.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================================
# DATABASE MODELS
# ============================================================================

class SecurityEvent(Base):
    """Model for storing security events from log analysis"""
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    event_type = Column(String, index=True)  # 'failed_login', 'attack_detected'
    ip_address = Column(String, index=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    isp = Column(String, nullable=True)
    asn = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    map_url = Column(String, nullable=True)
    is_proxy = Column(Boolean, default=False)
    is_hosting = Column(Boolean, default=False)
    raw_log = Column(Text, nullable=True)

class Alert(Base):
    """Model for storing active alerts"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    alert_type = Column(String)  # 'bruteforce', 'suspicious_activity'
    severity = Column(String)  # 'low', 'medium', 'high', 'critical'
    source_ip = Column(String, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    acknowledged = Column(Boolean, default=False)

class AttackerIntelligence(Base):
    """Model for storing attacker intelligence"""
    __tablename__ = "attacker_intelligence"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, index=True)
    first_seen = Column(DateTime, default=datetime.now)
    last_seen = Column(DateTime, default=datetime.now)
    total_attempts = Column(Integer, default=0)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    isp = Column(String, nullable=True)
    asn = Column(String, nullable=True)
    is_proxy = Column(Boolean, default=False)
    is_hosting = Column(Boolean, default=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    threat_level = Column(String, default="low")  # 'low', 'medium', 'high', 'critical'

# Create tables
Base.metadata.create_all(bind=engine)

# ============================================================================
# PYDANTIC MODELS (API Schemas)
# ============================================================================

class EventResponse(BaseModel):
    """Response model for security events"""
    id: int
    timestamp: datetime
    event_type: str
    ip_address: str
    country: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None
    asn: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_proxy: bool = False
    is_hosting: bool = False
    
    class Config:
        from_attributes = True

class AlertResponseModel(BaseModel):
    """Response model for alerts"""
    id: int
    timestamp: datetime
    alert_type: str
    severity: str
    source_ip: str
    description: str
    is_active: bool
    acknowledged: bool
    
    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    """Response model for dashboard statistics"""
    total_events: int
    total_attacks: int
    unique_ips: int
    active_alerts: int
    events_today: int
    attacks_today: int
    top_countries: List[Dict]
    recent_activity: List[Dict]

class MonitorControlResponse(BaseModel):
    """Response for monitor control actions"""
    status: str
    message: str
    is_running: bool

# ============================================================================
# GLOBAL STATE
# ============================================================================

monitoring_active = False
monitor_task = None

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# BACKGROUND MONITORING
# ============================================================================

async def monitor_logs_background(threshold: int = 3):
    """
    Background task for real-time log monitoring.
    Monitors the auth.log file and detects attacks.
    """
    global monitoring_active
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_file = os.path.join(base_dir, "logs", "auth.log")
    last_position = 0
    
    print(f"🔍 Starting real-time monitoring (threshold: {threshold})")
    
    while monitoring_active:
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    f.seek(last_position)
                    new_lines = f.readlines()
                    last_position = f.tell()
                    
                    if not new_lines: # Optimization: if no new lines, skip DB session creation
                        await asyncio.sleep(2) # Wait before checking again
                        continue # Continue to next iteration of while loop

                    db = SessionLocal() # Create session once per loop iteration
                    try:
                        for line in new_lines:
                            if "Failed password" in line:
                                # Extract IP from log line
                                ip_pattern = r"\b\d{1,3}(?:\.\d{1,3}){3}\b"
                                match = re.search(ip_pattern, line)
                                
                                if match:
                                    ip = match.group()
                                    await process_failed_login(ip, line, db) # Pass db session
                        
                        # After processing all new lines, check for alerts based on updated intelligence
                        # Query AttackerIntelligence for IPs that have met the threshold and don't have an active alert
                        ips_to_check_for_alerts = db.query(AttackerIntelligence).filter(
                            AttackerIntelligence.total_attempts >= threshold,
                            ~AttackerIntelligence.ip_address.in_(
                                db.query(Alert.source_ip).filter(Alert.is_active == True)
                            )
                        ).all()

                        for intel in ips_to_check_for_alerts:
                            await create_alert_if_needed(db, intel.ip_address, intel.total_attempts)
                    finally:
                        db.close() # Close session after loop iteration
                    
        except Exception as e:
            print(f"Monitor error: {e}")
        
        await asyncio.sleep(2)  # Check every 2 seconds

async def process_failed_login(ip: str, raw_log: str, db: Session):
    """Process a failed login attempt"""
    # db session is now always passed in and managed by the caller (monitor_logs_background)
    
    try:
        # Get geo-ip information
        ip_info = get_ip_info(ip)
        if not ip_info:
            ip_info = {}
        
        # Create security event
        event = SecurityEvent(
            event_type="failed_login",
            ip_address=ip,
            country=ip_info.get("country"),
            city=ip_info.get("city"),
            isp=ip_info.get("isp"),
            asn=ip_info.get("asn"),
            latitude=ip_info.get("lat"),
            longitude=ip_info.get("lon"),
            map_url=ip_info.get("map_url"),
            is_proxy=ip_info.get("proxy", False),
            is_hosting=ip_info.get("hosting", False),
            raw_log=raw_log.strip()
        )
        db.add(event)
        
        # Update or create attacker intelligence
        intel = db.query(AttackerIntelligence).filter(
            AttackerIntelligence.ip_address == ip
        ).first()
        
        if intel:
            intel.last_seen = datetime.now()
            intel.total_attempts += 1
        else:
            intel = AttackerIntelligence(
                ip_address=ip,
                total_attempts=1,
                country=ip_info.get("country"),
                city=ip_info.get("city"),
                isp=ip_info.get("isp"),
                asn=ip_info.get("asn"),
                latitude=ip_info.get("lat"),
                longitude=ip_info.get("lon"),
                is_proxy=ip_info.get("proxy", False),
                is_hosting=ip_info.get("hosting", False)
            )
            db.add(intel)
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error processing failed login for IP {ip}: {e}")

async def create_alert_if_needed(db: Session, ip: str, attempts: int):
    """Create an alert if one doesn't already exist"""
    existing = db.query(Alert).filter(
        Alert.source_ip == ip,
        Alert.is_active == True
    ).first()
    
    if not existing:
        severity = "high" if attempts > 10 else "medium"
        alert = Alert(
            alert_type="bruteforce",
            severity=severity,
            source_ip=ip,
            description=f"Brute-force attack detected: {attempts} failed login attempts from {ip}",
            is_active=True
        )
        db.add(alert)
        db.commit()
        
        # Send email alert (non-blocking)
        try:
            send_alert_email(ip, attempts)
        except Exception as e:
            print(f"Failed to send email alert: {e}")

# ============================================================================
# API ROUTES
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context for startup and shutdown"""
    # Startup
    print("🚀 Cyber Log Analyzer API starting...")
    yield
    # Shutdown
    global monitoring_active
    monitoring_active = False
    print("🛑 Cyber Log Analyzer API stopped.")

app = FastAPI(
    title="Cyber Log Analyzer API",
    description="SIEM-style security monitoring and log analysis API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------------
# Health & Status
# ----------------------------------------------------------------------------

@app.get("/api/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "service": "cyber-log-analyzer",
        "timestamp": datetime.now(),
        "monitoring_active": monitoring_active
    }

# ----------------------------------------------------------------------------
# Events API
# ----------------------------------------------------------------------------

@app.get("/api/events", response_model=List[EventResponse])
async def get_events(
    db: Session = Depends(get_db),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    ip: Optional[str] = Query(None, description="Filter by IP address"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Skip results")
):
    """Get all security events with optional filters"""
    query = db.query(SecurityEvent)
    
    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type)
    if ip:
        query = query.filter(SecurityEvent.ip_address == ip)
    
    events = query.order_by(SecurityEvent.timestamp.desc()).offset(offset).limit(limit).all()
    return events

@app.get("/api/events/stats")
async def get_events_stats(db: Session = Depends(get_db)):
    """Get statistics about security events"""
    total = db.query(SecurityEvent).count()
    today = datetime.now().date()
    events_today = db.query(SecurityEvent).filter(
        SecurityEvent.timestamp >= today
    ).count()
    
    # Top attacking IPs
    ip_counts = db.query(
        SecurityEvent.ip_address,
        func.count(SecurityEvent.id).label('count')
    ).group_by(SecurityEvent.ip_address).order_by(
        func.count(SecurityEvent.id).desc()
    ).limit(10).all()
    
    top_ips = [{"ip": ip, "count": count} for ip, count in ip_counts]
    
    return {
        "total_events": total,
        "events_today": events_today,
        "top_attacking_ips": top_ips
    }

# ----------------------------------------------------------------------------
# Alerts API
# ----------------------------------------------------------------------------

@app.get("/api/alerts", response_model=List[AlertResponseModel])
async def get_alerts(
    db: Session = Depends(get_db),
    active_only: bool = Query(True, description="Show only active alerts"),
    severity: Optional[str] = Query(None, description="Filter by severity")
):
    """Get all alerts with optional filters"""
    query = db.query(Alert)
    
    if active_only:
        query = query.filter(Alert.is_active == True)
    if severity:
        query = query.filter(Alert.severity == severity)
    
    alerts = query.order_by(Alert.timestamp.desc()).all()
    return alerts

@app.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """Acknowledge an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.acknowledged = True
    alert.is_active = False
    db.commit()
    
    return {"message": "Alert acknowledged"}

# ----------------------------------------------------------------------------
# Attacker Intelligence API
# ----------------------------------------------------------------------------

@app.get("/api/intelligence")
async def get_attacker_intelligence(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500)
):
    """Get attacker intelligence data"""
    intelligence = db.query(AttackerIntelligence).order_by(
        AttackerIntelligence.last_seen.desc()
    ).limit(limit).all()
    
    return intelligence

@app.get("/api/intelligence/{ip}")
async def get_ip_details(ip: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific IP"""
    intel = db.query(AttackerIntelligence).filter(
        AttackerIntelligence.ip_address == ip
    ).first()
    
    if not intel:
        # Try to get fresh data
        fresh_info = get_ip_info(ip)
        return {"ip": ip, **fresh_info, "cached": False}
    
    return {**intel.__dict__, "cached": True}

# ----------------------------------------------------------------------------
# Dashboard Stats API
# ----------------------------------------------------------------------------

@app.get("/api/stats", response_model=StatsResponse)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get comprehensive dashboard statistics"""
    today = datetime.now().date()
    
    # Basic counts
    total_events = db.query(SecurityEvent).count()
    total_attacks = db.query(Alert).count()
    unique_ips = db.query(SecurityEvent.ip_address).distinct().count()
    active_alerts = db.query(Alert).filter(Alert.is_active == True).count()
    events_today = db.query(SecurityEvent).filter(
        SecurityEvent.timestamp >= today
    ).count()
    attacks_today = db.query(Alert).filter(
        Alert.timestamp >= today
    ).count()
    
    # Top countries
    country_counts = db.query(
        SecurityEvent.country,
        func.count(SecurityEvent.id).label('count')
    ).filter(SecurityEvent.country != None).group_by(
        SecurityEvent.country
    ).order_by(func.count(SecurityEvent.id).desc()).limit(10).all()
    
    top_countries = [{"country": c or "Unknown", "count": n} for c, n in country_counts]
    
    # Recent activity
    recent = db.query(SecurityEvent).order_by(
        SecurityEvent.timestamp.desc()
    ).limit(10).all()
    
    recent_activity = [{
        "timestamp": e.timestamp,
        "type": e.event_type,
        "ip": e.ip_address,
        "country": e.country
    } for e in recent]
    
    return StatsResponse(
        total_events=total_events,
        total_attacks=total_attacks,
        unique_ips=unique_ips,
        active_alerts=active_alerts,
        events_today=events_today,
        attacks_today=attacks_today,
        top_countries=top_countries,
        recent_activity=recent_activity
    )

# ----------------------------------------------------------------------------
# Monitor Control API
# ----------------------------------------------------------------------------

@app.post("/api/monitor/start", response_model=MonitorControlResponse)
async def start_monitoring(background_tasks: BackgroundTasks, threshold: int = Query(3, ge=1, le=20)):
    """Start real-time log monitoring"""
    global monitoring_active, monitor_task
    
    if monitoring_active:
        return MonitorControlResponse(
            status="info",
            message="Monitoring already active",
            is_running=True
        )
    
    monitoring_active = True
    monitor_task = asyncio.create_task(monitor_logs_background(threshold))
    
    return MonitorControlResponse(
        status="success",
        message=f"Real-time monitoring started (threshold: {threshold})",
        is_running=True
    )

@app.post("/api/monitor/stop", response_model=MonitorControlResponse)
async def stop_monitoring():
    """Stop real-time log monitoring"""
    global monitoring_active
    
    monitoring_active = False
    
    return MonitorControlResponse(
        status="success",
        message="Real-time monitoring stopped",
        is_running=False
    )

@app.get("/api/monitor/status")
async def get_monitor_status():
    """Get current monitoring status"""
    return {
        "is_running": monitoring_active
    }

# ----------------------------------------------------------------------------
# Analysis API
# ----------------------------------------------------------------------------

@app.post("/api/analyze")
async def analyze_log_file(
    background_tasks: BackgroundTasks,
    threshold: int = Query(3, ge=1, le=20)
):
    """Analyze the auth.log file for attacks"""
    background_tasks.add_task(run_batch_analysis, threshold)
    
    return {
        "message": "Analysis started in background",
        "threshold": threshold
    }

async def run_batch_analysis(threshold: int):
    """Run batch log analysis"""
    # Use absolute path from project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_path = os.path.join(base_dir, "logs", "auth.log")
    db = SessionLocal()
    try:
        ips = get_failed_login_ips(log_path)
        suspicious_ips = detect_bruteforce(ips, threshold=threshold)
        
        for ip, attempts in suspicious_ips.items():
            ip_info = get_ip_info(ip)
            if not ip_info:
                ip_info = {}
            
            # Create nkevent
            event = SecurityEvent(
                event_type="attack_detected",
                ip_address=ip,
                country=ip_info.get("country"),
                city=ip_info.get("city"),
                isp=ip_info.get("isp"),
                asn=ip_info.get("asn"),
                latitude=ip_info.get("lat"),
                longitude=ip_info.get("lon"),
                map_url=ip_info.get("map_url"),
                is_proxy=ip_info.get("proxy", False),
                is_hosting=ip_info.get("hosting", False)
            )
            db.add(event)
            
            # Create alert
            alert = Alert(
                alert_type="bruteforce",
                severity="high" if attempts > 10 else "medium",
                source_ip=ip,
                description=f"Batch analysis detected {attempts} failed login attempts",
                is_active=True
            )
            db.add(alert)
            
            # Update intelligence
            intel = db.query(AttackerIntelligence).filter(
                AttackerIntelligence.ip_address == ip
            ).first()
            
            if intel:
                intel.total_attempts += attempts
                intel.last_seen = datetime.now()
            else:
                intel = AttackerIntelligence(
                    ip_address=ip,
                    total_attempts=attempts,
                    country=ip_info.get("country"),
                    city=ip_info.get("city"),
                    isp=ip_info.get("isp"),
                    asn=ip_info.get("asn"),
                    latitude=ip_info.get("lat"),
                    longitude=ip_info.get("lon"),
                    is_proxy=ip_info.get("proxy", False),
                    is_hosting=ip_info.get("hosting", False)
                )
                db.add(intel)
            
            db.commit()
            
    finally:
        db.close()

# ----------------------------------------------------------------------------
# Reports API
# ----------------------------------------------------------------------------

@app.get("/api/reports/export")
async def export_report(db: Session = Depends(get_db)):
    """Export attack report as CSV"""
    report_path = "reports/attack_report.csv"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    intelligence = db.query(AttackerIntelligence).all()
    
    with open(report_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'IP', 'Total Attempts', 'Country', 'City', 'ISP', 'ASN',
            'First Seen', 'Last Seen', 'Threat Level'
        ])
        for intel in intelligence:
            writer.writerow([
                intel.ip_address,
                intel.total_attempts,
                intel.country,
                intel.city,
                intel.isp,
                intel.asn,
                intel.first_seen,
                intel.last_seen,
                intel.threat_level
            ])
    
    return FileResponse(report_path, filename="attack_report.csv")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("""
    🛡️  Cyber Log Analyzer - SIEM System
    =====================================
    API Server running on http://localhost:8000
    API Documentation: http://localhost:8000/docs
    
    Available Endpoints:
    - GET  /api/health              - Health check
    - GET  /api/events              - Get security events
    - GET  /api/alerts              - Get alerts
    - GET  /api/stats               - Dashboard statistics
    - GET  /api/intelligence        - Attacker intelligence
    - POST /api/monitor/start       - Start monitoring
    - POST /api/monitor/stop        - Stop monitoring
    - POST /api/analyze             - Analyze log file
    - GET  /api/reports/export      - Export report
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)
