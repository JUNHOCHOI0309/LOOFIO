from datetime import date

from pydantic import BaseModel, Field


class Money(BaseModel):
    amount: str
    currency: str = "KRW"


class DailyAppointmentMetric(BaseModel):
    date: date
    appointment_count: int = Field(ge=0)
    completed_count: int = Field(ge=0)
    cancelled_count: int = Field(ge=0)
    no_show_count: int = Field(ge=0)
    actual_revenue: Money


class TimeSlotAppointmentMetric(BaseModel):
    weekday: str
    slot_start_hour: int = Field(ge=0, le=22)
    appointment_count: int = Field(ge=0)
    completed_count: int = Field(ge=0)
    cancelled_count: int = Field(ge=0)
    cancellation_rate: float = Field(ge=0, le=1)
    actual_revenue: Money


class AppointmentMetrics(BaseModel):
    metric_version: str
    period_start: date | None = None
    period_end: date | None = None
    observed_weeks: int = Field(ge=0)
    appointment_count: int = Field(ge=0)
    completed_count: int = Field(ge=0)
    cancelled_count: int = Field(ge=0)
    no_show_count: int = Field(ge=0)
    cancellation_rate: float = Field(ge=0, le=1)
    actual_revenue: Money
    average_completed_revenue: Money | None = None
    daily: list[DailyAppointmentMetric]
    time_slots: list[TimeSlotAppointmentMetric]
    limitations: list[str]
