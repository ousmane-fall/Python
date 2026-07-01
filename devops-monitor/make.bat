@echo off
REM DevOps Monitoring Dashboard - Windows batch commands

setlocal

if "%1"=="" goto help
if "%1"=="install" goto install
if "%1"=="test" goto test
if "%1"=="lint" goto lint
if "%1"=="format" goto format
if "%1"=="run-api" goto run_api
if "%1"=="run-dashboard" goto run_dashboard
if "%1"=="help" goto help
goto unknown

:install
echo Installing dependencies...
python -m pip install -r requirements.txt
goto end

:test
echo Running tests with coverage...
set DISABLE_POLL_LOOP=1
python -m pytest tests/ -v --cov=api --cov-report=term-missing --cov-fail-under=75
goto end

:lint
echo Checking code with black and flake8...
python -m black --check api/ dashboard/ tests/
python -m flake8 api/ dashboard/ tests/ --max-line-length=100
goto end

:format
echo Formatting code with black...
python -m black api/ dashboard/ tests/ --line-length=100
goto end

:run_api
echo Starting FastAPI server on http://localhost:8000...
python -m uvicorn api.main:app --reload --port 8000
goto end

:run_dashboard
echo Starting Streamlit dashboard on http://localhost:8501...
python -m streamlit run dashboard/app.py
goto end

:unknown
echo Unknown command: %1
:help
echo.
echo Usage: make.bat [command]
echo.
echo Commands:
echo   install      Install dependencies from requirements.txt
echo   test         Run pytest with coverage (requires 75%%)
echo   lint         Check code quality with black and flake8
echo   format       Format code with black
echo   run-api      Start FastAPI server
echo   run-dashboard Start Streamlit dashboard
echo   help         Show this help message
echo.

:end
endlocal
