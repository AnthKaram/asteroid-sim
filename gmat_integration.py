# gmat_integration.py
import json
import math
import asyncio
import websockets
import threading
import time

class GMATIntegration:
    def __init__(self):
        self.connected_clients = set()
        self.server = None
        self.loop = None
        
    def cross_product(self, a, b):
        """Calculate cross product of two 3D vectors"""
        return [
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]
        ]
    
    def dot_product(self, a, b):
        """Calculate dot product of two vectors"""
        return sum(a[i] * b[i] for i in range(len(a)))
    
    def vector_norm(self, v):
        """Calculate magnitude of a vector"""
        return math.sqrt(sum(x*x for x in v))
    
    def gmat_to_orbital_elements(self, gmat_data):
        """
        Convert GMAT Cartesian coordinates to Keplerian orbital elements
        """
        if gmat_data is None or len(gmat_data) < 6:
            return None
            
        x, y, z, vx, vy, vz = gmat_data[:6]
        
        # Constants
        mu = 3.986004418e5  # Earth gravitational parameter (km^3/s^2)
        
        # Position and velocity vectors
        r_vec = [x, y, z]
        v_vec = [vx, vy, vz]
        
        r = self.vector_norm(r_vec)
        v = self.vector_norm(v_vec)
        
        # Specific angular momentum
        h_vec = self.cross_product(r_vec, v_vec)
        h = self.vector_norm(h_vec)
        
        # Eccentricity vector
        h_cross_v = self.cross_product(h_vec, v_vec)
        e_vec = [
            h_cross_v[0] / mu - r_vec[0] / r,
            h_cross_v[1] / mu - r_vec[1] / r,
            h_cross_v[2] / mu - r_vec[2] / r
        ]
        e = self.vector_norm(e_vec)
        
        # Semi-major axis
        energy = v**2 / 2 - mu / r
        a = -mu / (2 * energy) if energy < 0 else float('inf')
        
        # Inclination
        i = math.acos(h_vec[2] / h) if h != 0 else 0
        
        # Right ascension of ascending node
        k_vec = [0, 0, 1]
        n_vec = self.cross_product(k_vec, h_vec)
        n = self.vector_norm(n_vec)
        
        if n != 0:
            raan = math.acos(n_vec[0] / n)
            if n_vec[1] < 0:
                raan = 2 * math.pi - raan
        else:
            raan = 0
        
        # Argument of periapsis
        if n != 0 and e > 1e-10:
            argp = math.acos(self.dot_product(n_vec, e_vec) / (n * e))
            if e_vec[2] < 0:
                argp = 2 * math.pi - argp
        else:
            argp = 0
        
        # True anomaly
        if e > 1e-10:
            nu = math.acos(self.dot_product(e_vec, r_vec) / (e * r))
            if self.dot_product(r_vec, v_vec) < 0:
                nu = 2 * math.pi - nu
        else:
            nu = 0
        
        # Mean anomaly (via eccentric anomaly)
        if e < 1:
            E = 2 * math.atan(math.sqrt((1 - e) / (1 + e)) * math.tan(nu / 2))
            M = E - e * math.sin(E)
        else:
            M = nu  # Approximation for near-circular orbits
        
        return {
            'a': a,                           # semi-major axis (km)
            'e': e,                           # eccentricity
            'i': math.degrees(i),             # inclination (degrees)
            'raan': math.degrees(raan),       # right ascension (degrees)
            'argp': math.degrees(argp),       # argument of periapsis (degrees)
            'M0': math.degrees(M),            # mean anomaly (degrees)
            'mass': 1e6,                      # default mass (kg)
            'velocity': v                     # current velocity (km/s)
        }
    
    def read_gmat_trajectory(self, filename):
        """
        Read GMAT output file and extract trajectory data
        """
        try:
            data = []
            with open(filename, 'r') as f:
                lines = f.readlines()
                # Skip header line if present
                start_line = 1 if len(lines) > 1 and 'X' in lines[0] else 0
                
                for line in lines[start_line:]:
                    values = line.strip().split()
                    if len(values) >= 6:
                        # Convert to float and take first 6 values (X, Y, Z, VX, VY, VZ)
                        data.append([float(x) for x in values[:6]])
            return data
        except Exception as e:
            print(f"Error reading GMAT file: {e}")
            # Return sample data for testing
            return self.generate_sample_data()
    
    def generate_sample_data(self):
        """Generate sample orbital data for testing"""
        print("Generating sample orbital data...")
        sample_data = []
        # Sample elliptical orbit
        for i in range(100):
            t = i * 0.1
            x = 20000 * math.cos(t)
            y = 15000 * math.sin(t)
            z = 5000 * math.sin(t * 0.5)
            vx = -2000 * math.sin(t)
            vy = 1500 * math.cos(t)
            vz = 500 * math.cos(t * 0.5)
            sample_data.append([x, y, z, vx, vy, vz])
        return sample_data
    
    async def send_gmat_data(self, websocket, path):
        """
        WebSocket server to send GMAT data to the web interface
        """
        self.connected_clients.add(websocket)
        try:
            # Read GMAT data
            gmat_data = self.read_gmat_trajectory('AsteroidTrajectory.txt')
            
            if gmat_data:
                print(f"Sending {len(gmat_data)} GMAT data points to client...")
                
                # Convert to orbital elements for each time step
                for i, state in enumerate(gmat_data):
                    if len(state) >= 6:
                        orbital_elements = self.gmat_to_orbital_elements(state)
                        
                        if orbital_elements:
                            message = {
                                'type': 'gmat_data',
                                'elements': orbital_elements,
                                'timestamp': i,
                                'cartesian': state[:6],
                                'total_points': len(gmat_data)
                            }
                            
                            await websocket.send(json.dumps(message))
                            await asyncio.sleep(0.05)  # Control update rate
            
            # Send completion message
            await websocket.send(json.dumps({
                'type': 'complete', 
                'message': f'Processed {len(gmat_data)} data points'
            }))
            
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
        except Exception as e:
            print(f"Error in WebSocket handler: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
        finally:
            self.connected_clients.remove(websocket)
    
    def start_server(self):
        """Start the WebSocket server in the current thread"""
        try:
            # Create new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Start the server
            start_server = websockets.serve(self.send_gmat_data, "localhost", 8765)
            self.server = self.loop.run_until_complete(start_server)
            
            print("GMAT Integration Bridge running on ws://localhost:8765")
            print("Server is ready to accept connections...")
            
            # Run the event loop
            self.loop.run_forever()
            
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            if self.server:
                self.server.close()
                self.loop.run_until_complete(self.server.wait_closed())
            if self.loop:
                self.loop.close()
    
    def stop_server(self):
        """Stop the WebSocket server"""
        if self.loop and self.server:
            self.server.close()
            self.loop.run_until_complete(self.server.wait_closed())
            self.loop.stop()

# Simple test function
def test_orbital_calculation():
    """Test the orbital element calculation"""
    integrator = GMATIntegration()
    
    # Test with sample data (circular orbit)
    test_data = [7000, 0, 0, 0, 7.5, 0]  # x, y, z, vx, vy, vz
    elements = integrator.gmat_to_orbital_elements(test_data)
    
    print("Test orbital elements calculation:")
    print(f"Semi-major axis: {elements['a']:.2f} km")
    print(f"Eccentricity: {elements['e']:.6f}")
    print(f"Inclination: {elements['i']:.2f}°")
    print(f"RAAN: {elements['raan']:.2f}°")
    print(f"Argument of periapsis: {elements['argp']:.2f}°")
    print(f"Mean anomaly: {elements['M0']:.2f}°")

# Run the integration bridge
if __name__ == "__main__":
    print("Starting GMAT Integration Bridge...")
    
    # Test the calculation
    test_orbital_calculation()
    
    # Create and start the server
    integrator = GMATIntegration()
    
    try:
        # Start server in the main thread (no separate thread needed)
        integrator.start_server()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        integrator.stop_server()