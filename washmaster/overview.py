from datetime import datetime
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
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
        get_db().execute("SELECT * FROM user WHERE id = ?", (g.user['id'],)).fetchone()
    )


def on_timer_end():
    global active_username, started_timestamp
    # call the api
    active_username = None
    started_timestamp = None


@bp.route("/")
@login_required
def index():
    global active_username, started_timestamp

    action = request.args.get('action', None)
    
    if action == 'start':
        if active_username or started_timestamp:
            flash('already running')
        elif g.user['credits'] < 1:
            flash('no credits')
        else:
            active_username = g.user['username']
            started_timestamp = datetime.now()
            decrease_credits()
            # call api
            timer = Timer(60 * WASH_CYCLE_MINUTES, on_timer_end)
            timer.start()
            flash('started!!!')
    elif action == 'cancel':
        if active_username != g.user['username']:
            flash("already finished")
        else:
            active_username = None
            started_timestamp = None
            # call api, optionally
            flash('canceled')

    if started_timestamp:
        minutes_remaining = WASH_CYCLE_MINUTES - int((datetime.now() - started_timestamp).total_seconds() // 60)
    else:
        minutes_remaining = None

    return render_template("overview.html", available=active_username is None, active_username=active_username, minutes_remaining=minutes_remaining, credits=g.user['credits'])

