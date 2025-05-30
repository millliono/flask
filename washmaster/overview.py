from datetime import datetime
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import render_template_string


from .auth import login_required, admin_required
from .db import get_db
from .device_controller import DeviceController
from .logs import app_logger, LOG_FILE_PATH

washer = DeviceController("washer")
dryer = DeviceController("dryer")

bp = Blueprint("overview", __name__)

@bp.route("/", methods=("GET", "POST"))
@login_required
def index():
    if request.method == "POST":
        action = request.form["action"]
        device = request.form["device"]
        if device == "washer":
            washer.handle_device_action(action, g)
        elif device == "dryer":
            dryer.handle_device_action(action, g)
        return redirect(url_for("overview.index"))

    washer_minutes = None
    dryer_minutes = None

    if washer.started_timestamp:
        elapsed_minutes = (datetime.now() - washer.started_timestamp).seconds // 60
        washer_minutes = washer.config["duration_minutes"] - elapsed_minutes


    if dryer.started_timestamp:
        elapsed_minutes = (datetime.now() - dryer.started_timestamp).seconds // 60
        dryer_minutes = dryer.config["duration_minutes"] - elapsed_minutes


    return render_template(
        "overview.html",
        washer_available=washer.active_username is None,
        washer_active_username=washer.active_username,
        washer_minutes_remaining=washer_minutes,
        dryer_available=dryer.active_username is None,
        dryer_active_username=dryer.active_username,
        dryer_minutes_remaining=dryer_minutes,
        credits=g.user["credits"],
    )


@bp.route("/admin/logs")
@admin_required
def view_logs():
    try:
        with open(LOG_FILE_PATH, "r") as f:
            logs = f.readlines()
    except FileNotFoundError:
        logs = ["Log file not found."]

    return render_template_string(
        """
    <h1>Transaction Logs</h1>
    <pre style="background-color: #f8f9fa; padding: 10px; font-size: 17px;">{{ logs }}</pre>
    """,
        logs="".join(logs),
    )


@bp.route("/admin_dashboard", methods=("GET", "POST"))
@admin_required
def admin_dashboard():
    if request.method == "POST":
        id = request.form["id"]
        credits = request.form["credits"]
        error = None

        if not id:
            error = "Id is required."
        elif not credits:
            error = "Set credits is required."

        if error is None:
            db = get_db()
            user = db.execute("SELECT * FROM user WHERE id = ?", (id,)).fetchone()
            if user is None:
                error = "User not found."
            else:
                db.execute("UPDATE user SET credits = ? WHERE id = ?", (credits, id))
                db.commit()
                flash(f"Updated [{user['username']}] with [{credits}] credits.")
                app_logger.info(f"User [{user['username']}] bought [{credits}] credits.")
                return redirect(url_for("overview.admin_dashboard"))
        flash(error)

    db = get_db()
    users = db.execute("SELECT id, username, credits FROM user").fetchall()
    return render_template("admin_dashboard.html", users=users)
