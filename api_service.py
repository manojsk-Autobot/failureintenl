"""FastAPI service for MSSQL Failure Intelligence Agent."""
import asyncio
import hashlib
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config.settings import settings
from connectors.mssql import MSSQLConnector
from features.failure_analyzer import FailureAnalyzer
from mail.formatter import EmailFormatter
from mail.sender import EmailSender
import dotenv

# Configure logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "mssql_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MSSQL Failure Intelligence Agent",
    description="Automated SQL Server job failure analysis and notification system",
    version="1.0.0"
)

# Add CORS middleware for internal use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Duplicate tracking file path
DATA_DIR = Path("/data") if os.path.exists("/data") else Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
SENT_LOG_FILE = DATA_DIR / "email_sent_log.json"
logger.info(f"Data directory: {DATA_DIR}")
logger.info(f"Sent log file: {SENT_LOG_FILE}")

# API Key for authentication
API_KEY = os.getenv("API_KEY", "your-secret-api-key-change-this")


class DuplicateTracker:
    """Track sent emails to prevent duplicates."""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.load_log()
    
    def load_log(self):
        """Load sent email log from file."""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    self.sent_log = json.load(f)
                logger.info(f"Loaded {len(self.sent_log)} sent email records")
            except Exception as e:
                logger.error(f"Error loading log file: {e}")
                self.sent_log = []
        else:
            logger.info(f"No existing log file found at {self.log_file}, starting fresh")
            self.sent_log = []
    
    def save_log(self):
        """Save sent email log to file."""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.sent_log, f, indent=2)
            logger.info(f"Saved log with {len(self.sent_log)} records to {self.log_file}")
        except Exception as e:
            logger.error(f"Error saving log file: {e}")
    
    def create_hash(self, job_data: Dict[str, Any]) -> str:
        """Create unique hash for job failure."""
        key = f"{job_data.get('JobName')}_{job_data.get('ServerName')}_{job_data.get('FailedDateTime')}_{job_data.get('FailureMessage')}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def should_send(self, job_data: Dict[str, Any], throttle_hours: int = 24) -> tuple[bool, Optional[Dict]]:
        """
        Check if email should be sent (not sent within throttle window).
        
        Returns:
            (should_send: bool, last_sent_info: Optional[Dict])
        """
        email_hash = self.create_hash(job_data)
        
        # Find if this failure was sent before
        for entry in reversed(self.sent_log):  # Check most recent first
            if entry['hash'] == email_hash:
                sent_time = datetime.fromisoformat(entry['sent_at'])
                time_diff = datetime.now() - sent_time
                
                if time_diff < timedelta(hours=throttle_hours):
                    # Too soon, don't send
                    return False, entry
        
        return True, None
    
    def log_sent(self, job_data: Dict[str, Any], recipient: str):
        """Log that email was sent."""
        entry = {
            'hash': self.create_hash(job_data),
            'job_name': job_data.get('JobName'),
            'server_name': job_data.get('ServerName'),
            'failed_at': job_data.get('FailedDateTime'),
            'sent_to': recipient,
            'sent_at': datetime.now().isoformat()
        }
        self.sent_log.append(entry)
        self.save_log()
    
    def get_recent_sent(self, limit: int = 20) -> List[Dict]:
        """Get recently sent emails."""
        return self.sent_log[-limit:][::-1]  # Return last N in reverse order


# Initialize tracker
tracker = DuplicateTracker(SENT_LOG_FILE)


def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key from header."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "MSSQL Failure Intelligence Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "analyze_latest": "/api/v1/analyze-latest",
            "sent_history": "/api/v1/sent-history",
            "clear_history": "/api/v1/clear-history (DELETE)"
        }
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    try:
        db = MSSQLConnector(settings.get_db_config())
        db_healthy = db.test_connection()
        db.disconnect()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected" if db_healthy else "disconnected",
            "gemini_api": "configured" if settings.GEMINI_API_KEY else "not_configured"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.post("/api/v1/analyze-latest")
async def analyze_latest(x_api_key: str = Header(None)):
    """Analyze latest job failure and send email."""
    verify_api_key(x_api_key)
    
    logger.info("=== Starting analyze_latest endpoint ===")
    
    try:
        # Initialize components
        db = MSSQLConnector(settings.get_db_config())
        analyzer = FailureAnalyzer()
        formatter = EmailFormatter()
        sender = EmailSender(settings.get_email_config())
        
        # Fetch latest failure
        with db:
            job_data = db.fetch_last_row("FailedJobData_Archive")
            if not job_data:
                logger.warning("No job failures found in database")
                return {"status": "no_failures", "message": "No job failures found in database"}
            
            # Get recipient from DB or use default
            recipient = job_data.get('EmailID') or job_data.get('EmailId') or settings.SENDER_EMAIL
            logger.info(f"Job: {job_data.get('JobName')}, Recipient: {recipient}")
        
        # Check if we should send (duplicate check)
        should_send, last_sent = tracker.should_send(job_data, throttle_hours=24)
        
        if not should_send:
            logger.info(f"THROTTLED: Email already sent for {job_data.get('JobName')}")
            return {
                "status": "throttled",
                "message": "Email already sent for this failure within last 24 hours",
                "job_name": job_data.get('JobName'),
                "last_sent_at": last_sent['sent_at'], #type: ignore
                "last_sent_to": last_sent['sent_to']  #type: ignore
            }
        
        # Analyze with LLM
        logger.info("Analyzing with Gemini...")
        analysis = await analyzer.analyze(job_data)
        logger.info(f"Analysis complete: {len(analysis)} characters")
        
        # Format email
        html_body, plain_body = formatter.format_email(analysis, job_data, settings.SENDER_EMAIL)
        
        # Send email
        subject = f"[URGENT] SQL Job Failure: {job_data.get('JobName', 'Unknown Job')}"
        logger.info(f"Sending email to {recipient}...")
        success = sender.send(
            recipient=recipient,
            subject=subject,
            html_body=html_body,
            plain_body=plain_body
        )
        
        if success:
            # Log the sent email
            tracker.log_sent(job_data, recipient)
            logger.info(f"✓ Email sent successfully to {recipient}")
            
            return {
                "status": "sent",
                "message": "Email sent successfully",
                "job_name": job_data.get('JobName'),
                "server_name": job_data.get('ServerName'),
                "failed_at": job_data.get('FailedDateTime'),
                "sent_to": recipient,
                "sent_at": datetime.now().isoformat()
            }
        else:
            logger.error("Failed to send email")
            raise HTTPException(status_code=500, detail="Failed to send email")
            
    except Exception as e:
        logger.error(f"Error in analyze_latest: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sent-history")
async def get_sent_history(limit: int = 20, x_api_key: str = Header(None)):
    """Get history of sent emails."""
    verify_api_key(x_api_key)
    
    history = tracker.get_recent_sent(limit)
    return {
        "status": "success",
        "count": len(history),
        "history": history
    }


@app.delete("/api/v1/clear-history")
async def clear_history(x_api_key: str = Header(None)):
    """Clear sent email history to bypass throttle."""
    verify_api_key(x_api_key)
    
    logger.info("Clearing email sent history")
    old_count = len(tracker.sent_log)
    tracker.sent_log = []
    tracker.save_log()
    logger.info(f"Cleared {old_count} records from history")
    
    return {
        "status": "success",
        "message": f"Cleared {old_count} email history records",
        "cleared_count": old_count
    }


# Optional UI
if __name__ == "__main__":
    # Run the service
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
