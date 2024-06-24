# This one fetches all the appointments  of the patient.

import requests

url = 'https://openmrs.cloudwise.co.ke/openmrs/ws/rest/v1/appointmentscheduling/appointment'
params = {
    'v': 'default'  
}
response = requests.get(url, auth=('Admin', 'Admin123'), params=params)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Failed to fetch data: {response.status_code}, {response.text}")
