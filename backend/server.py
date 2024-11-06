import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import qrcode
from io import BytesIO

# Simulated user database (for testing purposes)
users_db = {
    'professor': {'password': 'password123', 'id': 1, 'name': 'Professor John', 'role': 1},  # Professor
    'student': {'password': 'password123', 'id': 2, 'name': 'Student Jane', 'role': 0},    # Student
}

class MyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Handle pre-flight CORS requests (sent by the browser)
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/generate-qr':
            # Handle QR code generation
            self.handle_generate_qr()
        
        elif self.path == '/login':
            # Handle login
            self.handle_login()

    def handle_generate_qr(self):
        """ Generate the QR code for login page """
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            login_url = data.get("login_url", "http://localhost:3000/login")  # Default to localhost login

            # Create the QR code from the login URL
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(login_url)
            qr.make(fit=True)

            # Generate the image of the QR code
            img = qr.make_image(fill='black', back_color='white')

            # Convert image to binary data (PNG format)
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()

            # Send the image back as a response with proper content type
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(img_bytes)

        except Exception as e:
            # If something goes wrong, return an error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def handle_login(self):
        """ Handle user login by verifying credentials """
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
                self.send_response(401)  # Unauthorized
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid credentials'}).encode())

        except Exception as e:
            # If there's an error, send a failure response
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid request'}).encode())

# Start the HTTP server
def run(server_class=HTTPServer, handler_class=MyHandler):
    server_address = ('', 8080)  # Run the server on localhost:8080
    httpd = server_class(server_address, handler_class)
    print('Starting server at http://localhost:8080...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
