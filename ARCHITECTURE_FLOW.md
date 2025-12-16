# MSSQL Failure Intelligence Agent - Architecture Flow

## System Overview

```mermaid
graph TB
    Start([API Request]) --> Auth{API Key Valid?}
    Auth -->|No| Error1[401 Unauthorized]
    Auth -->|Yes| Endpoint{Which Endpoint?}
    
    Endpoint -->|/health| Health[Health Check]
    Endpoint -->|/analyze-latest| Analyze[Analyze Latest Failure]
    Endpoint -->|/sent-history| History[Get Sent History]
    
    Health --> DBTest[Test DB Connection]
    DBTest --> HealthResp[Return Status JSON]
    
    History --> LoadJSON[Load email_sent_log.json]
    LoadJSON --> HistoryResp[Return Last 20 Records]
    
    Analyze --> Step1[1. Fetch Latest Failure]
    
    style Start fill:#e1f5ff
    style Auth fill:#fff3e0
    style Analyze fill:#f3e5f5
    style Health fill:#e8f5e9
    style History fill:#e8f5e9
```

## Analyze Latest Failure - Detailed Flow

```mermaid
flowchart TD
    Start([POST /api/v1/analyze-latest]) --> Auth{Verify API Key}
    Auth -->|Invalid| Err401[401 Error]
    Auth -->|Valid| DB[Connect to MSSQL]
    
    DB --> Query[Query: SELECT TOP 1<br/>FROM FailedJobData_Archive<br/>ORDER BY FailedDateTime DESC]
    Query --> Check{Data Found?}
    Check -->|No| NoData[Return: no_failures]
    Check -->|Yes| Extract[Extract Job Data]
    
    Extract --> GetEmail[Get Recipient Email<br/>Priority:<br/>1. EmailID from DB<br/>2. EmailId from DB<br/>3. Config DEFAULT]
    
    GetEmail --> Hash[Create MD5 Hash<br/>JobName + ServerName +<br/>FailedDateTime + FailureMessage]
    
    Hash --> LoadLog[Load email_sent_log.json]
    LoadLog --> Throttle{Email Sent<br/>in Last 24hrs?}
    
    Throttle -->|Yes| Block[Return: throttled<br/>Show last sent time]
    Throttle -->|No| AI[Call Gemini AI]
    
    AI --> Prompt[Send Prompt with:<br/>- Job Name<br/>- Server Name<br/>- Failure Message<br/>- Failed DateTime]
    
    Prompt --> AIResp[Get AI Analysis<br/>SUMMARY + URGENCY +<br/>ROOT_CAUSE + SOLUTION]
    
    AIResp --> Format[Format Email]
    Format --> Template[Load email_template.html]
    Template --> Replace[Replace Placeholders:<br/>job_name, server_name,<br/>failed_at, summary,<br/>urgency, root_cause,<br/>solution]
    
    Replace --> Send[Send Email via SMTP]
    Send --> SMTPConn[Connect to:<br/>bridgeheads.bskyb.com:25]
    
    SMTPConn --> Success{Email Sent?}
    Success -->|No| ErrEmail[500 Error:<br/>Failed to send email]
    Success -->|Yes| Log[Save to email_sent_log.json]
    
    Log --> SaveJSON[Append Entry:<br/>hash, job_name, server_name,<br/>failed_at, sent_to, sent_at]
    SaveJSON --> Response[Return: sent<br/>Include job details]
    
    style Start fill:#e1f5ff
    style Auth fill:#fff3e0
    style DB fill:#e8f5e9
    style AI fill:#f3e5f5
    style Throttle fill:#fff9c4
    style Send fill:#ffccbc
    style Log fill:#c8e6c9
```

## Component Interactions

```mermaid
graph LR
    subgraph "API Layer"
        API[api_service.py<br/>FastAPI]
    end
    
    subgraph "Data Layer"
        DB[(MSSQL<br/>failed_jobs DB)]
        JSON[(email_sent_log.json<br/>Duplicate Tracking)]
    end
    
    subgraph "AI Layer"
        Gemini[Google Gemini<br/>gemini-flash-latest]
        Prompt[llm_analysis.txt<br/>Prompt Template]
    end
    
    subgraph "Email Layer"
        Formatter[EmailFormatter<br/>HTML Generator]
        Template[email_template.html]
        SMTP[SMTP Server<br/>bridgeheads.bskyb.com:25]
    end
    
    subgraph "Storage"
        Logs[logs/<br/>mssql_agent_*.log]
        Data[data/<br/>email_sent_log.json]
    end
    
    API --> DB
    API --> JSON
    API --> Gemini
    Gemini --> Prompt
    API --> Formatter
    Formatter --> Template
    Formatter --> SMTP
    API --> Logs
    API --> Data
    
    style API fill:#42a5f5
    style DB fill:#66bb6a
    style JSON fill:#ffa726
    style Gemini fill:#ab47bc
    style SMTP fill:#ef5350
    style Logs fill:#78909c
    style Data fill:#ffa726
```

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI Service
    participant DB as MSSQL Database
    participant Tracker as DuplicateTracker
    participant AI as Gemini AI
    participant Formatter as EmailFormatter
    participant SMTP as SMTP Server
    participant Log as JSON File
    
    Client->>API: POST /api/v1/analyze-latest
    API->>API: Verify API Key
    
    API->>DB: Connect & Query Latest Failure
    DB-->>API: Return Job Data + EmailID
    
    API->>Tracker: Load email_sent_log.json
    Tracker-->>API: Loaded history
    
    API->>Tracker: should_send(job_data)?
    Tracker->>Tracker: Create MD5 hash
    Tracker->>Tracker: Check if sent in 24hrs
    
    alt Already sent in 24 hours
        Tracker-->>API: False + last_sent_info
        API-->>Client: 200 OK (throttled)
    else Not sent recently
        Tracker-->>API: True
        
        API->>AI: analyze(job_data)
        AI->>AI: Load llm_analysis.txt
        AI->>AI: Format prompt with job data
        AI->>AI: Call Gemini API
        AI-->>API: Analysis text (3500+ chars)
        
        API->>Formatter: format_email(analysis, job_data)
        Formatter->>Formatter: Load email_template.html
        Formatter->>Formatter: Parse analysis (SUMMARY/URGENCY/etc)
        Formatter->>Formatter: Replace placeholders
        Formatter-->>API: (html_body, plain_body)
        
        API->>SMTP: send(recipient, subject, body)
        SMTP->>SMTP: Connect to bridgeheads.bskyb.com:25
        SMTP->>SMTP: Send email
        
        alt SMTP Success
            SMTP-->>API: True
            API->>Log: log_sent(job_data, recipient)
            Log->>Log: Append to email_sent_log.json
            Log-->>API: Saved
            API-->>Client: 200 OK (sent)
        else SMTP Failed
            SMTP-->>API: False
            API-->>Client: 500 Error
        end
    end
```

## File Structure & Purpose

```mermaid
graph TD
    subgraph "Core Service"
        A[api_service.py<br/>Main FastAPI app<br/>3 endpoints]
        B[run_service.py<br/>Service starter<br/>with logging setup]
    end
    
    subgraph "Config"
        C[config/settings.py<br/>Load .env<br/>DB & Email config]
        D[.env<br/>Credentials<br/>MSSQL, SMTP, Gemini]
    end
    
    subgraph "Database"
        E[connectors/mssql.py<br/>ODBC connection<br/>fetch_last_row]
    end
    
    subgraph "AI Analysis"
        F[features/failure_analyzer.py<br/>Orchestrator]
        G[llm/gemini.py<br/>Gemini API calls]
        H[prompts/llm_analysis.txt<br/>AI instructions]
    end
    
    subgraph "Email"
        I[mail/formatter.py<br/>Parse AI response<br/>Generate HTML]
        J[mail/sender.py<br/>SMTP client]
        K[prompts/email_template.html<br/>HTML template]
    end
    
    subgraph "Persistence"
        L[data/email_sent_log.json<br/>Throttle tracking]
        M[logs/mssql_agent_*.log<br/>Application logs]
    end
    
    A --> C
    A --> E
    A --> F
    A --> I
    A --> L
    A --> M
    B --> A
    C --> D
    F --> G
    G --> H
    I --> K
    I --> J
    
    style A fill:#42a5f5,color:#fff
    style B fill:#42a5f5,color:#fff
    style L fill:#ffa726
    style M fill:#78909c
```

## Key Logic Components

### 1. DuplicateTracker Class
- **File**: `api_service.py`
- **Purpose**: Prevent duplicate emails within 24 hours
- **Methods**:
  - `create_hash()`: MD5 hash from job data
  - `should_send()`: Check if email sent in last 24hrs
  - `log_sent()`: Save sent email record
  - `get_recent_sent()`: Return history

### 2. MSSQLConnector Class
- **File**: `connectors/mssql.py`
- **Purpose**: Connect to MSSQL database
- **Methods**:
  - `test_connection()`: Health check
  - `fetch_last_row()`: Get latest failure

### 3. FailureAnalyzer Class
- **File**: `features/failure_analyzer.py`
- **Purpose**: Coordinate AI analysis
- **Methods**:
  - `analyze()`: Send job data to Gemini AI

### 4. GeminiProvider Class
- **File**: `llm/gemini.py`
- **Purpose**: Interact with Gemini API
- **Methods**:
  - `format_prompt()`: Fill template with job data
  - `generate()`: Call Gemini API

### 5. EmailFormatter Class
- **File**: `mail/formatter.py`
- **Purpose**: Generate HTML email
- **Methods**:
  - `format_email()`: Parse AI response, generate HTML
  - `_format_solution()`: Detect SQL code blocks

### 6. EmailSender Class
- **File**: `mail/sender.py`
- **Purpose**: Send email via SMTP
- **Methods**:
  - `send()`: Connect to SMTP and send

## Environment Configuration

```ini
# Database
MSSQL_SERVER=localhost
MSSQL_DATABASE=failed_jobs
MSSQL_USERNAME=sa
MSSQL_PASSWORD=***
MSSQL_DRIVER=ODBC Driver 18 for SQL Server

# Email
SMTP_SERVER=bridgeheads.bskyb.com
SMTP_PORT=25
SENDER_EMAIL=manojkumar.selvakumar@sky.uk

# AI
GEMINI_API_KEY=AIzaSy***
GEMINI_MODEL=gemini-flash-latest

# API Security
API_KEY=sky-mssql-agent-2025-secret
PORT=8000
```

## Throttle Logic Example

```
Time: 10:00 AM - Job fails, email sent
Hash: abc123 saved to email_sent_log.json

Time: 2:00 PM - Same job fails again
Check: abc123 found, sent_at = 10:00 AM
Diff: 4 hours < 24 hours
Action: Block email, return "throttled"

Time: 10:01 AM (next day) - Same job fails
Check: abc123 found, sent_at = 10:00 AM yesterday
Diff: 24 hours 1 minute > 24 hours
Action: Allow email, send again
```

## API Usage Examples

### 1. Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### 2. Analyze Latest Failure
```bash
curl -X POST http://localhost:8000/api/v1/analyze-latest \
  -H "X-API-Key: sky-mssql-agent-2025-secret"
```

### 3. Get Sent History
```bash
curl http://localhost:8000/api/v1/sent-history?limit=10 \
  -H "X-API-Key: sky-mssql-agent-2025-secret"
```
