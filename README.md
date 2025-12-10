# Database Monitor & AI Analysis Service

An intelligent database monitoring system with AI-powered failure analysis and automated email notifications.

## 📁 Project Structure

```
failureintel/
├── app/                      # FastAPI application
│   ├── main.py              # API routes and endpoints
│   ├── config.py            # Configuration management
│   └── models.py            # Pydantic models
├── db/                       # Database connectors (pluggable)
│   ├── base.py              # Abstract base connector
│   ├── mssql.py, mysql.py, mongodb.py
├── llm/                      # LLM providers (pluggable)
│   ├── factory.py           # Provider factory
│   ├── gemini.py, openai.py, anthropic.py, ollama.py
├── services/                 # Business logic
│   ├── email_service.py     # Email notifications
│   ├── analysis_service.py  # LLM analysis
│   └── background_tasks.py  # Async processing
├── prompts/                  # Prompt templates
├── tests/                    # Test files
├── run.py                   # Application entry point
├── requirements.txt
└── .env                     # Configuration
```

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the service
python run.py
```

API available at: http://localhost:8000/docs

## ⚙️ Configuration

### Choose LLM Provider (in .env)
```bash
# Gemini (default - free tier available)
LLM_PROVIDER="gemini"
GEMINI_API_KEY="your-key"

# OR OpenAI
LLM_PROVIDER="openai"
OPENAI_API_KEY="your-key"

# OR Ollama (local, free)
LLM_PROVIDER="ollama"
OLLAMA_MODEL="llama3.2"
```

### Database
```bash
MSSQL_SERVER=localhost
MSSQL_DATABASE=your_db
MSSQL_USERNAME=sa
MSSQL_PASSWORD=YourPass
```

## 📚 API Endpoints

**Fetch, Analyze & Email**
```bash
POST /fetch-and-email
{
  "db_type": "mssql",
  "table_name": "FailedJobData_Archive",
  "order_by": "FailedDateTime",
  "recipient_email": "admin@example.com"
}
```

**Test LLM**
```bash
POST /llm/test
{"prompt": "Hello"}
```

**Check Providers**
```bash
GET /llm/providers
```

## 🔌 Extend the System

### Add Database Connector
1. Create `db/your_db.py` extending `BaseConnector`
2. Implement: `connect()`, `disconnect()`, `fetch_last_row()`, `test_connection()`
3. Register in `db/__init__.py`

### Add LLM Provider
1. Create `llm/your_provider.py` extending `BaseLLMProvider`
2. Implement: `generate()`, `is_available()`
3. Register in `llm/factory.py`

### Add Service
1. Create `services/your_service.py`
2. Use in `app/main.py`

## 🎯 Use Cases

- SQL Server Agent job failure monitoring
- Application error analysis with AI
- Automated DBA notifications
- Database health monitoring

---
Built for intelligent database monitoring 🚀
# failureintenl
