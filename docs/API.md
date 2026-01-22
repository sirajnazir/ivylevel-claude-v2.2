# IvyLevel API Reference

**Version:** MVP 1.0.1
**Last Updated:** January 21, 2026 @ 19:15 PST
**Base URL:** `http://localhost:8000` (dev) | `https://api.ivylevel.com` (prod)

---

## Overview

IvyLevel has two API surfaces:
1. **Backend API** (FastAPI) - Agent orchestration, AI features
2. **Frontend API** (Next.js) - Authentication, data proxying

---

## Backend API (FastAPI)

**Location:** `/agents/main.py`
**Port:** 8000

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/proactive/status` | Proactive system status |

#### GET /health
```json
{
  "status": "healthy",
  "version": "15.0.0",
  "agents_enabled": true
}
```

---

### Proactive System (v10.0)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/proactive/matches/{profile_id}` | Get opportunity matches |
| GET | `/proactive/notifications/{profile_id}` | Get notifications |
| POST | `/proactive/trigger/{job_name}` | Trigger job manually |

#### GET /proactive/matches/{profile_id}

**Query Parameters:**
- `max_matches` (int, default=5): Maximum matches to return
- `include_awards` (bool, default=true): Include awards
- `include_opportunities` (bool, default=true): Include programs

**Response:**
```json
{
  "success": true,
  "profile_id": "uuid",
  "matches": [
    {
      "source": "opportunity",
      "source_id": "uuid",
      "opportunity_name": "Summer Science Program",
      "deadline": "2026-02-15",
      "match_score": 0.85,
      "match_reasons": ["🎯 Matches your STEM profile", "⭐ Highly prestigious"]
    }
  ],
  "proactive_enabled": true
}
```

---

### Execution Hub

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/execution/eds/{profile_id}` | Get EDS score |
| GET | `/api/execution/weekly-plan/{profile_id}` | Get weekly plan |
| POST | `/api/execution/chat` | Chat with execution agent |
| POST | `/api/execution/chat/stream` | Streaming chat |

#### GET /api/execution/eds/{profile_id}

**Response:**
```json
{
  "profile_id": "uuid",
  "score": 42,
  "level": "moderate",
  "factors": {
    "overdue_tasks": 2,
    "upcoming_deadlines": 3,
    "stalled_projects": 1
  },
  "recommendations": ["Focus on overdue tasks first"]
}
```

#### POST /api/execution/chat

**Request:**
```json
{
  "profile_id": "uuid",
  "message": "What should I work on this week?",
  "conversation_id": "uuid"  // optional
}
```

**Response:**
```json
{
  "response": "Based on your game plan, I recommend...",
  "conversation_id": "uuid",
  "tools_used": ["get_weekly_plan", "check_deadlines"]
}
```

---

### Multi-Agent System

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/agents/game-plan/generate` | Generate game plan |
| POST | `/api/agents/awards/match` | Match awards |
| POST | `/api/agents/assessment/process` | Process assessment |

#### POST /api/agents/game-plan/generate

**Request:**
```json
{
  "profile_id": "uuid",
  "regenerate": false
}
```

**Response:**
```json
{
  "success": true,
  "game_plan": {
    "id": "uuid",
    "version": 1,
    "years": [
      {
        "year": "Freshman",
        "focus": "Foundation Building",
        "projects": [...]
      }
    ]
  }
}
```

---

## Frontend API Routes (Next.js)

**Location:** `/app/api/`

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/callback` | OAuth callback |
| POST | `/api/auth/signout` | Sign out |

### Data Proxies

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profile` | Get current user profile |
| PUT | `/api/profile` | Update profile |
| GET | `/api/assessment/{frame}` | Get frame data |
| POST | `/api/assessment/{frame}` | Save frame data |

---

## Error Handling

### Standard Error Response

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request |
| 401 | Unauthorized |
| 404 | Not found |
| 500 | Server error |
| 503 | Service unavailable (feature disabled) |

---

## Authentication

### Backend API
- Uses Supabase JWT tokens
- Pass token in `Authorization: Bearer <token>` header

### Frontend API
- Uses Supabase session cookies
- Automatic via `@supabase/auth-helpers-nextjs`

---

## Rate Limits

| Endpoint Type | Limit |
|---------------|-------|
| Health checks | Unlimited |
| Read endpoints | 100/min |
| Write endpoints | 30/min |
| AI generation | 10/min |

---

## WebSocket (Future)

WebSocket support for real-time updates is planned for v11.0:
- `/ws/notifications` - Real-time proactive notifications
- `/ws/chat` - Streaming chat responses
