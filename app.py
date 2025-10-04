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

@app.route("/update-kinetic-energy")
def update_kinetic_energy():
    mass = 1000  # in kilograms
    velocity = request.args.get("velocity", type=float)  # Velocity in km/s
    kinetic_energy = calculate_kinetic_energy(mass, velocity)
    kinetic_energy_sci = "{:.2e}".format(kinetic_energy)  # Format in scientific notation
    return jsonify({"kinetic_energy": kinetic_energy_sci})

if __name__ == "__main__":
    app.run(debug=False)