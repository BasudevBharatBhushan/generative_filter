import logging
import os

# Create a formatter
formatter = logging.Formatter(' %(levelname)s - %(asctime)s - %(module)s - %(filename)s - %(lineno)d - %(message)s')

# Create file handlers for each log level in a logs directory
logs_dir = 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

error_handler = logging.FileHandler(
    os.path.join(logs_dir, 'error.log'), encoding='utf-8')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

warning_handler = logging.FileHandler(
    os.path.join(logs_dir, 'warning.log'), encoding='utf-8')
warning_handler.setLevel(logging.WARNING)
warning_handler.setFormatter(formatter)

info_handler = logging.FileHandler(
    os.path.join(logs_dir, 'info.log'), encoding='utf-8')
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)

# Set up the basic configuration with multiple handlers
logging.basicConfig(
    
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[error_handler, warning_handler,
              info_handler, logging.StreamHandler()]
)