# Hack Knight - Project Context Documentation

## Project Overview

Hack Knight is a full-stack application template designed with modern web development best practices. It provides a complete boilerplate setup for building scalable web applications with a React-based frontend and Python backend, fully containerized with Docker.

### Tech Stack

- **Frontend**: Next.js 14 (React 18.3, TypeScript 5.0)
- **Backend**: FastAPI 0.109 (Python 3.11)
- **Containerization**: Docker & Docker Compose
- **Development Tools**: Hot-reloading, TypeScript, ESLint

### Key Features

- Modern React framework with Next.js App Router
- Fast and type-safe Python backend with FastAPI
- Fully containerized development and production environments
- Hot-reloading for rapid development
- CORS configuration for cross-origin requests
- Automatic API documentation (Swagger UI and ReDoc)
- Health check endpoints
- Beautiful, responsive UI with modern design
- TypeScript support for type safety

### Project Structure

```
hack-knight/
├── frontend/                    # Next.js application
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout component
│   │   ├── page.tsx            # Home page with API integration
│   │   ├── globals.css         # Global styles
│   │   └── page.module.css     # Page-specific styles
│   ├── package.json            # Node.js dependencies
│   ├── tsconfig.json           # TypeScript configuration
│   ├── next.config.js          # Next.js configuration
│   ├── Dockerfile              # Production Docker image
│   ├── Dockerfile.dev          # Development Docker image
│   └── .dockerignore           # Docker ignore patterns
│
├── backend/                    # FastAPI application
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Production Docker image
│   ├── Dockerfile.dev          # Development Docker image
│   └── .dockerignore           # Docker ignore patterns
│
├── docs/                       # Project documentation
│   └── PROJECT_CONTEXT.md      # This file
│
├── docker-compose.yml          # Production orchestration
├── docker-compose.dev.yml      # Development orchestration
└── README.md                   # User-facing documentation
```

## Architecture

### Frontend Architecture

**Next.js 14 with App Router**

The frontend uses Next.js 14's App Router architecture, which provides:

- **Server Components**: React Server Components by default for better performance
- **Client Components**: Explicitly marked with `'use client'` directive for interactivity
- **File-based Routing**: Routes defined by the file structure in `/app` directory
- **Layouts**: Shared UI components across routes via `layout.tsx`

**Key Configuration:**

```javascript
// next.config.js
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',  // Required for Docker production builds
}
```

The `output: 'standalone'` setting enables Next.js to create a minimal production build suitable for containerization, reducing image size.

**API Integration:**

The frontend communicates with the backend via fetch API:
- Environment variable `NEXT_PUBLIC_API_URL` configures the backend URL
- Default: `http://localhost:8000` for local development
- In Docker: `http://backend:8000` for internal network communication

**TypeScript Configuration:**

- Strict mode enabled for type safety
- Path aliases configured (`@/*` maps to root)
- Modern ES features with ESNext target
- Full DOM and library support

### Backend Architecture

**FastAPI with Python 3.11**

The backend uses FastAPI, a modern Python web framework:

```python
# main.py structure
app = FastAPI(
    title="Hack Knight API",
    description="Backend API for Hack Knight application",
    version="1.0.0"
)
```

**CORS Configuration:**

Cross-Origin Resource Sharing is configured to allow frontend communication:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**API Endpoints:**

- `GET /` - Root endpoint with welcome message and timestamp
- `GET /health` - Health check endpoint with status and environment info
- `GET /api/hello` - Sample API endpoint demonstrating structure
- `GET /docs` - Interactive Swagger UI documentation (auto-generated)
- `GET /redoc` - Alternative ReDoc documentation (auto-generated)

**Automatic Documentation:**

FastAPI automatically generates OpenAPI documentation accessible at `/docs` and `/redoc`, providing interactive API testing capabilities.

### Docker Containerization Strategy

#### Development Environment

**Development Dockerfiles:**

Both frontend and backend have separate development Dockerfiles optimized for hot-reloading:

**Frontend (Dockerfile.dev):**
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
```

**Backend (Dockerfile.dev):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**Development Compose (docker-compose.dev.yml):**

Key features:
- Volume mounting for hot-reloading: local code is mounted into containers
- Separate volumes for `node_modules` and `.next` to prevent conflicts
- `--reload` flag for uvicorn enables automatic backend reload on code changes
- `WATCHPACK_POLLING=true` ensures file watching works in Docker
- Anonymous volumes for `__pycache__` to prevent permission issues

#### Production Environment

**Production Dockerfiles:**

Optimized for minimal size and security:

**Frontend (Dockerfile):**
- Multi-stage build to reduce final image size
- Dependencies installed in separate stage
- Production build created with `npm run build`
- Runs with minimal Node.js runtime
- Non-root user (nextjs:nodejs) for security
- Standalone output utilized for optimal performance

**Backend (Dockerfile):**
- Based on slim Python image
- Only production dependencies installed
- No development tools included
- Runs uvicorn without reload flag for stability

**Production Compose (docker-compose.yml):**
- No volume mounting for code (using built artifacts)
- Optimized for deployment
- Configured for production stability

### Network Setup

**Docker Network:**

Both services communicate via a Docker bridge network:

```yaml
networks:
  hack-knight-network:
    driver: bridge
```

**Service Communication:**

- Frontend → Backend: Uses internal Docker DNS (`backend:8000`)
- External access: Mapped ports (3000 for frontend, 8000 for backend)
- `depends_on` ensures backend starts before frontend

### Volume Mounting Strategy

**Development Mode:**

Frontend volumes:
```yaml
volumes:
  - ./frontend:/app           # Mount source code
  - /app/node_modules         # Anonymous volume for dependencies
  - /app/.next                # Anonymous volume for build cache
```

Backend volumes:
```yaml
volumes:
  - ./backend:/app            # Mount source code
  - /app/__pycache__          # Anonymous volume for Python cache
```

This strategy:
- Enables hot-reloading by mounting source code
- Prevents node_modules conflicts between host and container
- Avoids permission issues with cache directories
- Maintains fast file watching and rebuild times

## Setup Instructions

### Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For cloning the repository

Verify installations:
```bash
docker --version
docker-compose --version
```

### Initial Setup

1. **Clone or navigate to the project:**
```bash
cd /path/to/hack-knight
```

2. **Review environment variables (optional):**

Frontend environment (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Backend environment (`.env`):
```env
ENVIRONMENT=development
```

### Development Mode Startup

**Start both services with hot-reloading:**

```bash
docker-compose -f docker-compose.dev.yml up --build
```

For running in the background (detached mode):
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

The `--build` flag ensures images are rebuilt with latest code changes.

**First-time startup may take 2-5 minutes** as it:
- Downloads base images (Node.js, Python)
- Installs all dependencies
- Builds initial containers

Subsequent startups are much faster (10-30 seconds).

### Production Mode Startup

**Build and run production-optimized containers:**

```bash
docker-compose up --build
```

For detached mode:
```bash
docker-compose up -d --build
```

### Access URLs

Once containers are running:

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Development Workflow

### Running Services in Detached Mode

**Start in background:**
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

Benefits:
- Terminal remains available for other commands
- Services run in background
- No console output unless requested

### Hot-Reloading Capabilities

**Frontend (Next.js):**
- Automatic reload on file changes
- Fast Refresh preserves component state
- CSS updates without full reload
- Works for all files in `app/` directory

**Backend (FastAPI):**
- Uvicorn with `--reload` flag watches for changes
- Automatic server restart on `.py` file modifications
- Fast restart time (1-2 seconds)

**Making changes:**
1. Edit any file in `frontend/` or `backend/`
2. Save the file
3. Wait 1-3 seconds for automatic reload
4. Refresh browser (or see changes automatically)

### Viewing Logs

**View logs from all services:**
```bash
docker-compose -f docker-compose.dev.yml logs -f
```

**View logs from specific service:**
```bash
# Frontend logs only
docker-compose -f docker-compose.dev.yml logs -f frontend

# Backend logs only
docker-compose -f docker-compose.dev.yml logs -f backend
```

**View last N lines:**
```bash
docker-compose -f docker-compose.dev.yml logs --tail=50 frontend
```

The `-f` flag follows logs in real-time (like `tail -f`).

### Managing Services

**Check service status:**
```bash
docker-compose -f docker-compose.dev.yml ps
```

**Restart specific service:**
```bash
docker-compose -f docker-compose.dev.yml restart frontend
docker-compose -f docker-compose.dev.yml restart backend
```

**Restart all services:**
```bash
docker-compose -f docker-compose.dev.yml restart
```

**Stop services (keeps containers):**
```bash
docker-compose -f docker-compose.dev.yml stop
```

**Start stopped services:**
```bash
docker-compose -f docker-compose.dev.yml start
```

**Stop and remove containers:**
```bash
docker-compose -f docker-compose.dev.yml down
```

**Stop, remove containers, and volumes:**
```bash
docker-compose -f docker-compose.dev.yml down -v
```

### Environment Variables

**Frontend Environment Variables:**

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Note: Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser.

**Backend Environment Variables:**

Create `backend/.env`:
```env
ENVIRONMENT=development
# Add database URLs, API keys, etc.
```

After changing environment variables, rebuild containers:
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

### API Development

**Available Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with API info |
| GET | `/health` | Health check status |
| GET | `/api/hello` | Sample endpoint |
| GET | `/docs` | Interactive API docs |
| GET | `/redoc` | Alternative API docs |

**Adding New Endpoints:**

1. Open `backend/main.py`
2. Add new route:
```python
@app.get("/api/your-endpoint")
async def your_function():
    return {"message": "Your response"}
```
3. Save file (auto-reloads in 1-2 seconds)
4. Visit http://localhost:8000/docs to test

**Testing API:**
- Use Swagger UI at `/docs` for interactive testing
- Use curl: `curl http://localhost:8000/api/hello`
- Use frontend fetch calls from Next.js

### Local Development Without Docker

**Backend (Alternative):**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Runs on http://localhost:8000

**Frontend (Alternative):**

```bash
cd frontend
npm install
npm run dev
```

Runs on http://localhost:3000

**When to use Docker vs Local:**
- Docker: Production parity, consistent environment, full-stack testing
- Local: Faster startup, easier debugging, IDE integration

### Common Development Commands

**Rebuild containers after dependency changes:**
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

**Execute commands inside running container:**
```bash
# Frontend
docker-compose -f docker-compose.dev.yml exec frontend npm install new-package

# Backend
docker-compose -f docker-compose.dev.yml exec backend pip install new-package
```

**Access container shell:**
```bash
# Frontend
docker-compose -f docker-compose.dev.yml exec frontend sh

# Backend
docker-compose -f docker-compose.dev.yml exec backend bash
```

**Clean up everything (fresh start):**
```bash
docker-compose -f docker-compose.dev.yml down -v
docker system prune -f
docker-compose -f docker-compose.dev.yml up -d --build
```

### Development Best Practices

1. **Always use detached mode** for background development
2. **Monitor logs** when testing new features
3. **Rebuild after dependency changes** (package.json, requirements.txt)
4. **Use health check endpoint** to verify backend is ready
5. **Check API docs** at `/docs` for endpoint testing
6. **Commit often** with descriptive messages
7. **Test in both Docker and production mode** before deploying

---

**Document Version**: 1.0  
**Last Updated**: October 17, 2025  
**Maintained By**: Development Team

