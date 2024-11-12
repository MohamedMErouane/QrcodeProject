import psycopg2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Function to connect to the database and fetch data
def get_students_and_presence(class_id):
    try:
        # Connect to your PostgreSQL database
        conn = psycopg2.connect(
            dbname="your_db_name",
            user="your_user",
            password="your_password",
            host="your_host",
            port="your_port"
        )
        cursor = conn.cursor()
        
        # Define today's date
        today = datetime.today().date()
        
        # Query the students in the specified class
        query_students = """
        SELECT student_id, student_name
        FROM students
        WHERE class_id = %s;
        """
        cursor.execute(query_students, (class_id,))
        students = cursor.fetchall()
        
        # Query the presence data for the specific day and class
        query_presence = """
        SELECT student_id, session_time, presence_status
        FROM presence
        WHERE presence_date = %s AND class_id = %s;
        """
        cursor.execute(query_presence, (today, class_id))
        presence_data = cursor.fetchall()
        
        # Close the database connection
        cursor.close()
        conn.close()
        
        return students, presence_data
    except psycopg2.DatabaseError as e:
        print(f"Database error: {e}")
        return [], []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return [], []

# Function to format the data into a summary string
def format_presence_summary(students, presence_data):
    summary = "Presence Report for Today:\n\n"
    
    # Define the session times
    session_times = ["8:00 - 10:00", "10:00 - 12:00", "14:00 - 16:00", "16:00 - 18:00"]
    
    # Initialize a dictionary for presence tracking
    presence_dict = {student[0]: { "name": student[1], "sessions": {session: "not present" for session in session_times}} for student in students}
    
    # Update presence status for each student based on the database data
    for row in presence_data:
        student_id, session_time, presence_status = row
        if student_id in presence_dict:
            presence_dict[student_id]["sessions"][session_time] = presence_status
    
    # Add session details for each student
    for student_id, details in presence_dict.items():
        summary += f"Student: {details['name']} (ID: {student_id})\n"
        for session in session_times:
            status = details["sessions"].get(session, "not present")
            summary += f"  {session}: {status}\n"
        summary += "\n"
    
    return summary

# Function to send the email
def send_email(subject, body):
    try:
        from_address = "your_email@example.com"
        to_address = "admin@example.com"
        password = "your_email_password"
        
        # Setup the email server
        server = smtplib.SMTP("smtp.example.com", 587)
        server.starttls()
        server.login(from_address, password)
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = from_address
        msg['To'] = to_address
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send the email
        server.sendmail(from_address, to_address, msg.as_string())
        server.quit()
    except smtplib.SMTPException as e:
        print(f"Email sending error: {e}")
    except Exception as e:
        print(f"Unexpected error while sending email: {e}")

def main():
    class_id = 101  # Example class_id for the specific class you want to check
    
    # Get the students and presence data
    students, presence_data = get_students_and_presence(class_id)
    
    if students and presence_data:
        # Format the data into a summary
        summary = format_presence_summary(students, presence_data)
        
        # Send the summary via email
        subject = f"Presence Report for {datetime.today().date()}"
        send_email(subject, summary)
        print("Email sent successfully.")
    else:
        print("No data to send.")

if __name__ == "__main__":
    main()
