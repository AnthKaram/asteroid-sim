# http_gmat_bridge.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import math
import time

class PhysicsGMATHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.counter = 0
        self.simulation_active = True
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/gmat-data':
            self.send_physics_data()
        elif self.path == '/control' and 'command' in self.path:
            self.handle_control_command()
        elif self.path == '/status':
            self.send_status()
        elif self.path == '/':
            self.send_home_page()
        else:
            self.send_error(404)
    
    def handle_control_command(self):
        """Handle control commands from the web interface"""
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        command = params.get('command', [''])[0]
        
        if command == 'start':
            self.simulation_active = True
            response = {'status': 'started', 'message': 'GMAT simulation started'}
        elif command == 'stop':
            self.simulation_active = False
            response = {'status': 'stopped', 'message': 'GMAT simulation stopped'}
        elif command == 'reset':
            self.counter = 0
            response = {'status': 'reset', 'message': 'Counter reset'}
        else:
            response = {'status': 'error', 'message': 'Unknown command'}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def send_status(self):
        """Send current server status"""
        status = {
            'simulation_active': self.simulation_active,
            'counter': self.counter,
            'clients_served': self.counter,
            'server_time': time.time()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def send_physics_data(self):
        """Send orbital physics data to the JavaScript client"""
        if not self.simulation_active:
            data = {
                'simulation_active': False,
                'message': 'GMAT simulation is paused'
            }
        else:
            data = self.generate_orbital_elements()
            data['simulation_active'] = True
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def generate_orbital_elements(self):
        """Generate realistic orbital elements with proper physics"""
        self.counter += 1
        t = self.counter * 0.1
        
        # Different orbit types
        orbit_type = (self.counter // 100) % 4
        
        if orbit_type == 0:
            # Low Earth Orbit (ISS-like)
            a = 6371 + 400
            e = 0.0005
            i = 51.6
            raan = (t * 0.3) % 360
            argp = 0
            nu = (t * 4.0) % 360
            velocity = 7.66
            orbit_name = "Low Earth Orbit"
        elif orbit_type == 1:
            # Geostationary Transfer Orbit
            a = 24500
            e = 0.73
            i = 28.5
            raan = (t * 0.2) % 360
            argp = 180
            nu = (t * 1.5) % 360
            velocity = 9.9
            orbit_name = "Geostationary Transfer"
        elif orbit_type == 2:
            # Molniya Orbit
            a = 26500
            e = 0.74
            i = 63.4
            raan = (t * 0.15) % 360
            argp = 270
            nu = (t * 0.8) % 360
            velocity = 9.5
            orbit_name = "Molniya Orbit"
        else:
            # Highly Elliptical Orbit
            a = 30000
            e = 0.8
            i = 45
            raan = (t * 0.25) % 360
            argp = 90
            nu = (t * 0.6) % 360
            velocity = 8.2
            orbit_name = "Highly Elliptical"
        
        return {
            'a': a,
            'e': e,
            'i': i,
            'raan': raan,
            'argp': argp,
            'M0': nu,
            'velocity': velocity,
            'mass': 1e6,
            'orbit_type': orbit_name,
            'altitude': a - 6371,
            'period_hours': (2 * math.pi * math.sqrt(a**3 / 3.986004418e5)) / 3600,
            'counter': self.counter,
            'timestamp': time.time(),
        }
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass

def run_server():
    server_address = ('localhost', 8765)
    httpd = HTTPServer(server_address, PhysicsGMATHandler)
    print("🚀 GMAT Physics HTTP Bridge running on http://localhost:8765")
    print("📡 Connect your asteroid simulator to this bridge")
    print("⏹️  Press Ctrl+C to stop the server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

if __name__ == "__main__":
    run_server()