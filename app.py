# app.py
from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")

def calculate_kinetic_energy(mass, velocity):
    return 0.5 * mass * (velocity * 1000) ** 2  # Convert km/s to m/s for calculation

@app.route("/")
def index():
    mass = 1000  # in kilograms
    velocity = 11  # Default velocity in km/s (minimum value)
    kinetic_energy = calculate_kinetic_energy(mass, velocity)
    kinetic_energy_sci = "{:.2e}".format(kinetic_energy)  # Format in scientific notation
    return render_template("index.html", kinetic_energy=kinetic_energy_sci)

@app.route("/preset-orbits")
def preset_orbits():
    # NASA JPL Small Body Database API endpoint
    BASE_URL = "https://ssd-api.jpl.nasa.gov/sbdb.api"
    
    # Asteroid SPK-ID mapping (NASA's internal IDs)
    asteroid_ids = {
        "Bennu (101955)": "2101955",
        "Apophis (99942)": "2099942", 
        "Ryugu (162173)": "2162173",
        "Didymos (65803)": "2065803",
        "Eros (433)": "2000433",
        "Itokawa (25143)": "2025143",
        "Vesta (4)": "2000004",
        "Ceres (1)": "2000001"
    }
    
    real_asteroids = []
    
    for name, spk_id in asteroid_ids.items():
        try:
            print(f"🔄 FETCHING data for {name} (ID: {spk_id})...")
            
            # Fetch orbital data from NASA JPL API
            url = f"{BASE_URL}?sstr={spk_id}"
            print(f"   📡 API URL: {url}")
            
            response = requests.get(url)
            print(f"   ✅ Response status: {response.status_code}")
            
            data = response.json()
            print(f"   📊 Data received for {name}")
            
            # Extract orbital elements
            orbit_data = data.get('orbit', {})
            elements = orbit_data.get('elements', [])
            
            # Convert elements list to dictionary for easy access
            elements_dict = {elem['name']: elem['value'] for elem in elements}
            print(f"   🌍 Orbital elements found: {list(elements_dict.keys())}")
            
            # Extract physical parameters
            physical_data = data.get('physical_parameters', [])
            physical_dict = {param['name']: param['value'] for param in physical_data}
            print(f"   📏 Physical parameters found: {list(physical_dict.keys())}")
            
            # Get diameter (convert from meters to km)
            diameter = None
            if 'diameter' in physical_dict:
                diameter = float(physical_dict['diameter']) / 1000  # Convert m to km
                print(f"   📐 Diameter: {diameter} km")
            elif 'A' in physical_dict:  # Sometimes diameter is labeled as 'A'
                diameter = float(physical_dict['A']) / 1000
                print(f"   📐 Diameter (from A): {diameter} km")
            else:
                print("   ❌ No diameter data found")
            
            # Get mass (convert from kg if available)
            mass = None
            if 'mass' in physical_dict:
                mass = float(physical_dict['mass'])
                print(f"   ⚖️ Mass: {mass} kg")
            else:
                print("   ❌ No mass data found")
            
            # Extract orbital parameters
            a = float(elements_dict.get('a', 0))  # Semi-major axis (AU)
            e = float(elements_dict.get('e', 0))  # Eccentricity
            inc = float(elements_dict.get('i', 0))  # Inclination (degrees)
            
            print(f"   🛰️ Semi-major axis (a): {a} AU")
            print(f"   📈 Eccentricity (e): {e}")
            print(f"   📐 Inclination (i): {inc}°")
            
            # Calculate approximate velocity (simplified)
            GM = 1.32712440018e20  # m^3/s^2
            a_m = a * 1.496e11  # Convert AU to meters
            orbital_velocity = (GM / a_m) ** 0.5 / 1000  # Convert to km/s
            print(f"   🚀 Orbital velocity: {orbital_velocity} km/s")
            
            # Get additional info
            full_name = data.get('object', {}).get('fullname', name)
            neo_flag = data.get('object', {}).get('neo', False)
            pha_flag = data.get('object', {}).get('pha', False)
            
            print(f"   🎯 NEO: {neo_flag}, PHA: {pha_flag}")
            
            # Determine hazard level
            if pha_flag:
                hazard = "high"
            elif neo_flag:
                hazard = "medium" 
            else:
                hazard = "low"
            
            print(f"   ⚠️ Hazard level: {hazard}")
            
            asteroid = {
                "nasa_id": spk_id,  # <-- ADD THIS LINE
                "name": full_name,
                "description": f"{'Potentially Hazardous ' if pha_flag else ''}{'Near-Earth ' if neo_flag else ''}Asteroid - Data from NASA JPL",
                "a": round(a, 3),
                "e": round(e, 3),
                "inc": round(inc, 3),
                "diameter": round(diameter, 2) if diameter else None,
                "mass": mass,
                "velocity": round(orbital_velocity, 1),
                "hazard": hazard,
                "image": f"{name.split(' ')[0].lower()}.jpg",
                "mission": "Multiple observations"
            }
            
            real_asteroids.append(asteroid)
            print(f"   ✅ Successfully processed {name}\n")
            
        except Exception as e:
            print(f"   ❌ ERROR fetching data for {name}: {e}")
            print(f"   📋 Response content: {response.text if 'response' in locals() else 'No response'}\n")
            # Fallback to placeholder data if API fails
            real_asteroids.append({
                "name": name,
                "description": "Data temporarily unavailable",
                "a": 0, "e": 0, "inc": 0, "diameter": 0, "mass": 0, "velocity": 0,
                "hazard": "unknown", "image": "default.jpg", "mission": "Unknown"
            })
    
    print(f"🎯 FINAL RESULT: Processed {len(real_asteroids)} asteroids")
    for asteroid in real_asteroids:
        print(f"   - {asteroid['name']}: a={asteroid['a']} AU, e={asteroid['e']}, inc={asteroid['inc']}°")
    
    return render_template("preset.html", asteroids=real_asteroids)

@app.route("/update-kinetic-energy")
def update_kinetic_energy():
    mass = 1000  # in kilograms
    velocity = request.args.get("velocity", type=float)  # Velocity in km/s
    kinetic_energy = calculate_kinetic_energy(mass, velocity)
    kinetic_energy_sci = "{:.2e}".format(kinetic_energy)  # Format in scientific notation
    return jsonify({"kinetic_energy": kinetic_energy_sci})

if __name__ == "__main__":
    app.run(debug=False)