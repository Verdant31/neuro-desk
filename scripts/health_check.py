import threading
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

health_status = {
    "status": "offline",
    "message": "OS Assistant not started",
    "timestamp": str(int(datetime.now().timestamp()))
}


def update_health_status(status, message=""):
    """Update global health status for HTTP endpoint"""
    global health_status
    health_status = {
        "status": status,
        "message": message,
        "timestamp": str(int(datetime.now().timestamp()))
    }


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()

            response = json.dumps(health_status)
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def start_health_server():
    """Start HTTP server for health checks"""
    try:
        server = HTTPServer(('127.0.0.1', 5002), HealthCheckHandler)
        server_thread = threading.Thread(
            target=server.serve_forever, daemon=True)
        server_thread.start()
        return server
    except:
        return None
