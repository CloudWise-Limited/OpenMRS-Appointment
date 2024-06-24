# Pipenv install && pipenvshell
# run python excel.py


import pandas as pd


appointment_data = [
    {
        "uuid": "f0ea1658-def2-4445-bae7-ffbc1cc1620d",
        "display": "[Provider: providerId:4 providerName:[Jake Smith] ], Outpatient Clinic: 2024-06-25 08:00:00.0 - 2024-06-25 11:00:00.0",
        "startDate": "2024-06-25T08:00:00.000+0000",
        "endDate": "2024-06-25T11:00:00.000+0000",
        "provider": {
            "uuid": "f53983d8-757f-404a-8fe3-6b2b1eb8c628",
            "display": "doctor - Jake Smith",
            "person": {
                "uuid": "af7c3340-0503-11e3-8ffd-0800200c9a66",
                "display": "Jake Smith",
            },
            "identifier": "doctor"
        },
        "location": {
            "uuid": "58c57d25-8d39-41ab-8422-108a0c277d98",
            "display": "Outpatient Clinic"
        },
        "types": [
            {"uuid": "7dd9ac8e-c436-11e4-a470-82b0ea87e2d8", "display": "General Medicine"}
        ]
    }
    
]

# Transform the data into a pandas DataFrame

appointments = []
for appointment in appointment_data:
    appointments.append({
        "Appointment ID": appointment["uuid"],
        "Provider": appointment["provider"]["display"],
        "Provider ID": appointment["provider"]["uuid"],
        "Location": appointment["location"]["display"],
        "Start Date": appointment["startDate"],
        "End Date": appointment["endDate"],
        "Appointment Types": ", ".join([atype["display"] for atype in appointment["types"]])
    })

df = pd.DataFrame(appointments)

# Export the DataFrame to Excel
df.to_excel("appointments.xlsx", index=False)

print("Appointments exported to appointments.xlsx")
