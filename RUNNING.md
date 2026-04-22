# Quick Start (Windows)

## 1) Create and activate virtual environment

```powershell
python -m venv venv
.\\venv\\Scripts\\Activate.ps1
```

## 2) Install dependencies

```powershell
pip install -r requirements.txt
```

## 3) Prepare environment file

```powershell
Copy-Item .env.example .env -Force
```

Fill database settings in `.env` before calling database APIs.

## 4) Start API from project root

Option A:

```powershell
python run.py
```

Option B:

```powershell
.\\run.ps1
```

Option C (direct command):

```powershell
python -m uvicorn app.main:app --app-dir src --host 0.0.0.0 --port 8000 --reload
```

## 5) Open API docs

- http://localhost:8000/docs
- http://localhost:8000/redoc

## Notes

- This project uses src layout, so `python src\\app\\main.py` used to fail with import path issues.
- It now supports direct script run as well, but root-level start (`python run.py`) is the recommended flow.
