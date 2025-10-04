# app.py
from flask import Flask, render_template, request

app = Flask(__name__)

def calculate_kinetic_energy(mass, velocity):
    return 0.5 * mass * velocity ** 2

@app.route("/")
def index():
    # Example values for mass and velocity
    mass = 1000  # in kilograms
    velocity = 20  # in meters per second
    kinetic_energy = calculate_kinetic_energy(mass, velocity)
    return render_template("index.html", kinetic_energy=kinetic_energy)

if __name__ == "__main__":
    app.run(debug=True)