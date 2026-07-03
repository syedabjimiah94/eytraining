# 🌦️ Self-Healing Weather API Platform

An AI-powered Self-Healing Weather Platform built using **FastAPI**, **Streamlit**, **LangGraph**, **LangSmith**, **SQLite**, **Docker**, and **GitHub Actions**.

The platform automatically detects failures, performs root cause analysis using AI agents, applies recovery strategies, validates recovery, logs incidents, detects data drift, and escalates critical issues via email when automatic recovery is not possible.

---

# 🚀 Features

- Live & Mock Weather Provider
- Failure Simulation
- AI-powered Self-Healing Workflow
- LangGraph Multi-Agent Architecture
- LangSmith Tracing
- SQLite Incident & Request Logging
- Drift Detection Layer
- Automatic Recovery
- Manual Email Escalation
- Evaluation Metrics Dashboard
- Docker Support
- GitHub Actions CI Pipeline

---

# 🏗️ Architecture

```
Streamlit UI
      │
      ▼
FastAPI Backend
      │
      ▼
Middleware
 ├── Logging
 ├── Monitoring
 ├── Request Tracking
 ├── Error Handling
 └── Audit Trail
      │
      ▼
Drift Detection Layer
 ├── API Schema Drift
 └── Data Anomaly Drift
      │
      ▼
LangGraph AI Agents
 ├── Monitoring Agent
 ├── Diagnosis Agent
 ├── Healing Agent
 ├── Validation Agent
 └── Notification Agent
      │
      ▼
SQLite Database
      │
      ▼
LangSmith Observability
```

---

# 🛠️ Technology Stack

| Component | Technology |
|------------|------------|
| Backend | FastAPI |
| Frontend | Streamlit |
| AI Workflow | LangGraph |
| LLM | OpenAI |
| Observability | LangSmith |
| Database | SQLite |
| Containerization | Docker |
| CI | GitHub Actions |
| Email Notification | Resend |
| Deployment | Azure Container Apps |

---

# 📂 Project Structure

```
self-healing-weather-api/

│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── middleware/
│   │   ├── models/
│   │   ├── prompts/
│   │   ├── database/
│   │   └── main.py
│
├── frontend/
│   └── streamlit_app.py
│
├── docker-compose.yml
│
└── .github/
    └── workflows/
        └── docker-ci.yml
```

---

# 🤖 AI Agents

## 1. Monitoring Agent

Responsible for

- Monitoring API execution
- Retry mechanism
- Detecting failures

---

## 2. Diagnosis Agent

Uses LLM to identify

- Root Cause
- Severity
- Recommendation

---

## 3. Healing Agent

Automatically performs recovery

Examples

- Retry Request
- Switch to Mock Weather API
- Rule-based fallback
- Exponential Backoff

---

## 4. Validation Agent

Verifies

- Recovery success
- Output validity
- Response integrity

---

## 5. Notification Agent

Responsible for

- Incident logging
- SQLite persistence
- Email notification
- Manual investigation ticket

---

# 🌊 Drift Detection Layer

The project includes a non-blocking Drift Detection layer.

### API Schema Drift

Detects

- Missing required fields
- Changed API schema

Example

```
Humidity field missing
```

---

### Data Anomaly Drift

Detects

- Temperature out of range
- Invalid Humidity
- Invalid Wind Speed

Example

```
Temperature = 999°C
```

---

# ⚠️ Failure Scenarios

| Failure | Automatic Recovery |
|-----------|-------------------|
| success | Normal Response |
| network_error | Retry Request |
| weather_api_down | Switch to Mock API |
| api_timeout | Retry with Backoff |
| rate_limit_429 | Backoff & Retry |
| invalid_json | Validate & Retry |
| llm_timeout | Rule-based Fallback |
| invalid_api_key | Manual Investigation |
| database_down | Manual Investigation |
| schema_drift | Drift Detection |
| data_anomaly_drift | Drift Detection |

---

# 📊 Evaluation Metrics

Dashboard displays

- Total Requests
- Successful Requests
- Self-Healed Requests
- Manual Investigations
- Average Latency
- LLM Calls
- Emails Sent

---

# 📋 Request Logs

Every request stores

- Request ID
- City
- Provider Mode
- Failure Type
- Diagnosis
- Healing Action
- Validation Result
- Incident ID
- Latency

Users can

- Search by Request ID
- View complete request details
- Delete request logs

---

# 🚨 Incident Logs

SQLite stores

- Incident ID
- Error Type
- Severity
- Status
- Healing Action
- Timestamp

---

# 📧 Manual Escalation

Critical failures automatically generate

- Incident
- Email Notification
- Manual Investigation Ticket

---

# 📈 LangSmith

Provides

- Workflow Trace
- Agent Execution
- LLM Calls
- Performance Monitoring
- Evaluation

---

# 🐳 Docker

Run

```bash
docker compose up --build
```

Frontend

```
http://localhost:8501
```

Backend

```
http://localhost:8000
```

---

# ⚙️ GitHub Actions CI

Every push to **main** automatically

- Checks out source code
- Builds Docker images
- Starts containers
- Verifies containers
- Stops containers

Workflow

```
Developer
     │
git push
     │
GitHub Actions
     │
Docker Build
     │
Run Containers
     │
Health Check
     │
Success
```

---

# ☁️ Azure Deployment

The application is deployment-ready for

- Azure Container Apps
- Azure Container Registry
- Azure Kubernetes Service (AKS)

---

# 🔮 Future Enhancements

- Kubernetes Auto Scaling
- Prometheus Metrics
- Grafana Dashboard
- Redis Cache


---

# 👨‍💻 Developed By

**Syed Abjimiah**
**Amit Kumar Yadav**

AI-Powered Self-Healing Weather Platform using FastAPI, Streamlit, LangGraph, LangSmith, Docker, SQLite, GitHub Actions, and Azure.

---

