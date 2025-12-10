"""Pydantic models for API requests and responses."""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any


class FetchRequest(BaseModel):
    """Request model for fetching data."""
    db_type: str  # 'mssql', 'mysql', 'mongodb'
    table_name: str
    order_by: Optional[str] = None
    recipient_email: EmailStr
    subject: Optional[str] = "Database Query Result"
    llm_provider: Optional[str] = None  # Override default LLM provider


class FetchResponse(BaseModel):
    """Response model."""
    status: str
    message: str
    data: Dict[str, Any]
    email_sent: bool
    analysis_included: bool = False


class LLMTestRequest(BaseModel):
    """Request model for LLM testing."""
    prompt: str
    provider: Optional[str] = None


class LLMTestResponse(BaseModel):
    """Response model for LLM testing."""
    provider: str
    model: str
    prompt: str
    response: str


class ProviderInfo(BaseModel):
    """LLM provider information."""
    current_provider: str
    available_providers: list[str]
    supported_providers: list[str]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str = "1.0.0"
    services: Dict[str, bool]
