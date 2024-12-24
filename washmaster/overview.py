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
import requests

from .auth import login_required
from .db import get_db

bp = Blueprint("overview", __name__)


active_username = None
started_timestamp = None
curr_timer = None

WASH_CYCLE_MINUTES = 1
WASH_CYCLE_COST = 5


turnON = {
    'channel': '0',
    'turn': 'on',
    'id': 'b0b21c10f7fc',
    'auth_key': 'MmJmMDM4dWlk7FA603986E0FEE7CDEFE52E5F53A96EBCD7BC7196DF0856E6AE90EA4B9E3D68E57F97605E0C5028D',
}
turnOFF = {
    'channel': '0',
    'turn': 'off',
    'id': 'b0b21c10f7fc',
    'auth_key': 'MmJmMDM4dWlk7FA603986E0FEE7CDEFE52E5F53A96EBCD7BC7196DF0856E6AE90EA4B9E3D68E57F97605E0C5028D',
}


def decrease_credits():
    db = get_db()
    db.execute(
        "UPDATE user SET credits = credits - ? WHERE username = ?", (WASH_CYCLE_COST, g.user['username'])
    )
    db.commit()
    g.user = (
        get_db().execute("SELECT * FROM user WHERE id = ?", (session.get("user_id"),)).fetchone()
    )


def washer_off():
    global active_username, started_timestamp, curr_timer
    response = requests.post('https://shelly-149-eu.shelly.cloud/device/relay/control', data=turnOFF)
    active_username = None
    started_timestamp = None
    if curr_timer:
        curr_timer.cancel()
        curr_timer = None


@bp.route("/", methods=("GET", "POST"))
@login_required
def index():
    global active_username, started_timestamp, curr_timer

    if request.method == "POST":
        action = request.form["action"]
        
        if action == 'start':
            if active_username:
                flash('*WASHER BUSY*')
            elif g.user['credits'] < WASH_CYCLE_COST:
                flash('*NOT ENOUGH CREDITS*')
            else:
                active_username = g.user['username']
                started_timestamp = datetime.now()
                decrease_credits()
                response = requests.post('https://shelly-149-eu.shelly.cloud/device/relay/control', data=turnON)
                curr_timer = Timer(60 * WASH_CYCLE_MINUTES, washer_off)
                curr_timer.start()
                flash('*WASHER ON*')
        elif action == 'cancel':
            if active_username != g.user['username']:
                flash("*WASHER ALREADY OFF*")
            else:
                washer_off()
                flash('*WASHER OFF*')
        
        return redirect(url_for('overview.index'))

    if started_timestamp:
        minutes_remaining = WASH_CYCLE_MINUTES - int((datetime.now() - started_timestamp).total_seconds() // 60)
    else:
        minutes_remaining = None

    return render_template("overview.html", available=active_username is None, active_username=active_username, minutes_remaining=minutes_remaining, credits=g.user['credits'])

