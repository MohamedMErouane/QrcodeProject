import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from io import BytesIO
import qrcode

# Simulated user database (for testing purposes)
users_db = {
    'professor': {'password': 'password123', 'id': 1, 'name': 'Professor John', 'role': 1},
    'student': {'password': 'password123', 'id': 2, 'name': 'Student Jane', 'role': 0},
}

# Mock session data
sessions = {
    "2024-11-06": {"session": "Session details for 2024-11-06", "professor": "Professor John"},
    "2024-11-07": {"session": "Session details for 2024-11-07", "professor": "Professor Doe"},
}

# Mock absent dates for students
absent_dates = ["2024-11-06", "2024-11-07"]

class MyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle pre-flight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        if parsed_url.path == '/api/absent-dates':
            # Return the list of absent dates
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"absentDates": absent_dates}).encode())
        
        elif parsed_url.path == '/api/session-details':
            # Get the session details for a specific date
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

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/generate-qr':
            self.handle_generate_qr()
        elif self.path == '/login':
            self.handle_login()

    def handle_generate_qr(self):
        """Generate the QR code for the login page"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            login_url = data.get("login_url", "http://localhost:3000/login")

            # Create the QR code
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

            # Send the image as response
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
        """Handle user login by verifying credentials"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            username = data.get("username")
            password = data.get("password")

            if username in users_db and users_db[username]['password'] == password:
                user = users_db[username]
                response = {
                    'id': user['id'],
                    'name': user['name'],
                    'role': user['role'],
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

        except Exception as e:
            # Handle errors
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid request'}).encode())

# Start the HTTP server
def run(server_class=HTTPServer, handler_class=MyHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
