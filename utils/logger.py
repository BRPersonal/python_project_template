import logging
import logging.handlers
import os
from datetime import datetime

# Create logger
logger = logging.getLogger("Ai-QuizBot")
logger.setLevel(logging.DEBUG)  # minimum log level


# Create logs directory
log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)

# Rotating file handler (similar to logback's size-based rotation)
# Max file size: 10MB, keep 5 backup files
rotating_file_handler = logging.handlers.RotatingFileHandler(
    filename=f"{log_directory}/app.log",
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)

# Log Format
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)
rotating_file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(rotating_file_handler)
