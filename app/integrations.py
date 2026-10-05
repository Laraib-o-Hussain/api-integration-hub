"""Pretend we're calling some other clinic system. No real network call."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.models import Appointment


def push_to_external_system(appointment: Appointment) -> dict:
    # In a real integration you'd POST somewhere. Here we just fake success.
    return {
        "ok": True,
        "external_reference": f"EXT-{uuid4().hex[:10].upper()}",
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "patient_id": appointment.patient_id,
        "appointment_id": appointment.id,
    }
