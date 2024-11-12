import json
from http.server import BaseHTTPRequestHandler, HTTPServer #bach kat processi requests li ghadi i jiw mora ma ghadi i scanni l qr o yji lk l page d login
from QrcodeProject.auth import verify_password, generate_jwt
from QrcodeProject.database import get_db_connection


class RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        # Handle login requests
        if self.path == '/login':
            self.handle_login()

    def handle_login(self):
        # Get the request body containing login credentials
        content_length = int(self.headers['Content-Length'])  # Get the size of the request body
        body = self.rfile.read(content_length).decode('utf-8')  # Read the body data
        data = json.loads(body)  # Parse the JSON data from the request

        email = data.get('email')  # Extract email from request
        password = data.get('password')  # Extract password from request

        # Connect to the PostgreSQL database to check the user credentials
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))# hna f blast l mail khask tdir dek l uniq li ghadi traverser bih les tables 
        user = cursor.fetchone()  # Fetch the first matching user

        if user and verify_password(user[2], password):  # Verify the password
            # Generate a JWT token for the user
            token = generate_jwt(user[0], user[1])  # user[0] is ID, user[1] is email
            self.send_response(200)  # Send HTTP 200 status (OK)
            self.send_header('Content-Type', 'application/json')  # Set response type as JSON
            self.end_headers()
            # Send the success message and the token
            self.wfile.write(json.dumps({'message': 'Login successful', 'token': token}).encode('utf-8'))
        else:
            # If credentials are incorrect, respond with a 401 status (Unauthorized)
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'message': 'Invalid credentials'}).encode('utf-8'))

def run():
    # Start the HTTP server on port 8080
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Running server...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
