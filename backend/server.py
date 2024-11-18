import json
import uuid  # For generating unique session IDs
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from io import BytesIO
import qrcode
import psycopg2
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Database connection details
DB_HOST = '127.0.0.1'
DB_PORT = '5432'
DB_NAME = 'Qrcode'
DB_USER = 'Mohamed'
DB_PASSWORD = '123'

# Session storage (in-memory)
session_store = {}

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


def send_absent_notification(absentees):
    """Send an email to notify about the absence."""
    try:
        # Sender and receiver details
        sender_email = "merouanemohamed495@gmail.com"
        receiver_email = "jackdoeno@gmail.com"
        password = "egyv bnjp nnzb vfkn"  # Ensure this is a valid app password
        
        # Email subject and body
        subject = "Absence Notification"
        body = "The following students were marked as absent:\n\n" + "\n".join(absentees)

        # Create the email content
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.set_debuglevel(1)  # Enables debug output to check SMTP session
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        print("Absence notification sent successfully.")
    except smtplib.SMTPAuthenticationError as e:
        print("SMTP Authentication Error: Please check the app password and account settings.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"Error sending email: {e}")



class MyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle pre-flight CORS requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/login':
            self.handle_login()
        elif self.path == '/generate-qr':
            self.handle_generate_qr()

    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        if parsed_url.path == '/api/absent-dates':
            self._send_response(200, {"absentDates": ["2024-11-06", "2024-11-07"]})
        elif parsed_url.path == '/api/session-details':
            date = query_params.get('date', [None])[0]
            if date and date in session_store:
                self._send_response(200, session_store[date])
            else:
                self._send_response(404, {"error": "No session details found for this date"})

    def handle_generate_qr(self):
        """Generate a QR code for a session."""
        try:
            conn = get_db_connection()
            if not conn:
                raise Exception("Database connection failed")
            
            with conn.cursor() as cur:
                # Read and parse the POST data
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)

                session_name = data.get("session_name")
                session_date = data.get("session_date")
                session_time = data.get("session_time")
                login_url = data.get("login_url", "http://localhost:3000/login")

                if not session_name or not session_date or not session_time:
                    self._send_response(400, {'error': 'Session name, date, and time are required'})
                    return

                # Reformat the date and time to match PostgreSQL's expected format
                try:
                    datetime_obj = datetime.strptime(f"{session_date} {session_time}", "%d/%m/%Y %H:%M:%S")
                    formatted_date_time = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    self._send_response(400, {'error': 'Invalid date or time format'})
                    return

                # Insert session data into the database
                insert_query = """
                INSERT INTO "Session" ("sessionDate", "topic")
                VALUES (%s, %s)
                RETURNING id;
                """
                cur.execute(insert_query, (formatted_date_time, session_name))
                session_id = cur.fetchone()[0]
                conn.commit()

                # Generate QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(login_url)
                qr.make(fit=True)
                img = qr.make_image(fill='black', back_color='white')

                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_bytes = buffered.getvalue()

                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(img_bytes)

            # Start a timer for 1 minute to check for absences and expire the QR code
            threading.Timer(60, self.expire_qr_and_check_absentees, [session_id]).start()

        except Exception as e:
            self._send_response(500, {'error': str(e)})

    def expire_qr_and_check_absentees(self, session_id):
        """Expire the QR code and check for absent students."""
        try:
            conn = get_db_connection()
            if not conn:
                raise Exception("Database connection failed")
            
            with conn.cursor() as cur:
                absent_query = """
                    SELECT name
                    FROM "User"
                    WHERE id NOT IN (
                        SELECT "userId"
                        FROM "Attendance"
                        WHERE "sessionId" = %s
                        );
                    """
                cur.execute(absent_query, (session_id,))
                absentees = [row[0] for row in cur.fetchall()]

                if absentees:
                    send_absent_notification(absentees)
                    print(f"Absent users: {', '.join(absentees)}")
                else:
                    print("No absentees found.")

                conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error checking absentees: {e}")
            if conn:
                conn.close()

    def handle_login(self):
        """Handle user login and update attendance."""
        try:
            conn = get_db_connection()
            if not conn:
                raise Exception("Database connection failed")
            
            with conn.cursor() as cur:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)

                username = data.get("username")
                password = data.get("password")

                if not username or not password:
                    self._send_response(400, {'error': 'Username and password are required'})
                    return

                username = username.strip()
                query = """SELECT id, password, role, name FROM "User" WHERE name = %s"""
                cur.execute(query, (username,))
                result = cur.fetchone()

                if result:
                    user_id, stored_password, role, name = result

                    # For simplicity, comparing plain-text passwords
                    if password == stored_password:
                        session_id = str(uuid.uuid4())
                        session_store[session_id] = {'username': username, 'role': role}
                        session_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
                        session_date=datetime(2024, 11, 18, 22, 0, 0, 0)
                        
                        # Query the database for a session that matches the current date
                        session_query = """SELECT id FROM "Session" WHERE "sessionDate" = %s"""
                        cur.execute(session_query, (session_date,))
                        session_result = cur.fetchone()
                        print("hadi hiya result",session_result)

                        if session_result:
                            session_id = session_result[0]
                            attendance_query = """
                            INSERT INTO "Attendance" ("status", "userId", "sessionId")
                            VALUES (TRUE, %s, %s)
                            ON CONFLICT ("userId", "sessionId") DO UPDATE SET status = TRUE;
                            """
                            cur.execute(attendance_query, (user_id, session_id))
                            conn.commit()

                        self._send_response(200, {'session_id': session_id, 'username': name, 'role': role})
                        print(session_id, session_result)
                    else:
                        self._send_response(401, {'error': 'Invalid password'})
                else:
                    self._send_response(404, {'error': 'User not found'})

            conn.close()

        except Exception as e:
            self._send_response(500, {'error': str(e)})

    def _send_response(self, status_code, content):
        """Helper function to send JSON responses."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(content).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=MyHandler, port=8080):
    """Run the server."""
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Server running on port {port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
