# SevaSetu AI — Single-URL Render Deployment

This deployment runs the React frontend and FastAPI backend from **one Render Web Service and one public URL**.

## Render settings

- Type: **Web Service**
- Name: `sevasetu-ai`
- Environment: `Production`
- Language: `Python 3`
- Branch: `main`
- Region: `Oregon`
- Root Directory: **blank / repository root**
- Build Command: `pip install -r backend/requirements.txt && cd frontend && npm install && npm run build`
- Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/health`

## How routing works

- `/` and React routes are served by the React production build.
- `/api/v1/*` is handled by FastAPI.
- `/health` is the backend health check.
- `/docs` is FastAPI Swagger.

The frontend automatically uses `window.location.origin` for API calls in production, so no separate backend domain is required.

## Required Render secrets

Set these in Render Environment Variables:

- `GEMINI_API_KEY`
- `DATABASE_URL`
- `REDIS_URL`

Render generates `SECRET_KEY` automatically from `render.yaml`.

## Important

Do not commit `.env`, Gemini keys, database passwords, SMTP passwords, or other secrets to GitHub.
