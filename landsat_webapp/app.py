from datetime import datetime, timedelta
import os
import secrets

import bcrypt
from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    UserMixin,
    LoginManager,
    current_user,
    logout_user,
    login_user,
    login_required,
)
from flask_apscheduler import APScheduler
from skyfield.api import load

from landsat_parser.main import (
    get_recent_scene_metadata,
    get_scene_metadata,
    predict_passover,
    get_is_cached_download,
    start_download,
    is_downloading,
)
from landsat_parser.tiff_parser import parse_tiff_pixel
from landsat_webapp.mailer import send_email

from http import HTTPStatus

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex())
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SCHEDULER_API_ENABLED"] = True

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
    # Get lat and lon from the request
    lat = float(request.args.get("lat", 0))
    lon = float(request.args.get("lon", 0))
    days = int(request.args.get("days", 30))

    # Load timescale
    ts = load.timescale()

    # Set the initial search range (30 days)
    start_time = ts.now()
    end_time = ts.utc(ts.now().utc_datetime() + timedelta(days=days))

    # Store the passovers for each satellite
    prediction_results = predict_passover(lat, lon, start_time, end_time)

    # Return the first occurrence of passovers for both satellites
    return jsonify(prediction_results)


@app.get("/metadata")
def get_metadata():
    lat = float(request.args.get("lat", 0))
    lon = float(request.args.get("lon", 0))
    start_date = request.args.get("start_date", datetime.now().strftime("%Y-%m-%d"))
    end_date = request.args.get("end_date", datetime.now().strftime("%Y-%m-%d"))

    start_date = (
        datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=1)
    ).strftime("%Y-%m-%d")

    cloud_coverage = int(request.args.get("cloud_coverage", 100))

    results = get_scene_metadata(lat, lon, start_date, end_date, cloud_coverage)
    return jsonify(results)


@app.get("/recent-metadata")
def get_recent_metadata():
    lat = float(request.args.get("lat", 0))
    lon = float(request.args.get("lon", 0))

    results = get_recent_scene_metadata(lat, lon)
    return jsonify(results)


@app.get("/l1-data")
def get_l1_data():
    display_id = request.args.get("display_id", "")
    lat = float(request.args.get("lat", 0))
    lon = float(request.args.get("lon", 0))

    bands, rgb = parse_tiff_pixel(display_id, lat, lon)
    return jsonify({"band_values": bands, "rgb_values": rgb})


# Function to be scheduled
def scheduled_task(message, email):
    print(f"\n=============\n{message} | {email}\n=============\n")
    send_email("New Landsat Notification", message, [email])
    app.logger.debug(f"Scheduled Task executed: {message}")


# Endpoint to schedule a new job
@app.post("/schedule")
@login_required
def schedule():
    try:
        data = request.json
        run_time = data.get("run_time")  # expecting 'run_time' in ISO format string
        message = data.get("message", "No message provided")

        if not run_time:
            return jsonify({"error": "Invalid datetime format"}), HTTPStatus.BAD_REQUEST

        send_email(
            "Landsat Subscription Notification",
            f"Thank you for using the Satelleyes Landsat system!\n\nYou'll be notified at {run_time} when the satellite is near the selected location.",
            [current_user.email],
        )

        run_time_dt = datetime.fromisoformat(run_time)
        job_id = f"job_{run_time_dt.strftime('%Y%m%d%H%M%S')}_{secrets.token_hex()}"

        scheduler.add_job(
            func=scheduled_task,
            trigger="date",
            run_date=run_time_dt,
            args=[message, current_user.email],
            id=job_id,
        )

        return jsonify(
            {"message": f"You will be notified at {run_time_dt}"}
        ), HTTPStatus.OK

    except Exception as e:
        app.logger.error(f"Error scheduling job: {str(e)}")
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


# Endpoint to schedule a new job
@app.get("/download")
# @login_required
def download():
    display_id = request.form.get("display_id")
    if display_id:
        is_cached = get_is_cached_download(display_id)
        return jsonify({"exists": is_cached}), HTTPStatus.OK

    return jsonify({"error": "No display_id provided"}), HTTPStatus.BAD_REQUEST


@app.post("/download")
# @login_required
def initialize_download():
    display_id = request.form.get("display_id")
    if display_id:
        success = start_download(display_id)
        return jsonify(
            {"success": success}
        ), HTTPStatus.OK if success else HTTPStatus.INTERNAL_SERVER_ERROR

    return jsonify({"error": "No display_id provided"}), HTTPStatus.BAD_REQUEST


@app.get("/poll-download")
# @login_required
def poll_download():
    display_id = request.args.get("display_id", "")
    if display_id:
        is_download = is_downloading(display_id)
        return jsonify({"is_downloading": is_download}), HTTPStatus.OK

    return jsonify({"error": "No display_id provided"}), HTTPStatus.BAD_REQUEST


if __name__ == "__main__":
    # init db if not exists
    with app.app_context():
        if not os.path.exists("instance/site.db"):
            db.create_all()
        if not scheduler.running:
            scheduler.start()
    app.run(debug=True, host="0.0.0.0")
