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

    def is_online(self):
        try:
            response = requests.post(
                "https://shelly-149-eu.shelly.cloud/device/status",
                data=self.config["status"],
                timeout=5,
            )
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        except requests.exceptions.RequestException as e:
            return None
        else:
            response_json = response.json()
            if response_json["data"]["online"]:
                return True
            else:
                return False


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

    def send_request(self, data, timeout):
        try:
            response = requests.post(self.cloud, data=data, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            flash("*error: BAD REQUEST*")
            return False
        else:
            return True

    def start_device(self, g):
        if not self.is_online():
            flash(f"*SERVICE OFFLINE*")
            return
        else:
            if self.curr_timer: 
                self.curr_timer.cancel()
                self.curr_timer = None

            if self.send_request(self.config["turnON"], timeout=5):
                self.active_username = g.user["username"]
                self.started_timestamp = datetime.now()
                self.pay()
                self.curr_timer = Timer(60 * self.config["duration_minutes"], self.cancel_device)
                self.curr_timer.start()
                flash(f"*{self.device_name.upper()} ON*")

    def cancel_device(self):
        if self.send_request(self.config["turnOFF"], timeout=5):
            self.active_username = None
            self.started_timestamp = None
            if self.curr_timer:
                self.curr_timer.cancel()
                self.curr_timer = None
            flash(f"*{self.device_name.upper()} OFF*")

    def handle_device_action(self, action, g):
        if action == "start":
            if self.active_username:
                flash(f"*{self.device_name.upper()} BUSY*")
            elif g.user["credits"] < self.config["cost"]:
                flash("*NOT ENOUGH CREDITS*")
            else:
                self.start_device(g)
        elif action == "cancel":
            if self.active_username != g.user["username"]:
                flash(f"*{self.device_name.upper()} ALREADY OFF*")
            else:
                self.cancel_device()
