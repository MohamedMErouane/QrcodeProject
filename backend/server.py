import json
import uuid  # For generating unique session IDs
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from io import BytesIO
import qrcode
import psycopg2
import bcrypt

# Database connection details
DB_HOST = '127.0.0.1'
DB_PORT = '5432'
DB_NAME = 'Qrcode'
DB_USER = 'Mohamed'
DB_PASSWORD = '123'

# Session storage (for simplicity, this is in-memory; consider using a more robust solution)
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
            # Return a list of absent dates
            self._send_response(200, {"absentDates": ["2024-11-06", "2024-11-07"]})
        
        elif parsed_url.path == '/api/session-details':
            # Get session details for a specific date
            date = query_params.get('date', [None])[0]
            if date and date in session_store:
                self._send_response(200, session_store[date])
            else:
                self._send_response(404, {"error": "No session details found for this date"})

    def handle_generate_qr(self):
        """Generate a QR code for a given URL."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            login_url = data.get("login_url", "http://localhost:3000/login")

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(login_url)
            qr.make(fit=True)

            # Convert QR code to binary data
            img = qr.make_image(fill='black', back_color='white')
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()

            # Send the image as a response
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(img_bytes)

        except Exception as e:
            self._send_response(500, {'error': str(e)})

    def handle_login(self):
        """Handle user login by verifying credentials and returning session data."""
        try:
            conn = get_db_connection()
            if not conn:
                raise Exception("Database connection failed")

            cur = conn.cursor()

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                self._send_response(400, {'error': 'Username and password are required'})
                return

            # Ensure username is stripped of whitespace
            username = username.strip()
            print(f"Attempting to log in with username: {username}")

            # Query the database for user details
            query = """SELECT password, role, name FROM "User" WHERE name = %s"""
            cur.execute(query, (username,))
            result = cur.fetchone()
            print(f"Database query result: {result}")

            if result:
                stored_password, role, name = result

                # Directly compare plain-text passwords
                if password == stored_password:
                    # Create a session ID and store user data
                    session_id = str(uuid.uuid4())
                    session_store[session_id] = {'username': username, 'role': role}
                    print(f"Session created for user {username} with session_id {session_id}")
                    self._send_response(200, {'session_id': session_id, 'username': name, 'role': role})
                else:
                    print("Invalid password.")
                    self._send_response(401, {'error': 'Invalid password'})
            else:
                print("User not found.")
                self._send_response(404, {'error': 'User not found'})

            cur.close()
            conn.close()

        except Exception as e:
            print(f"Error: {e}")
            self._send_response(500, {'error': str(e)})   

    def _send_response(self, status_code, content):
        """Helper function to send JSON responses."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(content).encode())
# Server setup
def run(server_class=HTTPServer, handler_class=MyHandler, port=8080):
    """Run the HTTP server."""
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Server running on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    try:
        run(port=8080)
    except KeyboardInterrupt:
        print('\nServer stopped.')
