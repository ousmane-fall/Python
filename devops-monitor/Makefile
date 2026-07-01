.PHONY: install test lint format run-api run-dashboard build up down logs clean

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=api --cov-report=term-missing --cov-fail-under=75

lint:
	black --check api/ dashboard/ tests/
	flake8 api/ dashboard/ tests/

format:
	black api/ dashboard/ tests/

run-api:
	uvicorn api.main:app --reload --port 8000

run-dashboard:
	streamlit run dashboard/app.py

build:
	docker compose build

up: build
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

clean:
	docker compose down --rmi all --volumes
