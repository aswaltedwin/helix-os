# HelixOS: Enterprise OS for Autonomous AI Workforces

> Multi-agent orchestration. Auto-workflow discovery. Enterprise-grade governance. From hackathon to unicorn.

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Docker & Docker Compose installed
- Anthropic API key (get free at https://console.anthropic.com/)

### Setup
```bash
# Clone
git clone https://github.com/[your-name]/helix-os.git
cd helix-os

# Configure
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Add your Anthropic key to backend/.env
```

### Run
```bash
docker-compose up
```

Wait ~30 seconds for services to be healthy.

Open:
- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## ✨ Features

- **Multi-Agent Orchestration**: LangGraph supervisor pattern + specialist agents
- **5 Pre-Built Agents**: Finance, HR, Sales, Compliance, Ops
- **Enterprise Governance**: Policy engine, audit trails, watermarking
- **Auto-Workflow Discovery**: LLM analyzes company data
- **Real-Time Dashboard**: Live metrics, agent status, results
- **Fully Auditable**: Every action logged, watermarked, explainable

## 📂 Project Structure