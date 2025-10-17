# 🏰 Hack Knight

A full-stack application template with Next.js frontend, FastAPI backend, and Docker containerization.

## Tech Stack

- **Frontend**: Next.js 14 (React, TypeScript)
- **Backend**: FastAPI (Python)
- **Containerization**: Docker & Docker Compose

## Project Structure

```
hack-knight/
├── frontend/           # Next.js application
│   ├── app/           # App router pages
│   ├── Dockerfile     # Production Dockerfile
│   └── Dockerfile.dev # Development Dockerfile
├── backend/           # FastAPI application
│   ├── main.py        # FastAPI app entry point
│   ├── Dockerfile     # Production Dockerfile
│   └── Dockerfile.dev # Development Dockerfile
├── docker-compose.yml     # Production compose file
└── docker-compose.dev.yml # Development compose file
```

## Quick Start

### Development Mode (Recommended)

Start both frontend and backend with hot-reloading:

```bash
docker-compose -f docker-compose.dev.yml up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

To stop:
```bash
docker-compose -f docker-compose.dev.yml down
```

### Production Mode

Build and run production containers:

```bash
docker-compose up --build
```

To stop:
```bash
docker-compose down
```

## Local Development (Without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend will run on http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on http://localhost:3000

## Available Commands

### Docker Commands

| Command | Description |
|---------|-------------|
| `docker-compose -f docker-compose.dev.yml up` | Start development servers |
| `docker-compose -f docker-compose.dev.yml up --build` | Rebuild and start dev servers |
| `docker-compose -f docker-compose.dev.yml down` | Stop dev servers |
| `docker-compose up` | Start production build |
| `docker-compose down` | Stop production build |

### Frontend Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |

### Backend Commands

| Command | Description |
|---------|-------------|
| `uvicorn main:app --reload` | Start with hot reload |
| `uvicorn main:app` | Start production server |
| `python main.py` | Alternative start method |

## API Endpoints

- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check endpoint
- `GET /api/hello` - Sample API endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Environment Variables

### Frontend

Create `.env.local` in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend

Create `.env` in the backend directory:

```env
ENVIRONMENT=development
```

## Features

- ✅ Next.js 14 with App Router
- ✅ TypeScript support
- ✅ FastAPI with automatic API docs
- ✅ Docker containerization
- ✅ Docker Compose orchestration
- ✅ Hot-reloading in development mode
- ✅ CORS configuration
- ✅ Health check endpoints
- ✅ Modern, responsive UI

## Development Tips

1. **Hot Reloading**: In dev mode, changes to code will automatically reload
2. **Volume Mounting**: Your local files are mounted in containers for instant updates
3. **API Documentation**: Visit `/docs` endpoint for interactive API testing
4. **Network**: Both services communicate via Docker network

## Troubleshooting

### Port Already in Use

If ports 3000 or 8000 are in use, you can modify them in `docker-compose.dev.yml`:

```yaml
ports:
  - "3001:3000"  # Change host port (left side)
```

### Container Issues

Remove all containers and rebuild:

```bash
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up --build
```

### Node Modules Issues

If you have permission issues with node_modules:

```bash
docker-compose -f docker-compose.dev.yml down -v
docker volume prune
docker-compose -f docker-compose.dev.yml up --build
```

## License

MIT

## Contributing

Feel free to submit issues and pull requests!

