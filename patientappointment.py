import requests
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# URL to fetch appointments
url = os.getenv('API_URL')

# API authentication
auth = (os.getenv('API_USERNAME'), os.getenv('API_PASSWORD'))

# Query parameters
params = {
    'v': 'default'  # Version of the API
}

# Make the GET request
response = requests.get(url, auth=auth, params=params)

# Check the response status
if response.status_code == 200:
    appointments = response.json().get('results', [])
    
    # Filtered appointments list
    filtered_appointments = []
    
    for appointment in appointments:
        # Extract telephone number and replace leading '0' with '254'
        telephone_number = next(
            (attr['display'].split(" = ")[1] for attr in appointment['patient']['person'].get('attributes', [])
             if attr['display'].startswith("Telephone Number")), None
        )
        if telephone_number and telephone_number.startswith('0'):
            telephone_number = '254' + telephone_number[1:]
        
        filtered_appointment = {
            'uuid': appointment.get('uuid'),
            'display': appointment.get('display'),
            'startDate': appointment['timeSlot'].get('startDate') if 'timeSlot' in appointment else None,
            'endDate': appointment['timeSlot'].get('endDate') if 'timeSlot' in appointment else None,
            'telephoneNumber': telephone_number,
            'doctorName': appointment['timeSlot']['appointmentBlock']['provider']['person'].get('display') if 'timeSlot' in appointment and 'appointmentBlock' in appointment['timeSlot'] and 'provider' in appointment['timeSlot']['appointmentBlock'] else None,
            'patientName': appointment['patient']['person'].get('display') if 'patient' in appointment and 'person' in appointment['patient'] else None
        }
        filtered_appointments.append(filtered_appointment)
    
    # Print the filtered appointments
    print(filtered_appointments)
    
    # Database connection details
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    
    # Create a cursor object
    cur = conn.cursor()
    
    # Insert or update the data in the table
    insert_query = sql.SQL("""
        INSERT INTO appointments (uuid, display, start_date, end_date, telephone_number, doctor_name, patient_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (uuid) DO UPDATE SET
            display = EXCLUDED.display,
            start_date = EXCLUDED.start_date,
            end_date = EXCLUDED.end_date,
            telephone_number = EXCLUDED.telephone_number,
            doctor_name = EXCLUDED.doctor_name,
            patient_name = EXCLUDED.patient_name;
    """)
    
    for appointment in filtered_appointments:
        cur.execute(insert_query, (
            appointment['uuid'],
            appointment['display'],
            appointment['startDate'],
            appointment['endDate'],
            appointment['telephoneNumber'],
            appointment['doctorName'],
            appointment['patientName']
        ))
    
    # Commit the transaction
    conn.commit()
    
    # Close the cursor and connection
    cur.close()
    conn.close()
else:
    print(f"Failed to fetch data: {response.status_code}, {response.text}")
