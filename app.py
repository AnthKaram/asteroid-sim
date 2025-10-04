# app.py
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def calculate_kinetic_energy(mass, velocity):
    return 0.5 * mass * (velocity * 1000) ** 2  # Convert km/s to m/s for calculation

@app.route("/")
def index():
    mass = 1000  # in kilograms
    velocity = request.args.get("velocity", default=11, type=float)  # Default velocity in km/s
    kinetic_energy = calculate_kinetic_energy(mass, velocity)
    return render_template("index.html", kinetic_energy=kinetic_energy)

@app.route("/update-kinetic-energy")
def update_kinetic_energy():
    mass = 1000  # in kilograms
    velocity = request.args.get("velocity", type=float)  # Velocity in km/s
    kinetic_energy = calculate_kinetic_energy(mass, velocity)
    return jsonify({"kinetic_energy": kinetic_energy})

if __name__ == "__main__":
    app.run(debug=True)