import psycopg2

def test_db_connection():
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
            SELECT display,start_date,end_date, telephone_number, doctor_name, patient_name
            FROM appointments
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        cursor.close()
        connection.close()
    except Exception as error:
        print(f"Error fetching data from PostgreSQL table: {error}")

if __name__ == "__main__":
    test_db_connection()
