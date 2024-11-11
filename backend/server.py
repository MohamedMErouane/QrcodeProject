import json
import uuid  # For generating unique session IDs
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from io import BytesIO
import qrcode
import psycopg2

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
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"absentDates": ["2024-11-06", "2024-11-07"]}).encode())
        
        elif parsed_url.path == '/api/session-details':
            # Get session details for a specific date
            date = query_params.get('date', [None])[0]
            if date and date in sessions:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(sessions[date]).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No session details found for this date"}).encode())

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
            # Handle errors
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

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
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Username and password are required'}).encode())
                return

            # Query the database for user details
            cur.execute("SELECT password, role, name FROM users WHERE username = %s", (username,))
            result = cur.fetchone()

            if result:
                stored_password, role, name = result

                # Verify the password (simple comparison; use bcrypt for better security)
                if password == stored_password:
                    # Create a session ID and store user data
                    session_id = str(uuid.uuid4())
                    session_store[session_id] = {'username': username, 'role': role, 'name': name}

                    # Send response with user details and session ID
                    response = {
                        'session_id': session_id,
                        'role': role,
                        'name': name,
                    }

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Invalid credentials'}).encode())
            else:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid credentials'}).encode())

        except Exception as e:
            # Handle errors
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
        finally:
            if conn:
                cur.close()
                conn.close()

    def get_session_user(self, session_id):
        """Get user data from the session store."""
        return session_store.get(session_id)

# Run the server
def run(server_class=HTTPServer, handler_class=MyHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Server running on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
