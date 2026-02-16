# Railway Deployment Configuration

This repository is configured for seamless deployment to Railway with the following files:

## Configuration Files

### 1. `package.json` (Root)
Orchestrates the monorepo build process:
- **Build**: Installs frontend/backend dependencies and builds frontend
- **Start**: Launches FastAPI server with uvicorn
- **Node Version**: >=18 <=22

### 2. `railway.json`
Railway-specific configuration:
- **Builder**: Nixpacks (auto-detected from package.json)
- **Build Command**: `npm run build`
- **Start Command**: `npm run start:prod`
- **Restart Policy**: ON_FAILURE with 5 max retries

### 3. `Procfile`
Process configuration:
```
web: npm run start:prod
```

### 4. `.railwayignore`
Excludes unnecessary files from deployment (tests, docs, temp files, etc.)
**Note**: `frontend/build/` is NOT excluded as it contains production assets

## Deployment Flow

1. **Railway detects** `package.json` in root directory
2. **Build Phase**: Runs `npm run build`
   - Installs frontend dependencies with `--legacy-peer-deps`
   - Builds React app to `frontend/build/`
   - Installs Python backend dependencies
3. **Start Phase**: Runs `npm run start:prod`
   - Starts uvicorn server on PORT (Railway provides this)
   - Backend serves API routes (`/api/*`) and frontend SPA (`/*`)

## Architecture

```
┌─────────────────────────────────────────┐
│  Railway (Port from env, default 3000)  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│     FastAPI Backend (uvicorn)           │
│  ┌───────────────────────────────────┐  │
│  │  API Routes (/api/*)              │  │
│  │  - /api/auth/*                    │  │
│  │  - /api/projects/*                │  │
│  │  - /api/ai/*                      │  │
│  │  - etc.                           │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Static Files (/static/*)         │  │
│  │  - Serves frontend/build/static/  │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  SPA Routes (/*)                  │  │
│  │  - Serves frontend/build/index.html│ │
│  │  - Handles client-side routing   │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Environment Variables

Required environment variables for Railway:
- `MONGODB_URI` - MongoDB connection string
- `OPENAI_API_KEY` or `LLM_API_KEY` - AI API keys
- `ANTHROPIC_API_KEY` - Claude API key
- `GEMINI_API_KEY` - Google Gemini API key
- `JWT_SECRET` - Secret for JWT token generation
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)
- `PORT` - Auto-provided by Railway (defaults to 3000)

## Local Development

```bash
# Install dependencies and build
npm run build

# Start production server
npm run start:prod

# Or for development:
# Terminal 1: Frontend dev server
npm run dev:frontend

# Terminal 2: Backend dev server
npm run dev:backend
```

## Troubleshooting

### Build fails with dependency conflicts
- Frontend uses `--legacy-peer-deps` to resolve React 19 peer dependency issues

### Server doesn't start
- Check that PORT environment variable is set
- Verify all required environment variables are configured
- Check Railway logs for specific error messages

### Frontend not loading
- Verify `frontend/build/` directory exists and contains files
- Check that `.railwayignore` doesn't exclude the build directory
- Ensure static file serving is working: `GET /static/js/main.*.js`

## Documentation

See [docs/RAILWAY_DEPLOYMENT_GUIDE.md](docs/RAILWAY_DEPLOYMENT_GUIDE.md) for detailed deployment instructions.
