# app.py
from flask import Flask, render_template, request, jsonify
import os

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
    real_asteroids = [
        {
            "name": "Bennu (101955)",
            "description": "Near-Earth asteroid visited by OSIRIS-REx. High probability of Earth impact in 2182.",
            "a": 1.126,  # AU
            "e": 0.204,
            "inc": 6.035,
            "diameter": 0.49,  # km
            "mass": 7.8e10,  # kg
            "velocity": 28.5,  # km/s relative to Earth
            "hazard": "high",
            "image": "bennu.jpg",
            "mission": "OSIRIS-REx"
        },
        {
            "name": "Apophis (99942)",
            "description": "Famous near-Earth asteroid that caused concern for 2029 close approach.",
            "a": 0.922,  # AU
            "e": 0.191,
            "inc": 3.331,
            "diameter": 0.37,  # km
            "mass": 2.7e10,  # kg
            "velocity": 30.7,
            "hazard": "medium",
            "image": "apophis.jpg",
            "mission": "Multiple observations"
        },
        {
            "name": "Ryugu (162173)",
            "description": "Near-Earth asteroid visited by Hayabusa2. Carbonaceous composition.",
            "a": 1.190,  # AU
            "e": 0.190,
            "inc": 5.884,
            "diameter": 0.90,  # km
            "mass": 4.5e11,  # kg
            "velocity": 27.8,
            "hazard": "low",
            "image": "ryugu.jpg",
            "mission": "Hayabusa2"
        },
        {
            "name": "Didymos (65803)",
            "description": "Binary asteroid system, target of DART mission to test planetary defense.",
            "a": 1.644,  # AU
            "e": 0.383,
            "inc": 3.408,
            "diameter": 0.78,  # km (primary)
            "mass": 5.4e11,  # kg
            "velocity": 24.2,
            "hazard": "low",
            "image": "didymos.jpg",
            "mission": "DART"
        },
        {
            "name": "Eros (433)",
            "description": "First near-Earth asteroid discovered and first asteroid orbited by a spacecraft.",
            "a": 1.458,  # AU
            "e": 0.223,
            "inc": 10.829,
            "diameter": 16.84,  # km
            "mass": 6.7e15,  # kg
            "velocity": 24.6,
            "hazard": "low",
            "image": "eros.jpg",
            "mission": "NEAR Shoemaker"
        },
        {
            "name": "Itokawa (25143)",
            "description": "First asteroid from which samples were returned to Earth (Hayabusa mission).",
            "a": 1.324,  # AU
            "e": 0.280,
            "inc": 1.622,
            "diameter": 0.33,  # km
            "mass": 3.5e10,  # kg
            "velocity": 25.4,
            "hazard": "low",
            "image": "itokawa.jpg",
            "mission": "Hayabusa"
        },
        {
            "name": "Vesta (4)",
            "description": "One of the largest asteroids in the main belt, visited by Dawn spacecraft.",
            "a": 2.362,  # AU
            "e": 0.089,
            "inc": 7.140,
            "diameter": 525.4,  # km
            "mass": 2.6e20,  # kg
            "velocity": 19.3,
            "hazard": "none",
            "image": "vesta.jpg",
            "mission": "Dawn"
        },
        {
            "name": "Ceres (1)",
            "description": "Largest object in the asteroid belt, now classified as a dwarf planet.",
            "a": 2.766,  # AU
            "e": 0.076,
            "inc": 10.594,
            "diameter": 939.4,  # km
            "mass": 9.4e20,  # kg
            "velocity": 17.9,
            "hazard": "none",
            "image": "ceres.jpg",
            "mission": "Dawn"
        }
    ]
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