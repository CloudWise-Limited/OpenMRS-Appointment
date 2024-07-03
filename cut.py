from fastapi import FastAPI, HTTPException
import psycopg2
from typing import List
from pydantic import BaseModel
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Appointment(BaseModel):
    display: str
    start_date: str
    end_date: str
    telephone_number: str
    doctor_name: str
    patient_name: str

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
        """
        cursor.execute(query)
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

@app.get("/appointments", response_model=List[Appointment])
def read_appointments():
    appointments = get_appointments_from_db()
    if not appointments:
        raise HTTPException(status_code=404, detail="No appointments found or error fetching data")
    return appointments

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
