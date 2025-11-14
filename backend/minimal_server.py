"""
Serveur HTTP ultra-minimal - Démarre en < 1 seconde
Utilisez ce serveur pour tester si Railway peut démarrer Python
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "service": "Minimal Python Server"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Server is running!')

    def log_message(self, format, *args):
        """Override to print logs"""
        print(f"[{self.log_date_time_string()}] {format % args}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"🚀 Ultra-minimal server starting on port {port}...")
    print(f"✅ Server ready! Health endpoint: http://0.0.0.0:{port}/health")
    server.serve_forever()
