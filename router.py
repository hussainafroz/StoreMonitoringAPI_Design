

from io import StringIO
import os
import uuid
from fastapi.responses import FileResponse
import pandas as pd
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from config import SessionLocal
from sqlalchemy.orm import Session
from models import Report, ReportStatus, StoreBusinessHours, StoreStatusLog, StoreTimeZone
from schemas import ReportBase, StoreBusinessHoursCreate, StoreStatusLogCreate, StoreTimeZoneCreate
import helper


# Routes
store_router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# upload the datasets into the datbase


@store_router.post("/upload/store_status")
async def upload_store_status(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_csv(file.file)
    for index, row in df.iterrows():
        store_status = StoreStatusLogCreate(
            store_id=row['store_id'],
            timestamp_utc=row['timestamp_utc'],
            status=row['status']
        )
        helper.create_store_status(db, store_status)
    return {"message": "Store status uploaded successfully"}


@store_router.post("/upload/business_hours")
async def upload_business_hours(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_csv(file.file)
    for index, row in df.iterrows():
        business_hours = StoreBusinessHoursCreate(
            store_id=row['store_id'],
            day_of_week=row['day_of_week'],
            start_time_local=row['start_time_local'],
            end_time_local=row['end_time_local']
        )
        helper.create_business_hours(db, business_hours)
    return {"message": "Store business uploaded successfully"}


@store_router.post("/upload/store_timezone")
async def upload_store_timezone(file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_csv(file.file)
    for index, row in df.iterrows():
        store_timezone = StoreTimeZoneCreate(
            store_id=row['store_id'],
            timezone_str=row['timezone_str']
        )
        helper.create_store_timezone(db, store_timezone)
    return {"message": "Store timezone uploaded successfully"}


# The two API requirements

@store_router.post("/trigger_report")
async def trigger_report(background_task: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        new_report = ReportBase(
            store_id=None,
            uptime_last_hour=0.0,
            uptime_last_day=0.0,
            uptime_last_week=0.0,
            downtime_last_hour=0.0,
            downtime_last_day=0.0,
            downtime_last_week=0.0,
            status="RUNNING",
        )
        new_report = new_report.model_dump()
        new_report = Report(**new_report)
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        # generate the report and update its status
        background_task.add_task(
            helper.compute_uptime_downtime, db, new_report.id)

        return {"report_id": new_report.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@store_router.get("/get_report/{id}")
async def get_report(id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == id).first()
    if report:
        if report.status == ReportStatus.COMPLETE:
            # Prepare the CSV data
            csv_data = {
                "store_id": [report.store_id],
                "uptime_last_hour (minutes)": [report.uptime_last_hour],
                "uptime_last_day (hours)": [report.uptime_last_day],
                "uptime_last_week (hours)": [report.uptime_last_week],
                "downtime_last_hour (minutes)": [report.downtime_last_hour],
                "downtime_last_day (hours)": [report.downtime_last_day],
                "downtime_last_week (hours)": [report.downtime_last_week]
            }

            df = pd.DataFrame(csv_data)

            # Create a CSV file in memory
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)

            # Return the CSV file as a response
            return FileResponse(
                csv_buffer,
                media_type='text/csv',
                headers={
                    "Content-Disposition": f"attachment; filename=report_{id}.csv"}
            )
        else:
            return {
                "status": report.status.value,
                "report_content": None
            }
    else:
        raise HTTPException(status_code=404, detail="Report not found")
