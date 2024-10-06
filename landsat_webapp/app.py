from collections import defaultdict
from datetime import timedelta
from typing import List

from flask import Flask, render_template, request, redirect, flash, jsonify
import os
from dotenv import load_dotenv
import secrets
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user, logout_user, login_user
import bcrypt
from skyfield.api import load
from skyfield.sgp4lib import EarthSatellite
from skyfield.toposlib import Topos

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex())
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

db = SQLAlchemy(app)

# initializing authentication system
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


# Load satellite data at app startup
satellites: List[EarthSatellite] = []

def load_sat_data(filename: str) -> True:
    sat_file = load.tle_file(filename)
    landsat8 = [sat for sat in sat_file if "LANDSAT 8" in sat.name][0]
    landsat9 = [sat for sat in sat_file if "LANDSAT 9" in sat.name][0]
    satellites.append(landsat8)
    satellites.append(landsat9)
    return True

# Load the satellite data
curdir = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(curdir, "data/tle.txt")
load_sat_data(filename)

# Home route for selecting location
@app.get("/")
def home():
    return render_template("index.html")


@app.get("/login")
def login():
    return render_template("login.html")


@app.get("/register")
def register():
    return render_template("register.html")


@app.get("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect("/")


@app.post("/register")
def register_post():
    email = request.form.get("email")
    password = request.form.get("password")

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user = User(email=email, password=hashed)
    db.session.add(user)
    db.session.commit()
    flash(f"Created account for {email}. You may now log in.", "success")
    return redirect("/login")


@app.post("/login")
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    remember_me = request.form.get("rememberme")
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.checkpw(password.encode("utf-8"), user.password):
        login_user(user, remember=remember_me)
        # flash('Successfully logged in!', 'success')
        return redirect("/")
    flash("Error Logging In", "danger")
    return render_template("register.html")


@app.get("/predict")
def predict_passover_endpoint():
    # Get lat, lon, and days parameters from the request
    lat = float(request.args.get('lat', 0))
    lon = float(request.args.get('lon', 0))
    days = int(request.args.get('days', 2))  # Default to 2 days if not provided

    # Load timescale
    ts = load.timescale()
    start_time = ts.now()
    end_time = ts.utc(ts.now().utc_datetime() + timedelta(days=days))  # Check for the provided number of days

    results = defaultdict(list)

    for sat in satellites:
        location = Topos(latitude_degrees=lat, longitude_degrees=lon)

        # Predict passes over the location
        t0, events = sat.find_events(
            location, start_time, end_time, altitude_degrees=80
        )

        # Record the passover details
        for ti, event in zip(t0, events):
            event_time = ti.utc_iso()  # ti is a Time object, we call utc_iso() on it
            event_name = ["rise", "culmination", "set"][event]
            if event == 0:
                results[sat.name].append(event_time)

    return jsonify(results)


if __name__ == "__main__":
    # init db if not exists
    if not os.path.exists("instance/site.db"):
        with app.app_context():
            db.create_all()
    app.run(debug=True, host='0.0.0.0')

