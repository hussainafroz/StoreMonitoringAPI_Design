from datetime import time, timedelta, datetime
import os
import uuid
import pandas as pd
import pytz
from sqlalchemy import and_
from sqlalchemy.orm import Session
from models import Report, StoreBusinessHours, StoreStatus, StoreStatusLog, StoreTimeZone, ReportStatus
from schemas import StoreBusinessHoursCreate, StoreStatusLogCreate, StoreTimeZoneCreate

# create or update store status


def create_store_status(db: Session, status: StoreStatusLogCreate):
    _storestatus = StoreStatusLog(
        store_id=status.store_id, timestamp_utc=status.timestamp_utc, status=status.status
    )
    db.add(_storestatus)
    db.commit()
    db.refresh(_storestatus)
    return _storestatus

# create or update business hours


def create_business_hours(db: Session, hours: StoreBusinessHoursCreate):
    _storetime = StoreBusinessHours(
        store_id=hours.store_id,
        day_of_week=hours.day_of_week,
        start_time_local=hours.start_time_local,
        end_time_local=hours.end_time_local,
    )
    db.add(_storetime)
    db.commit()
    db.refresh(_storetime)
    return _storetime

# create or update store timezone


def create_store_timezone(db: Session, timezone: StoreTimeZoneCreate):
    _storetzone = StoreTimeZone(
        store_id=timezone.store_id,
        timezone_str=timezone.timezone_str,
    )
    db.add(_storetzone)
    db.commit()
    db.refresh(_storetzone)
    return _storetzone

# uptime_downtime_calculation

# Function to generate and save CSV file


def generate_csv_file(report_id, csv_data):
    filename = f"{uuid.uuid4()}.csv"
    filepath = os.path.join('reports', filename)

    df = pd.DataFrame(csv_data)
    df.to_csv(filepath, index=False)

    return filepath

# Uptime and downtime calculation


def calculate_uptime_downtime(db: Session, store_id: int, start_time: datetime, end_time: datetime):
    statuses = db.query(StoreStatusLog).filter(
        and_(
            StoreStatusLog.store_id == store_id,
            StoreStatusLog.timestamp_utc >= start_time,
            StoreStatusLog.timestamp_utc <= end_time
        )
    ).all()

    uptime = downtime = 0
    last_timestamp = start_time

    for status in statuses:
        interval = (status.timestamp_utc - last_timestamp).total_seconds()
        if status.status == 'active':
            uptime += interval
        else:
            downtime += interval
        last_timestamp = status.timestamp_utc

    # Include the interval from the last recorded status to the end time
    interval = (end_time - last_timestamp).total_seconds()
    if last_timestamp < end_time:
        if statuses and statuses[-1].status == 'active':
            uptime += interval
        else:
            downtime += interval

    return uptime / 60, downtime / 60  # Convert seconds to minutes

# Function to compute uptime and downtime, generate report, and save as CSV


def compute_uptime_downtime(db: Session):
    store_ids = db.query(StoreStatusLog.store_id).distinct().all()
    store_ids = [store_id[0] for store_id in store_ids]

    now = datetime.now().replace(tzinfo=pytz.utc)
    last_hour = now - timedelta(hours=1)
    last_day = now - timedelta(days=1)
    last_week = now - timedelta(days=7)

    for store_id in store_ids:
        business_hours = db.query(StoreBusinessHours).filter_by(
            store_id=store_id).all()
        timezone_str = db.query(StoreTimeZone).filter_by(
            store_id=store_id).first().timezone_str

        if not business_hours:
            business_hours = [
                {"start_time_local": time.min, "end_time_local": time.max}
            ]
        else:
            business_hours = [
                {
                    "start_time_local": bh.start_time_local,
                    "end_time_local": bh.end_time_local
                } for bh in business_hours
            ]

        store_tz = pytz.timezone(timezone_str)

        def adjust_to_timezone(dt):
            return store_tz.localize(dt)

        def get_business_hours(start_time, end_time):
            business_hours_today = []
            for bh in business_hours:
                bh_start = datetime.combine(
                    start_time.date(), bh['start_time_local'])
                bh_end = datetime.combine(
                    start_time.date(), bh['end_time_local'])
                bh_start = adjust_to_timezone(bh_start)
                bh_end = adjust_to_timezone(bh_end)

                if start_time <= bh_end and end_time >= bh_start:
                    business_hours_today.append(
                        (max(start_time, bh_start), min(end_time, bh_end)))
            return business_hours_today

        def calculate_period_uptime_downtime(start_time, end_time):
            uptime = downtime = 0
            for business_hours in get_business_hours(start_time, end_time):
                bh_start, bh_end = business_hours
                uptime_period, downtime_period = calculate_uptime_downtime(
                    db, store_id, bh_start, bh_end)
                uptime += uptime_period
                downtime += downtime_period
            return uptime, downtime

        uptime_last_hour, downtime_last_hour = calculate_period_uptime_downtime(
            last_hour, now)
        uptime_last_day, downtime_last_day = calculate_period_uptime_downtime(
            last_day, now)
        uptime_last_week, downtime_last_week = calculate_period_uptime_downtime(
            last_week, now)

        # Save the report to the database with status PENDING
        report = Report(
            store_id=store_id,
            uptime_last_hour=uptime_last_hour,
            uptime_last_day=uptime_last_day / 60,  # Convert to hours
            uptime_last_week=uptime_last_week / 60,  # Convert to hours
            downtime_last_hour=downtime_last_hour,
            downtime_last_day=downtime_last_day / 60,  # Convert to hours
            downtime_last_week=downtime_last_week / 60,  # Convert to hours
            status='PENDING'
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        # Generate CSV file
        csv_data = [
            {
                "store_id": store_id,
                "uptime_last_hour": uptime_last_hour,
                "uptime_last_day": uptime_last_day / 60,
                "uptime_last_week": uptime_last_week / 60,
                "downtime_last_hour": downtime_last_hour,
                "downtime_last_day": downtime_last_day / 60,
                "downtime_last_week": downtime_last_week / 60,
            }
        ]

        # Generate CSV file
        report_file_path = generate_csv_file(report.id, csv_data)

        # Update report with COMPLETED status
        report.status = 'COMPLETED'
        db.commit()
        db.refresh(report)

    return report.id
