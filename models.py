from datetime import datetime
import enum
from sqlalchemy import TIMESTAMP, Column, Float, Integer, DateTime, Enum, String, Time
from config import Base

# # POSTGRES MODELS


class StoreStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# Data-1


class StoreStatusLog(Base):
    __tablename__ = "store_status_log"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, index=True)
    timestamp_utc = Column(DateTime, index=True)
    status = Column(Enum(StoreStatus))

# Data-2


class StoreBusinessHours(Base):
    __tablename__ = "store_business_hours"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, index=True)
    day_of_week = Column(Integer)
    start_time_local = Column(Time)
    end_time_local = Column(Time)

# Data-3


class StoreTimeZone(Base):
    __tablename__ = "store_time_zone"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, index=True, unique=True)
    timezone_str = Column(String, default="America/Chicago")

# Enum for Report Status


class ReportStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"

# Final Report


class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, nullable=False)
    uptime_last_hour = Column(Float)
    uptime_last_day = Column(Float)
    uptime_last_week = Column(Float)
    downtime_last_hour = Column(Float)
    downtime_last_day = Column(Float)
    downtime_last_week = Column(Float)
    # New column for report status
    status = Column(Enum(ReportStatus, name="reportstatus"),
                    default=ReportStatus.PENDING)
