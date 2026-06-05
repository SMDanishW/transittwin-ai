# TransitTwin AI

A real-time digital twin for HSL public transport in the Helsinki metropolitan area (Helsinki, Espoo, Vantaa). Live vehicle positions stream from the HSL GTFS-RT feed, a simulation engine models disruption impact using PostGIS spatial queries, and a LangGraph AI agent answers natural-language questions about the network.

![Tech Stack](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js)
![MapLibre](https://img.shields.io/badge/MapLibre_GL-3D_map-396CB2?style=flat-square)
![LangGraph](https://img.shields.io/badge/LangGraph-ReAct_agent-orange?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-qwen3--32b-F55036?style=flat-square)

---

## Features

| Feature | Details |
|---|---|
| **Live map** | 3D MapLibre GL map, vehicle positions update every 3 s via SSE, colour-coded by mode (Bus / Tram / Metro / Rail / Ferry), WebGL clustering at low zoom |
| **Disruption simulation** | PostGIS `ST_DWithin` spatial queries, passenger impact scoring (0–100), alternative route detection, affected-stop flyover on the map |
| **AI assistant** | LangGraph ReAct agent powered by Groq `qwen/qwen3-32b` with four live-data tools: active disruptions, fleet summary, simulation runner, stop lookup |
| **SSE streaming** | Browser-native `EventSource` — no WebSocket overhead; vehicles every 3 s, alerts every 15 s |
| **Background worker** | Arq cron jobs poll HSL GTFS-RT every 5 s (vehicles), 10 s (trip updates), 30 s (alerts) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Browser (Next.js 15 + MapLibre GL)                     │
│  SSE ← /api/sse/vehicles   /api/sse/alerts              │
│  REST POST /api/simulation/run   /api/agent/chat         │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP
┌────────────────────▼────────────────────────────────────┐
│  FastAPI backend                                        │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐ │
│  │ Routers  │  │ Simulation   │  │ LangGraph Agent   │ │
│  │ vehicles │  │ Engine       │  │ (Groq qwen3-32b)  │ │
│  │ alerts   │  │ PostGIS      │  │ 4 live-data tools │ │
│  │ stops    │  │ ST_DWithin   │  └───────────────────┘ │
│  │ routes   │  └──────────────┘                        │
│  └──────────┘                                          │
└──────┬──────────────────────────────┬──────────────────┘
       │ asyncpg                      │ redis-py
┌──────▼──────┐               ┌───────▼──────┐
│  PostgreSQL │               │    Redis     │
│  + PostGIS  │               │ hsl:vehicles │
│  stops      │               │ hsl:alerts   │
│  routes     │               │ hsl:route_   │
└─────────────┘               │   modes      │
                              └──────▲───────┘
                                     │ writes every 5 s
                              ┌──────┴───────┐
                              │  Arq Worker  │
                              │  GTFS-RT     │
                              │  polling     │
                              └──────────────┘
```

---

## Tech Stack

**Backend**
- Python 3.11 · FastAPI · Uvicorn
- SQLAlchemy 2 (async) + asyncpg · GeoAlchemy2 · PostGIS
- Arq (async Redis job queue) for GTFS-RT cron polling
- LangGraph + LangChain · Groq Cloud (`qwen/qwen3-32b`)
- httpx · gtfs-realtime-bindings · Shapely · Pydantic v2

**Frontend**
- Next.js 15 App Router · TypeScript · Tailwind CSS
- MapLibre GL JS (3D buildings, WebGL clustering)
- Zustand (global state) · `useShallow` for stable selectors
- Browser-native `EventSource` (SSE)

**Infrastructure**
- PostgreSQL 16 + PostGIS 3.4
- Redis 7
- Docker Compose (local) / AWS EKS (production)

---

## Prerequisites

- Docker Desktop
- Node.js 20+
- Python 3.11+
- A [Groq Cloud](https://console.groq.com) API key (free tier is sufficient)
- *(Optional)* An [HSL Digitransit](https://digitransit.fi/en/developers/) API key for seeding real stop/route data
- *(Optional for live GTFS-RT outside Finland)* A VPN exit node in the EU; deploy on AWS `eu-north-1` for production

---

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/your-org/transit-twin-ai.git
cd transit-twin-ai
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/transittwin
REDIS_URL=redis://localhost:6380

# Groq — required for the AI assistant
GROQ_API_KEY=gsk_...

# Digitransit — optional; set USE_MOCK_SEED=true to skip
DIGITRANSIT_API_KEY=
USE_MOCK_SEED=true
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Start infrastructure

```bash
docker compose up db redis -d
```

> Redis is mapped to **6380** (not 6379) to avoid conflicts with a local Redis instance.

### 3. Start the backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

On first start the backend seeds stops and routes into PostGIS. With `USE_MOCK_SEED=true` it uses 17 real Helsinki stops and 13 real routes without needing the Digitransit API.

### 4. Start the GTFS-RT worker (separate terminal)

```bash
cd backend
source .venv/bin/activate
python worker.py
```

The worker polls the HSL GTFS-RT feed every 5 seconds. Watch the log for:
```
Vehicles stored: 857 | modes: {'BUS': 692, 'TRAM': 118, 'RAIL': 22, 'METRO': 18, 'FERRY': 3}
```

> **Geo-restriction**: The HSL GTFS-RT feed (`realtime.hsl.fi`) is accessible from EU IP addresses. Use a desktop VPN (not a browser extension) if you are outside the EU.

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Running with Docker Compose (full stack)

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |

---

## Project Structure

```
transit-twin-ai/
├── backend/
│   ├── app/
│   │   ├── agent/          # LangGraph ReAct agent + tools
│   │   ├── models/         # SQLAlchemy ORM (Stop, Route)
│   │   ├── routers/        # FastAPI routers (vehicles, alerts, simulation, agent…)
│   │   ├── schemas/        # Pydantic request/response models
│   │   ├── services/       # GTFS-RT parser, simulation engine, Digitransit client
│   │   ├── workers/        # Arq cron worker
│   │   ├── config.py       # pydantic-settings
│   │   ├── database.py     # async SQLAlchemy + PostGIS init
│   │   └── redis_client.py # singleton Redis connection
│   ├── worker.py           # Arq worker entry point
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   └── dashboard/
│   │   │       ├── live/         # Live vehicle map
│   │   │       ├── simulation/   # Disruption simulation
│   │   │       ├── assistant/    # AI chat
│   │   │       └── system/       # System health
│   │   ├── components/
│   │   │   ├── map/              # DigitalTwinMap (MapLibre GL)
│   │   │   ├── panels/           # RightPanel, DisruptionList
│   │   │   └── ui/               # Header
│   │   ├── hooks/                # useVehicleSSE, useAlertSSE
│   │   ├── store/                # Zustand dashboardStore
│   │   └── types/                # TypeScript interfaces
│   ├── Dockerfile
│   └── next.config.ts
│
└── docker-compose.yml
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/api/vehicles` | Current vehicles from Redis |
| `GET` | `/api/alerts` | Current service alerts |
| `GET` | `/api/stops` | All seeded stops |
| `GET` | `/api/routes` | All seeded routes |
| `GET` | `/api/sse/vehicles` | SSE stream — vehicle positions (3 s) |
| `GET` | `/api/sse/alerts` | SSE stream — service alerts (15 s) |
| `POST` | `/api/simulation/run` | Run disruption impact simulation |
| `POST` | `/api/agent/chat` | LangGraph AI agent (natural language) |

Interactive docs: **http://localhost:8000/docs**

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | ✅ | — | asyncpg connection string |
| `REDIS_URL` | ✅ | `redis://localhost:6379` | Redis connection string |
| `GROQ_API_KEY` | ✅ | — | Groq Cloud API key |
| `DIGITRANSIT_API_KEY` | ⬜ | `""` | HSL Digitransit subscription key |
| `USE_MOCK_SEED` | ⬜ | `false` | Skip Digitransit, use bundled fixtures |
| `GTFS_RT_BASE_URL` | ⬜ | `https://realtime.hsl.fi/realtime` | GTFS-RT feed base URL |

### Frontend (`frontend/.env.local`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | ⬜ | `http://localhost:8000` | Backend base URL |

---

## Mode Inference

HSL commuter rail route IDs carry a letter suffix (`3001A`, `3001D` …). Because the GTFS-RT protobuf does not include `route_type`, the worker infers mode from the route ID pattern:

| Pattern | Mode |
|---|---|
| Contains `M` (e.g. `31M1`, `31M2`) | METRO |
| Exactly `1019` | FERRY |
| Leading digits 1001–1012 | TRAM |
| Leading digits 3001–3030 (e.g. `3001A`) | RAIL |
| Everything else | BUS |

If the Digitransit seed is available, the `hsl:route_modes` Redis key takes priority over pattern matching.

---

## Deployment

The project targets **AWS EKS** (`eu-north-1` / Stockholm) so the backend has direct access to the geo-restricted HSL GTFS-RT feeds without a VPN. Kubernetes manifests are in `k8s/` (Step 11).

Each service has a multi-stage `Dockerfile`; the frontend uses `output: "standalone"` for minimal image size.

---

## License

MIT
