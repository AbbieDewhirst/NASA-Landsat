from collections import defaultdict
from datetime import timedelta
from typing import List

from flask import Flask, render_template, request, redirect, flash, jsonify
import os
from dotenv import load_dotenv
import secrets
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user, logout_user, login_user, login_required
from flask_apscheduler import APScheduler
import bcrypt
from skyfield.api import load
from skyfield.sgp4lib import EarthSatellite
from skyfield.toposlib import Topos
from datetime import datetime
from landsat_webapp.mailer import send_email

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex())
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config['SCHEDULER_API_ENABLED'] = True

scheduler = APScheduler()
scheduler.init_app(app)

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


from flask import jsonify
from collections import defaultdict
from datetime import timedelta
from skyfield.api import Topos, load


@app.get("/predict")
def predict_passover_endpoint():
    # Get lat and lon from the request
    lat = float(request.args.get('lat', 0))
    lon = float(request.args.get('lon', 0))

    # Load timescale
    ts = load.timescale()

    # Set the initial search range (30 days)
    days_increment = 30
    start_time = ts.now()
    end_time = ts.utc(ts.now().utc_datetime() + timedelta(days=days_increment))

    # Store the first occurrence of passovers for each satellite
    first_occurrence = {"LANDSAT 8": None, "LANDSAT 9": None}

    # Keep querying in 30-day increments until both LANDSAT 8 and LANDSAT 9 have results
    while not (first_occurrence["LANDSAT 8"] and first_occurrence["LANDSAT 9"]):
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
                if event == 0:  # We're only interested in the 'rise' event
                    results[sat.name].append(event_time)

        # Check for the first occurrence of both satellites
        if not first_occurrence["LANDSAT 8"] and results["LANDSAT 8"]:
            first_occurrence["LANDSAT 8"] = results["LANDSAT 8"][0]

        if not first_occurrence["LANDSAT 9"] and results["LANDSAT 9"]:
            first_occurrence["LANDSAT 9"] = results["LANDSAT 9"][0]

        # If one of the satellites is missing, extend the time window
        if not (first_occurrence["LANDSAT 8"] and first_occurrence["LANDSAT 9"]):
            start_time = end_time  # Move the start time forward
            end_time = ts.utc(end_time.utc_datetime() + timedelta(days=days_increment))  # Extend the end time

    # Return the first occurrence of passovers for both satellites
    return jsonify(first_occurrence)

# Function to be scheduled
def scheduled_task(message, email):
    print(f"\n=============\n{message} | {email}\n=============\n")
    send_email("New Landsat Notification", message, [email])
    app.logger.debug(f"Scheduled Task executed: {message}")

# Endpoint to schedule a new job
@app.post('/schedule')
@login_required
def schedule():
    try:
        data = request.json
        run_time = data.get('run_time')  # expecting 'run_time' in ISO format string
        message = data.get('message', 'No message provided')

        if not run_time:
            return jsonify({"error": "Invalid datetime format"}), 400

        run_time_dt = datetime.fromisoformat(run_time)
        job_id = f"job_{run_time_dt.strftime('%Y%m%d%H%M%S')}"

        scheduler.add_job(
            func=scheduled_task,
            trigger='date',
            run_date=run_time_dt,
            args=[message, current_user.email],
            id=job_id
        )

        return jsonify({"message": f"Job scheduled to run at {run_time_dt} with id {job_id}"}), 200

    except Exception as e:
        app.logger.error(f"Error scheduling job: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # init db if not exists
    with app.app_context():
        if not os.path.exists("instance/site.db"):
            db.create_all()
        if not scheduler.running:
            scheduler.start()

    app.run(debug=True, host='0.0.0.0')

