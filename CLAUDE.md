# Gase-Y Pipeline

## Overview
Multi-platform video generation & social media sharing automation pipeline.
Kullanıcı bir prompt girer → AI analiz eder → video generate eder → çoklu platformlara otomatik paylaşım yapar.

## Tech Stack

### Backend
- **Python 3.11+** / FastAPI / Uvicorn
- **PostgreSQL 16** + SQLAlchemy 2.0 (async) + Alembic
- **Celery** + Redis (task queue & scheduling)
- **FFmpeg** + ffmpeg-python (video processing)
- **Pydantic v2** (validation & settings)

### Frontend
- **React 18+** / TypeScript / Vite
- **Tailwind CSS** + shadcn/ui
- **Zustand** (state) + TanStack React Query (data fetching)
- **Axios** (HTTP) + React Router v6

### AI Services (pluggable - user selects)
- **LLM**: OpenAI GPT, Anthropic Claude
- **TTS**: ElevenLabs, Google Cloud TTS
- **Image**: Stability AI, DALL-E
- **Translation**: AI provider reuse, DeepL

### Social Platforms
- YouTube (default), Instagram, Twitter/X, Reddit, TikTok

### Infrastructure
- Docker + Docker Compose
- Nginx reverse proxy
- MinIO / S3-compatible storage

---

## Project Structure
```
backend/app/
├── main.py              # FastAPI app factory
├── config.py            # pydantic-settings
├── dependencies.py      # DI
├── core/                # security, exceptions, middleware
├── db/                  # session, base
├── models/              # SQLAlchemy ORM
├── schemas/             # Pydantic request/response
├── api/v1/              # Route handlers
├── services/            # Business logic (orchestrator, video_composer, publisher...)
├── providers/           # External service adapters (ai/, tts/, image/, platforms/)
├── workers/             # Celery tasks
└── utils/               # ffmpeg helpers, storage, validators

frontend/src/
├── api/                 # API client modules
├── components/          # UI components (layout/, video/, common/, analytics/)
├── pages/               # Route pages
├── hooks/               # Custom hooks
├── stores/              # Zustand stores
└── types/               # TypeScript types
```

## Development

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- FFmpeg

### Quick Start
```bash
cp .env.example .env
docker compose up -d db redis
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### Running
```bash
# Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm run dev

# Celery worker
cd backend && celery -A app.workers.celery_app worker -l info

# Full stack (Docker)
docker compose up
```

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Testing
```bash
cd backend && pytest
cd frontend && npm test
```

---

## Architecture

### Video Generation Pipeline
```
Prompt → Prompt Analyzer (AI) → Script Generator (AI) → Translation
→ TTS (per language, parallel) → Video Composer (FFmpeg) → Thumbnail (AI)
→ SEO Optimizer (AI) → Publisher (Platform APIs)
```

### Provider Pattern
All external services use factory pattern. User preferences stored in DB (JSONB).
Override per-project in project settings.

### Multi-Language Logic
- Video içinde yazı → Her dil için ayrı video_variant (TTS + overlay çevrilir)
- Sadece açıklama → 1 video + her dil için ayrı publish_job

### Key Design Patterns
- **Factory Pattern**: AI, TTS, Image, Platform providers
- **Repository Pattern**: DB access layer
- **Task Chain**: Celery chain() + group() for pipeline orchestration
- **Abstract Base**: All providers extend base classes for swappability

---

## API Routes (v1)
- `POST /api/v1/auth/register|login|refresh` - Auth
- `GET|POST /api/v1/projects` - Project CRUD
- `POST /api/v1/videos` - Trigger video generation
- `POST /api/v1/publish` - Publish to platforms
- `GET /api/v1/platforms` - Connected social accounts
- `GET /api/v1/templates` - Video templates
- `GET /api/v1/analytics/overview` - Performance metrics
- `WS /ws/jobs/{user_id}` - Real-time job status

---

## Environment Variables
See `.env.example` for full list. Key variables:
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `SECRET_KEY` - JWT signing key
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Claude API key
- `ELEVENLABS_API_KEY` - ElevenLabs TTS
- `YOUTUBE_CLIENT_ID` / `YOUTUBE_CLIENT_SECRET` - YouTube OAuth2
- `S3_ENDPOINT` / `S3_ACCESS_KEY` / `S3_SECRET_KEY` - Storage
