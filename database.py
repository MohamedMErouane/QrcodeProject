import psycopg2



def create_db_connection():
    connection = psycopg2.connect(
        host="localhost",
        database="attendance_db",
        user="your_username",
        password="your_password"
    )
    return connection



# hada dyal l connection