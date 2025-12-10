"""FastAPI application for database monitoring and email notifications."""
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pathlib import Path

from .models import (
    FetchRequest, FetchResponse, LLMTestRequest, LLMTestResponse,
    ProviderInfo, HealthResponse
)
from .config import get_db_config, get_email_config
from db import MSSQLConnector, MySQLConnector, MongoDBConnector  # type: ignore
from services import EmailService, AnalysisService
from llm.factory import LLMFactory

# Initialize FastAPI app
app = FastAPI(
    title="Database Monitor & AI Analysis Service",
    description="Intelligent database monitoring with AI-powered failure analysis and notifications",
    version="1.0.0"
)

# Initialize services
analysis_service = AnalysisService()


def get_db_connector(db_type: str):
    """
    Factory function to get appropriate database connector.
    
    Args:
        db_type: Type of database
        
    Returns:
        Database connector instance
    """
    db_type = db_type.lower()
    config = get_db_config(db_type)
    
    if db_type == 'mssql':
        return MSSQLConnector(config)
    elif db_type == 'mysql':
        return MySQLConnector(config)
    elif db_type == 'mongodb':
        return MongoDBConnector(config)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Database Monitor & AI Analysis Service",
        "status": "running",
        "version": "1.0.0",
        "features": {
            "databases": ["mssql", "mysql", "mongodb"],
            "llm_providers": ["gemini", "openai", "anthropic", "ollama"],
            "services": ["email", "analysis", "background_tasks"]
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check endpoint."""
    email_config = get_email_config()
    llm_available = analysis_service.is_available()
    
    return HealthResponse(
        status="healthy",
        services={
            "email": bool(email_config.get('smtp_server')),
            "llm": llm_available,
            "api": True
        }
    )


@app.post("/fetch-and-email", response_model=FetchResponse)
async def fetch_and_email(request: FetchRequest):
    """
    Fetch last row from database table, analyze with AI, and send via email.
    
    Args:
        request: FetchRequest with db_type, table_name, order_by, recipient_email
        
    Returns:
        FetchResponse with status, data, and email confirmation
    """
    try:
        # Get database connector
        connector = get_db_connector(request.db_type)
        
        # Fetch data using context manager
        with connector:
            # Test connection first
            if not connector.test_connection():
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to connect to {request.db_type} database"
                )
            
            # Fetch last row
            data = connector.fetch_last_row(
                table_name=request.table_name,
                order_by=request.order_by
            )
            
            if not data:
                return FetchResponse(
                    status="warning",
                    message=f"No data found in table {request.table_name}",
                    data={},
                    email_sent=False,
                    analysis_included=False
                )
        
        # Analyze with LLM
        llm_analysis = None
        try:
            llm_analysis = await analysis_service.analyze(
                log_data=data,
                provider_type=request.llm_provider
            )
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            # Continue without analysis
        
        # Send email
        email_config = get_email_config()
        email_service = EmailService(
            smtp_server=email_config['smtp_server'],
            smtp_port=email_config['smtp_port'],
            sender_email=email_config['sender_email']
        )
        
        email_sent = email_service.send_email(
            recipient_email=request.recipient_email,
            subject=request.subject,
            data=data,
            analysis=llm_analysis
        )
        
        return FetchResponse(
            status="success",
            message=f"Data fetched from {request.table_name} and email sent to {request.recipient_email}",
            data=data,
            email_sent=email_sent,
            analysis_included=llm_analysis is not None
        )
        
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/test-connection")
async def test_connection(db_type: str):
    """
    Test database connection.
    
    Args:
        db_type: Type of database to test
        
    Returns:
        Connection test result
    """
    try:
        connector = get_db_connector(db_type)
        with connector:
            result = connector.test_connection()
            return {
                "db_type": db_type,
                "connected": result,
                "message": "Connection successful" if result else "Connection failed"
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Connection test failed: {str(e)}"
        )


@app.get("/llm/providers", response_model=ProviderInfo)
async def get_llm_providers():
    """
    Get available LLM providers.
    
    Returns:
        Provider information
    """
    try:
        available = LLMFactory.get_available_providers()
        current = os.getenv('LLM_PROVIDER', 'gemini')
        return ProviderInfo(
            current_provider=current,
            available_providers=available,
            supported_providers=["gemini", "openai", "anthropic", "ollama"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking providers: {str(e)}"
        )


@app.post("/llm/test", response_model=LLMTestResponse)
async def test_llm(request: LLMTestRequest):
    """
    Test LLM provider with a custom prompt.
    
    Args:
        request: LLMTestRequest with prompt and optional provider
        
    Returns:
        LLM response
    """
    try:
        provider = LLMFactory.create_provider(provider_type=request.provider)
        response = await provider.generate(request.prompt)
        return LLMTestResponse(
            provider=request.provider or os.getenv('LLM_PROVIDER', 'gemini'),
            model=provider.model,
            prompt=request.prompt,
            response=response
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM test failed: {str(e)}"
        )


@app.post("/analyze")
async def analyze_log(log_data: dict, provider: str = None):
    """
    Analyze log data using LLM without sending email.
    
    Args:
        log_data: Log data dictionary
        provider: Optional LLM provider override
        
    Returns:
        Analysis result
    """
    try:
        analysis = await analysis_service.analyze(log_data, provider_type=provider)
        return {
            "status": "success",
            "provider": provider or os.getenv('LLM_PROVIDER', 'gemini'),
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
