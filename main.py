from fastapi import FastAPI, HTTPException
import psycopg2
from typing import List
from pydantic import BaseModel
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta, date
import requests

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
BULK_KE_API_KEY = "a0ee1604c1cd462eeadb42d5d2f2051f96db54a00a3f5ce1bdb45a4d90a3eb54"
BULK_KE_SENDER_NAME = "Speed_Crash"

class Appointment(BaseModel):
    display: str
    start_date: str
    end_date: str
    telephone_number: str
    doctor_name: str
    patient_name: str

class SMSData(BaseModel):
    phoneNumber: str

def get_appointments_from_db():
    try:
        connection = psycopg2.connect(
            dbname="appointments_db",
            user="postgres",
            password="@Syanwa2000",
            host="localhost",
            port="5432"
        )
        cursor = connection.cursor()
        query = """
            SELECT display, start_date, end_date, telephone_number, doctor_name, patient_name
            FROM appointments
            WHERE DATE(end_date) = %s
        """
        cursor.execute(query, (date.today(),))
        rows = cursor.fetchall()
        appointments = []
        for row in rows:
            appointment = Appointment(
                display=row[0].split(":")[0].strip(),
                start_date=row[1].isoformat(),
                end_date=row[2].isoformat(),
                telephone_number=row[3],
                doctor_name=row[4],
                patient_name=row[5]
            )
            appointments.append(appointment)
        cursor.close()
        connection.close()
        return appointments
    except Exception as error:
        logger.error(f"Error fetching data from PostgreSQL table: {error}")
        return []

def send_sms_reminder(appointment: Appointment):
    phone_number = appointment.telephone_number
    message = f"Hello {appointment.patient_name}, You have a {appointment.display} appointment with {appointment.doctor_name} today."
    url = 'https://api.bulk.ke/sms/sendsms'
    headers = {
        'h_api_key': BULK_KE_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        "mobile": phone_number,
        "response_type": "json",
        "sender_name": BULK_KE_SENDER_NAME,
        "service_id": 0,
        "message": message
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        logger.info(f"Successfully sent SMS to {phone_number}")
    except requests.RequestException as e:
        logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")

def schedule_sms_reminders():
    appointments = get_appointments_from_db()
    for appointment in appointments:
        scheduler.add_job(send_sms_reminder, IntervalTrigger(minutes=5), args=[appointment])

@app.on_event("startup")
def startup_event():
    global scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(schedule_sms_reminders, 'interval', minutes=5)
    scheduler.start()
    logger.info("Scheduler started")

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

@app.get("/appointments", response_model=List[Appointment])
def read_appointments():
    appointments = get_appointments_from_db()
    if not appointments:
        raise HTTPException(status_code=404, detail="No appointments found or error fetching data")
    return appointments

@app.post("/get_URL_and_send_SMS")
async def get_url_and_send_SMS(sms_data: SMSData):
    # Send SMS with a predefined message to the user
    phone_number = sms_data.phoneNumber
    url = 'https://api.bulk.ke/sms/sendsms'
    headers = {
        'h_api_key': BULK_KE_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        "mobile": phone_number,
        "response_type": "json",
        "sender_name": BULK_KE_SENDER_NAME,
        "service_id": 0,
        "message": "Your predefined message goes here."
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to send SMS: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
