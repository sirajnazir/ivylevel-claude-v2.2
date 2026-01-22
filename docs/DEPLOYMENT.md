# IvyLevel Deployment Guide

**Version:** MVP 1.0.3
**Last Updated:** January 21, 2026 @ 20:15 PST

---

## Overview

IvyLevel consists of two deployable components:
1. **Frontend** (Next.js) → Vercel
2. **Backend** (FastAPI) → Container/VM

---

## Quick Start (Development)

### Prerequisites

- Node.js 18+
- Python 3.11+
- Supabase account

### Frontend Setup

```bash
# Install dependencies
npm install

# Create .env.local
cp .env.example .env.local
# Edit .env.local with your Supabase credentials

# Run development server
npm run dev
```

### Backend Setup

```bash
cd agents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Create .env
cp .env.example .env
# Edit .env with your credentials

# Run server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Environment Variables

### Frontend (.env.local)

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Feature Flags
NEXT_PUBLIC_ENABLE_PROACTIVE=true
```

### Backend (agents/.env)

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...

# LLM Providers
OPENAI_API_KEY=sk-...
GOOGLE_GENERATIVE_AI_API_KEY=AI...

# LangChain/LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_...
LANGCHAIN_PROJECT=ivylevel-v58

# Proactive System
PROACTIVE_ENABLED=true
PROACTIVE_OPPORTUNITY_MATCH=true
PROACTIVE_DEADLINE_ALERTS=true
PROACTIVE_STALL_DETECTION=true
PROACTIVE_INACTIVITY_CHECK=true

# Feature Flags
LETTA_ENABLED=false
```

---

## Production Deployment

### Frontend (Vercel)

1. Connect GitHub repo to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main

**Vercel Settings:**
- Framework: Next.js
- Build Command: `npm run build`
- Output Directory: `.next`
- Node Version: 18.x

### Backend (Container)

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY agents/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build & Run:**
```bash
docker build -t ivylevel-agents .
docker run -p 8000:8000 --env-file agents/.env ivylevel-agents
```

---

## Database (Supabase)

### Running Migrations

```bash
# Install Supabase CLI
npm install -g supabase

# Link to project
supabase link --project-ref <project-id>

# Push migrations
supabase db push
```

### Backup & Restore

```bash
# Backup
supabase db dump -f backup.sql

# Restore
supabase db restore backup.sql
```

---

## Monitoring

### LangSmith (Agent Tracing)
- Dashboard: https://smith.langchain.com
- Project: `ivylevel-v58`
- Enabled via `LANGCHAIN_TRACING_V2=true`

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Proactive status
curl http://localhost:8000/proactive/status
```

### Logs

**Backend logs:**
```bash
# Development
uvicorn main:app --log-level debug

# Production (structured JSON)
# Logs output via structlog in JSON format
```

---

## Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
# Ensure you're in virtual environment
source agents/venv/bin/activate
pip install -r requirements.txt
```

**2. Supabase connection errors**
- Check `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`
- Verify RLS policies allow access

**3. CORS errors**
- Backend CORS is configured in `main.py`
- Ensure frontend URL is in allowed origins

**4. Proactive jobs not running**
- Check `PROACTIVE_ENABLED=true`
- Verify APScheduler is starting (check logs)

### Reset Development Environment

```bash
# Frontend
rm -rf node_modules .next
npm install

# Backend
rm -rf agents/venv
cd agents && python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## CI/CD

### GitHub Actions (Example)

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build
      - run: npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Vercel
        run: vercel --prod
```

---

## Security Checklist

- [ ] `.env` files in `.gitignore`
- [ ] Service role key only on backend
- [ ] RLS enabled on all tables
- [ ] CORS restricted to allowed origins
- [ ] Rate limiting enabled
- [ ] HTTPS enforced in production
