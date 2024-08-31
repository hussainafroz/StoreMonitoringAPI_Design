
import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Generic, TypeVar

from models import StoreStatus

# BASEMODELS (Pydantic Models)


class StoreStatusLogCreate(BaseModel):
    store_id: int
    timestamp_utc: datetime
    status: StoreStatus

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class StoreBusinessHoursCreate(BaseModel):
    store_id: int
    day_of_week: int
    start_time_local: datetime.time
    end_time_local: datetime.time

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class StoreTimeZoneCreate(BaseModel):
    store_id: int
    timezone_str: str = Field(default="America/Chicago")

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ReportBase(BaseModel):
    store_id: Optional[int] = None
    uptime_last_hour: Optional[float] = 0.0
    uptime_last_day: Optional[float] = 0.0
    uptime_last_week: Optional[float] = 0.0
    downtime_last_hour: Optional[float] = 0.0
    downtime_last_day: Optional[float] = 0.0
    downtime_last_week: Optional[float] = 0.0
    status: str

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
