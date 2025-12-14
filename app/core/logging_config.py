# import logging
# from logging.handlers import RotatingFileHandler

# def setup_logging():
#     logger = logging.getLogger()
#     logger.setLevel(logging.INFO)

#     handler = RotatingFileHandler(
#         "logs/recommendation.log", 
#         maxBytes=5_000_000,  # 5MB
#         backupCount=3
#     )

#     formatter = logging.Formatter(
#         "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
#     )
#     handler.setFormatter(formatter)

#     logger.addHandler(handler)


import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")
ERROR_FILE = os.path.join(LOG_DIR, "errors.log")

logger = logging.getLogger("ai_service")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

# General logs
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=5)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Error logs
error_handler = RotatingFileHandler(ERROR_FILE, maxBytes=5_000_000, backupCount=5)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)
logger.addHandler(error_handler)
