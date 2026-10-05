from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AppointmentStatus(str, Enum):
    scheduled = "scheduled"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    synced = "synced"


class AppointmentCreate(BaseModel):
    patient_name: str = Field(min_length=1, max_length=120)
    patient_id: str = Field(min_length=1, max_length=64)
    doctor_name: str = Field(min_length=1, max_length=120)
    appointment_date: str
    appointment_time: str
    status: AppointmentStatus = AppointmentStatus.scheduled

    @field_validator("appointment_date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("appointment_date must be YYYY-MM-DD") from exc
        return value

    @field_validator("appointment_time")
    @classmethod
    def validate_time(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%H:%M")
        except ValueError as exc:
            raise ValueError("appointment_time must be HH:MM (24h)") from exc
        return value


class AppointmentUpdate(BaseModel):
    patient_name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    patient_id: Optional[str] = Field(default=None, min_length=1, max_length=64)
    doctor_name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    status: Optional[AppointmentStatus] = None

    @field_validator("appointment_date")
    @classmethod
    def validate_date(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("appointment_date must be YYYY-MM-DD") from exc
        return value

    @field_validator("appointment_time")
    @classmethod
    def validate_time(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        try:
            datetime.strptime(value, "%H:%M")
        except ValueError as exc:
            raise ValueError("appointment_time must be HH:MM (24h)") from exc
        return value


class AppointmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_name: str
    patient_id: str
    doctor_name: str
    appointment_date: str
    appointment_time: str
    status: str
    sync_status: str
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class SyncResponse(BaseModel):
    appointment_id: int
    sync_status: str
    external_reference: str
    message: str
    appointment: AppointmentOut
