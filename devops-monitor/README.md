# DevOps Monitoring Dashboard

MVP Day 3: a FastAPI backend with live metrics, server CRUD, background polling, WebSocket
streaming, and a Streamlit dashboard.

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
set DISABLE_POLL_LOOP=1
pytest tests/ -v --cov=api --cov-fail-under=75
```

## Command shortcuts

### On Linux/macOS (with GNU Make)

```bash
make install         # Install dependencies
make test           # Run tests with coverage
make lint           # Check code quality
make format         # Format code with black
make run-api        # Start API server
make run-dashboard  # Start dashboard
make build          # Build Docker images
make up             # Start Docker stack
make down           # Stop Docker stack
make logs           # View logs
make clean          # Clean up
```

### On Windows (with make.bat)

```bash
make.bat install         # Install dependencies
make.bat test           # Run tests with coverage
make.bat lint           # Check code quality
make.bat format         # Format code with black
make.bat run-api        # Start API server
make.bat run-dashboard  # Start dashboard
```

Or run commands directly:

```bash
python -m pip install -r requirements.txt
python -m pytest tests/ -v --cov=api --cov-fail-under=75
python -m flake8 api/ dashboard/ tests/
python -m black api/ dashboard/ tests/
python -m uvicorn api.main:app --reload --port 8000
python -m streamlit run dashboard/app.py
```

## CI/CD (Day 4)

The GitHub Actions workflow is in:

- `.github/workflows/ci-cd.yml`

### Pipeline flow (without Azure):

1. **Lint and tests** on pull requests and pushes to `main`
   - Runs `black` and `flake8` for code formatting
   - Runs `pytest` with 75% coverage requirement

> **Note**: Azure deployment (build & push to ACR, deploy to Container Apps) is optional. To
> enable it, add the Azure secrets to your GitHub repository and uncomment/add the
> `build-and-push` and `deploy` jobs in the workflow.

## Environment variables

- `API_KEY`: API key used by protected routes and the dashboard form
- `API_BASE`: backend URL for the dashboard, defaults to `http://localhost:8000`
- `DISABLE_POLL_LOOP`: set to `1` to disable the background poller during tests
