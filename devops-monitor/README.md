# DevOps Monitoring Dashboard

MVP Day 3: a FastAPI backend with live metrics, server CRUD, background polling, WebSocket streaming, and a Streamlit dashboard.

## Structure

- `api/` FastAPI backend
- `dashboard/` Streamlit frontend
- `tests/` pytest checks

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create an environment file for Docker/Compose:

```bash
cp .env.example .env
```

## Run the API

```bash
uvicorn api.main:app --reload --port 8000
```

## Run the dashboard

```bash
streamlit run dashboard/app.py
```

## Run with Docker Compose (Day 4)

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f
```

Stop everything:

```bash
docker compose down
```

## Run tests

```bash
pytest tests/ -v
```

## Makefile shortcuts

```bash
make install
make test
make up
make logs
make down
```

## CI/CD (Day 4)

The GitHub Actions workflow is in:

- `.github/workflows/ci-cd.yml`

Pipeline flow:

1. Lint and tests on pull requests and pushes to `main`
2. Build and push Docker images to ACR on push to `main`
3. Deploy both containers to Azure Container Apps

Required GitHub secrets:

- `ACR_LOGIN_SERVER`
- `ACR_USERNAME`
- `ACR_PASSWORD`
- `AZURE_CREDENTIALS`
- `RG_NAME`
- `API_APP_NAME`
- `DASHBOARD_APP_NAME`

## Environment variables

- `API_KEY`: API key used by protected routes and the dashboard form
- `API_BASE`: backend URL for the dashboard, defaults to `http://localhost:8000`
- `DISABLE_POLL_LOOP`: set to `1` to disable the background poller during tests
