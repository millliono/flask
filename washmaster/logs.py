import logging
from logging.handlers import RotatingFileHandler

LOG_FILE_PATH = "app_user_actions.log"

app_logger = logging.getLogger("app")
app_logger.setLevel(logging.INFO)
app_handler = RotatingFileHandler(
    LOG_FILE_PATH, maxBytes=1 * 1024 * 1024, backupCount=3
)
app_handler.setLevel(logging.INFO)
app_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%m-%Y %H:%M:%S"
)
app_handler.setFormatter(app_formatter)
app_logger.addHandler(app_handler)
