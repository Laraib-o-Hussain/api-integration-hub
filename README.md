# API Integration Hub

Small FastAPI demo that pretends to be an appointment sync service between systems.

Nothing here talks to a real clinic or real patient data. It's just CRUD + a fake "sync to external system" endpoint so I can show REST, validation, SQLite, Docker, and Postman on my profile.

## Stack

- Python / FastAPI / Pydantic
- SQLAlchemy + SQLite
- Docker / docker-compose
- pytest
- Postman collection in `postman/`

## Run locally

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs for the interactive API docs.

## Run with Docker

```bash
docker compose up --build
```

API will be on http://localhost:8000

## Endpoints

| Method | Path | What it does |
|--------|------|--------------|
| GET | `/` | tiny welcome payload |
| GET | `/health` | health check |
| POST | `/appointments` | create |
| GET | `/appointments/{id}` | get one |
| PUT | `/appointments/{id}` | update |
| DELETE | `/appointments/{id}` | delete |
| POST | `/appointments/{id}/sync` | fake push to another system |

## Example create body

```json
{
  "patient_name": "Ava Chen",
  "patient_id": "P-1001",
  "doctor_name": "Dr. Rivera",
  "appointment_date": "2026-10-15",
  "appointment_time": "09:30",
  "status": "scheduled"
}
```

Valid statuses: `scheduled`, `confirmed`, `cancelled`, `completed`, `synced`

## Tests

```bash
pytest -v
```

## Postman

Import `postman/API_Integration_Hub.postman_collection.json` and hit the requests against `http://localhost:8000`.
