from flask import g
from flask import session
import requests
from threading import Timer
from flask import flash
from datetime import datetime

from .db import get_db
from .config import DEVICE_CONFIGS


class DeviceController:

    def __init__(self, device_name):
        self.device_name = device_name
        self.config = DEVICE_CONFIGS[device_name]
        self.active_username = None
        self.started_timestamp = None
        self.curr_timer = None
        self.cloud = "https://shelly-149-eu.shelly.cloud/device/relay/control"

    def pay(self):
        db = get_db()
        db.execute(
            "UPDATE user SET credits = credits - ? WHERE username = ?",
            (self.config["cost"], g.user["username"]),
        )
        db.commit()
        g.user = (
            get_db()
            .execute("SELECT * FROM user WHERE id = ?", (session.get("user_id"),))
            .fetchone()
        )

    def turnOFF(self):
        response = requests.post(self.cloud, data=self.config["turnOFF"], timeout=5)
        self.active_username = None
        self.started_timestamp = None
        if self.curr_timer:
            self.curr_timer.cancel()
            self.curr_timer = None

    def turnON_and_startTimer(self):
        response = requests.post(self.cloud, data=self.config["turnON"], timeout=5)
        self.curr_timer = Timer(60 * self.config["duration_minutes"], self.turnOFF)

    def handle_device_action(self, action, g):
        if action == "start":
            if self.active_username:
                flash(f"*{self.device_name.upper()} BUSY*")
            elif g.user["credits"] < self.config["cost"]:
                flash(f"*NOT ENOUGH CREDITS*")
            else:
                self.active_username = g.user["username"]
                self.started_timestamp = datetime.now()
                self.pay()
                self.turnON_and_startTimer()
                flash(f"*{self.device_name.upper()} ON*")
        elif action == "cancel":
            if self.active_username != g.user["username"]:
                flash(f"*{self.device_name.upper()} ALREADY OFF*")
            else:
                self.turnOFF()
                flash(f"*{self.device_name.upper()} OFF*")
