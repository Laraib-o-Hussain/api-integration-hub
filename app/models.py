from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    patient_name: Mapped[str] = mapped_column(String(120))
    patient_id: Mapped[str] = mapped_column(String(64), index=True)
    doctor_name: Mapped[str] = mapped_column(String(120))
    appointment_date: Mapped[str] = mapped_column(String(10))  # YYYY-MM-DD
    appointment_time: Mapped[str] = mapped_column(String(5))   # HH:MM
    status: Mapped[str] = mapped_column(String(32), default="scheduled")
    sync_status: Mapped[str] = mapped_column(String(32), default="not_synced")
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
