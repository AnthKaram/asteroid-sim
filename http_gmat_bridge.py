# http_gmat_bridge.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import math
import time

// GMAT INTEGRATION WITH ON/OFF SWITCH - CLEAN VERSION
class PhysicsGMATIntegration {
    constructor() {
        this.isConnected = false;
        this.simulationActive = false;
        this.currentData = null;
        this.pollInterval = null;
        this.baseURL = '/gmat/';
        this.manualMode = true; // Start in manual mode (GMAT OFF)
    }

    init() {
        this.addPhysicsControls();
        this.startStatusPolling();
        console.log('GMAT Physics Integration initialized - Starting in MANUAL mode');
    }

    async fetchPhysicsData() {
        if (!this.simulationActive || this.manualMode) return;
        
        try {
            const response = await fetch(`${this.baseURL}/gmat-data`);
            if (response.ok) {
                const data = await response.json();
                this.handlePhysicsData(data);
                this.isConnected = true;
            } else {
                this.isConnected = false;
            }
        } catch (error) {
            this.isConnected = false;
            this.updatePhysicsStatus('GMAT Bridge Not Running - Start Python Server');
        }
    }

    async sendControlCommand(command) {
        try {
            const response = await fetch(`${this.baseURL}/control?command=${command}`);
            if (response.ok) {
                const result = await response.json();
                return true;
            }
        } catch (error) {
            console.error('Control command failed:', error);
        }
        return false;
    }

    async checkServerStatus() {
        try {
            const response = await fetch(`${this.baseURL}/status`);
            if (response.ok) {
                const status = await response.json();
                this.isConnected = true;
                this.simulationActive = status.simulation_active;
                return status;
            }
        } catch (error) {
            this.isConnected = false;
            this.simulationActive = false;
        }
        return null;
    }

    handlePhysicsData(data) {
        this.currentData = data;
        
        if (data.simulation_active === false) {
            this.updatePhysicsStatus('GMAT Simulation Paused');
            return;
        }

        this.updateAllUIElements(data);
        this.updatePhysicsDisplay(data);
        this.updatePhysicsStatus(`LIVE: ${data.orbit_type}`);
    }

    updateAllUIElements(data) {
        if (this.manualMode) return; // Don't update UI if in manual mode

        // Update your existing UI sliders with real physics data
        if (data.a !== undefined) {
            ui.a.value = this.clamp(data.a, 7000, 60000);
        }
        
        if (data.e !== undefined) {
            ui.e.value = this.clamp(data.e, 0, 0.9);
        }
        
        if (data.i !== undefined) {
            ui.inc.value = this.clamp(data.i, 0, 90);
        }
        
        if (data.raan !== undefined) {
            ui.raan.value = data.raan % 360;
        }
        
        if (data.argp !== undefined) {
            ui.argp.value = data.argp % 360;
        }
        
        if (data.M0 !== undefined) {
            ui.M0.value = data.M0 % 360;
        }
        
        if (data.velocity !== undefined) {
            ui.velocity.value = this.clamp(data.velocity, 11, 72);
            document.getElementById('velocity-value').textContent = data.velocity.toFixed(1);
            updateVelocity(data.velocity);
        }
        
        if (data.mass !== undefined) {
            const massExp = Math.log10(data.mass);
            ui.mass.value = this.clamp(massExp, 3, 9);
            updateMassDisplay(massExp);
        }

        // Refresh orbit visualization
        refreshOrbitLine();
    }

    updatePhysicsDisplay(data) {
        const stats = document.getElementById('stats');
        if (!stats) return;

        let physicsInfo = stats.querySelector('.physics-info');
        if (!physicsInfo) {
            physicsInfo = document.createElement('div');
            physicsInfo.className = 'physics-info';
            physicsInfo.style.cssText = `
                margin-top: 10px;
                padding: 10px;
                background: #1a1a2e;
                border-radius: 8px;
                font-size: 12px;
                border-left: 4px solid #4CAF50;
                color: white;
            `;
            stats.appendChild(physicsInfo);
        }

        if (this.manualMode) {
            physicsInfo.innerHTML = `
                <div style="color: #ff9800; font-weight: bold; margin-bottom: 8px;">
                    ⚙️ MANUAL MODE
                </div>
                <div style="font-size: 11px; color: #ccc;">
                    Using manual controls - GMAT integration is OFF
                </div>
            `;
            return;
        }

        if (!this.simulationActive) {
            physicsInfo.innerHTML = `
                <div style="color: #ff9800; font-weight: bold; margin-bottom: 8px;">
                    ⏸️ GMAT PAUSED
                </div>
                <div style="font-size: 11px; color: #ccc;">
                    GMAT simulation is stopped
                </div>
            `;
            return;
        }

        physicsInfo.innerHTML = `
            <div style="color: #4CAF50; font-weight: bold; margin-bottom: 8px;">
                🛰️ GMAT PHYSICS ACTIVE
            </div>
            <div style="margin-bottom: 4px;">
                <strong>Orbit:</strong> ${data.orbit_type || 'Calculated'}
            </div>
            <div style="margin-bottom: 4px;">
                <strong>Altitude:</strong> ${(data.altitude || 0).toFixed(0)} km
            </div>
            <div style="margin-bottom: 4px;">
                <strong>Period:</strong> ${(data.period_hours || 0).toFixed(1)} hours
            </div>
            <div style="font-size: 10px; color: #888; margin-top: 6px;">
                Real Orbital Mechanics from GMAT Physics
            </div>
        `;
    }

    updatePhysicsStatus(message) {
        const statusElement = document.getElementById('physicsStatus');
        if (statusElement) {
            statusElement.innerHTML = message;
            
            if (message.includes('MANUAL') || message.includes('OFF')) {
                statusElement.style.background = '#ff9800';
            } else if (message.includes('LIVE')) {
                statusElement.style.background = '#4CAF50';
            } else if (message.includes('Not Running')) {
                statusElement.style.background = '#f44336';
            } else {
                statusElement.style.background = '#2196F3';
            }
        }
    }

    startStatusPolling() {
        // Poll for server status every 3 seconds
        this.pollInterval = setInterval(async () => {
            await this.checkServerStatus();
            this.updateControlButtons();
            
            if (this.simulationActive && !this.manualMode) {
                await this.fetchPhysicsData();
            }
        }, 3000);
    }

    toggleGMATIntegration() {
        this.manualMode = !this.manualMode;
        
        if (this.manualMode) {
            // Switching to MANUAL mode
            this.updatePhysicsStatus('MANUAL MODE - GMAT OFF');
        } else {
            // Switching to GMAT mode
            this.updatePhysicsStatus('GMAT MODE - Connecting...');
            this.fetchPhysicsData();
        }
        
        this.updateControlButtons();
        this.updatePhysicsDisplay(this.currentData);
    }

    async startGMATSimulation() {
        const success = await this.sendControlCommand('start');
        if (success) {
            this.simulationActive = true;
            this.updatePhysicsStatus('GMAT Simulation Started');
        }
        this.updateControlButtons();
    }

    async stopGMATSimulation() {
        const success = await this.sendControlCommand('stop');
        if (success) {
            this.simulationActive = false;
            this.updatePhysicsStatus('GMAT Simulation Stopped');
        }
        this.updateControlButtons();
    }

    updateControlButtons() {
        const toggleBtn = document.getElementById('toggleGMAT');
        const startBtn = document.getElementById('startGMAT');
        const stopBtn = document.getElementById('stopGMAT');
        
        if (toggleBtn) {
            if (this.manualMode) {
                toggleBtn.innerHTML = '🔴 GMAT OFF &nbsp; | &nbsp; Switch to GMAT Mode';
                toggleBtn.style.background = '#f44336';
            } else {
                toggleBtn.innerHTML = '🟢 GMAT ON &nbsp; | &nbsp; Switch to Manual Mode';
                toggleBtn.style.background = '#4CAF50';
            }
        }
        
        if (startBtn) {
            startBtn.disabled = !this.isConnected || this.simulationActive;
            startBtn.style.opacity = startBtn.disabled ? '0.5' : '1';
        }
        
        if (stopBtn) {
            stopBtn.disabled = !this.isConnected || !this.simulationActive;
            stopBtn.style.opacity = stopBtn.disabled ? '0.5' : '1';
        }
    }

    clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    addPhysicsControls() {
        const physicsDiv = document.createElement('div');
        physicsDiv.className = 'physics-controls';
        physicsDiv.innerHTML = `
            <div style="
                font-weight: 600; 
                margin-bottom: 12px; 
                margin-top: 20px; 
                border-top: 2px solid #4CAF50; 
                padding-top: 12px;
                color: #4CAF50;
                font-size: 14px;
            ">
                🚀 GMAT PHYSICS INTEGRATION
            </div>
            
            <!-- On/Off Toggle Switch -->
            <div style="margin-bottom: 12px;">
                <button id="toggleGMAT" style="
                    width: 100%;
                    padding: 12px;
                    background: #f44336;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: bold;
                    font-size: 13px;
                    margin-bottom: 8px;
                ">
                    🔴 GMAT OFF | Switch to GMAT Mode
                </button>
            </div>
            
            <!-- Control Buttons -->
            <div style="display: flex; gap: 5px; margin-bottom: 8px;">
                <button id="startGMAT" style="
                    flex: 1;
                    padding: 8px 8px;
                    background: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 11px;
                ">
                    Start Sim
                </button>
                <button id="stopGMAT" style="
                    flex: 1;
                    padding: 8px 8px;
                    background: #ff9800;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 11px;
                ">
                    Stop Sim
                </button>
                <button id="exportGMAT" style="
                    flex: 1;
                    padding: 8px 8px;
                    background: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 11px;
                ">
                    Export
                </button>
            </div>
            
            <!-- Status Display -->
            <div id="physicsStatus" style="
                font-size: 11px; 
                padding: 8px; 
                background: #5a2d2d; 
                color: white; 
                border-radius: 4px; 
                text-align: center;
            ">
                Status: Initializing...
            </div>
        `;
        
        // Add to your existing UI container
        const uiContainer = document.getElementById('ui');
        if (uiContainer) {
            uiContainer.appendChild(physicsDiv);
        }
        
        // Add event listeners
        document.getElementById('toggleGMAT').addEventListener('click', () => {
            this.toggleGMATIntegration();
        });
        
        document.getElementById('startGMAT').addEventListener('click', () => {
            this.startGMATSimulation();
        });
        
        document.getElementById('stopGMAT').addEventListener('click', () => {
            this.stopGMATSimulation();
        });
        
        document.getElementById('exportGMAT').addEventListener('click', () => {
            this.exportToGMAT();
        });
        
        // Initialize button states
        this.updateControlButtons();
    }

    exportToGMAT() {
        const elements = getElements();
        const gmatScript = this.generateGMATScript(elements);
        
        const blob = new Blob([gmatScript], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'asteroid_mission_gmat.script';
        a.click();
        URL.revokeObjectURL(url);
        
        this.updatePhysicsStatus('GMAT Script Exported!');
    }

    generateGMATScript(elements) {
        return `
Create Spacecraft Asteroid;
Asteroid.Epoch = '01 Jan 2025 00:00:00.000';
Asteroid.CoordinateSystem = EarthMJ2000Eq;

% Orbital elements from Asteroid Simulator
Asteroid.SMA = ${elements.a};
Asteroid.ECC = ${elements.e};
Asteroid.INC = ${elements.i};
Asteroid.RAAN = ${elements.raan};
Asteroid.AOP = ${elements.argp};
Asteroid.TA = ${elements.M0};

Create Propagator Prop;
Prop.FM = RungeKutta89;
Prop.InitialStepSize = 60;
Prop.Accuracy = 1e-12;

Create ForceModel FM;
FM.CentralBody = Earth;
FM.PointMasses = {Earth, Sun, Moon};

Create ReportFile Reporter;
Reporter.Filename = 'AsteroidTrajectory.txt';
Reporter.Add = {Asteroid.EarthMJ2000Eq.X, Asteroid.EarthMJ2000Eq.Y, Asteroid.EarthMJ2000Eq.Z,
                Asteroid.EarthMJ2000Eq.VX, Asteroid.EarthMJ2000Eq.VY, Asteroid.EarthMJ2000Eq.VZ};

BeginMissionSequence;
Propagate Prop(Asteroid) {Asteroid.ElapsedDays = 365};
        `.trim();
    }
}

// Initialize the physics integration
let physicsIntegration;

// Add this to your existing DOMContentLoaded event
document.addEventListener('DOMContentLoaded', () => {
    // Your existing initialization code...
    
    // Initialize physics integration after a short delay
    setTimeout(() => {
        physicsIntegration = new PhysicsGMATIntegration();
        physicsIntegration.init();
    }, 1000);
});
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