from datetime import datetime
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import session
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
from threading import Timer

from .auth import login_required
from .db import get_db

bp = Blueprint("overview", __name__)


active_username = None
started_timestamp = None

WASH_CYCLE_MINUTES = 80


def decrease_credits():
    db = get_db()
    db.execute(
        "UPDATE user SET credits = credits - 1 WHERE username = ?", (g.user['username'],)
    )
    db.commit()
    g.user = (
        get_db().execute("SELECT * FROM user WHERE id = ?", (session.get("user_id"),)).fetchone()
    )


def on_timer_end():
    global active_username, started_timestamp
    # call the api
    active_username = None
    started_timestamp = None


@bp.route("/", methods=("GET", "POST"))
@login_required
def index():
    global active_username, started_timestamp

    if request.method == "POST":
        action = request.form["action"]
        
        if action == 'start':
            if active_username:
                flash('*WASHER BUSY*')
            elif g.user['credits'] < 1:
                flash('*NOT ENOUGH CREDITS*')
            else:
                active_username = g.user['username']
                started_timestamp = datetime.now()
                decrease_credits()
                # call api
                timer = Timer(60 * WASH_CYCLE_MINUTES, on_timer_end)
                timer.start()
                flash('*WASHER ON*')
        elif action == 'cancel':
            active_username = None
            started_timestamp = None
            # call api, optionally
            flash('*WASHER OFF*')
        
        return redirect(url_for('overview.index'))

    if started_timestamp:
        minutes_remaining = WASH_CYCLE_MINUTES - int((datetime.now() - started_timestamp).total_seconds() // 60)
    else:
        minutes_remaining = None

    return render_template("overview.html", available=active_username is None, active_username=active_username, minutes_remaining=minutes_remaining, credits=g.user['credits'])

