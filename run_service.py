"""Simple service runner without UI."""
import logging
import os
from pathlib import Path
from datetime import datetime
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"mssql_agent_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
logger.info(f"Data directory: {DATA_DIR.absolute()}")
logger.info(f"Log directory: {LOG_DIR.absolute()}")

# Import and run the app
from api_service import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting MSSQL Failure Intelligence Agent on port {port}")
    logger.info(f"API Key: {os.getenv('API_KEY', 'NOT SET')[:10]}...")
    logger.info(f"Database: {os.getenv('MSSQL_SERVER')}/{os.getenv('MSSQL_DATABASE')}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
