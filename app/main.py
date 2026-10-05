from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.integrations import push_to_external_system
from app.models import Appointment
from app.schemas import (
    AppointmentCreate,
    AppointmentOut,
    AppointmentUpdate,
    SyncResponse,
)

app = FastAPI(title=settings.app_name, version="0.1.0")

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/appointments", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    row = Appointment(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/appointments/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    row = db.get(Appointment, appointment_id)
    if not row:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return row


@app.put("/appointments/{appointment_id}", response_model=AppointmentOut)
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
):
    row = db.get(Appointment, appointment_id)
    if not row:
        raise HTTPException(status_code=404, detail="Appointment not found")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")

    for key, value in data.items():
        setattr(row, key, value.value if hasattr(value, "value") else value)

    db.commit()
    db.refresh(row)
    return row


@app.delete("/appointments/{appointment_id}", status_code=status.HTTP_200_OK)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    row = db.get(Appointment, appointment_id)
    if not row:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(row)
    db.commit()
    return {"message": "Appointment deleted", "id": appointment_id}


@app.post("/appointments/{appointment_id}/sync", response_model=SyncResponse)
def sync_appointment(appointment_id: int, db: Session = Depends(get_db)):
    row = db.get(Appointment, appointment_id)
    if not row:
        raise HTTPException(status_code=404, detail="Appointment not found")

    result = push_to_external_system(row)
    if not result.get("ok"):
        raise HTTPException(status_code=500, detail="External sync failed")

    row.sync_status = "synced"
    row.status = "synced"
    row.last_synced_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)

    return SyncResponse(
        appointment_id=row.id,
        sync_status=row.sync_status,
        external_reference=result["external_reference"],
        message="Synced to mock external system",
        appointment=AppointmentOut.model_validate(row),
    )
