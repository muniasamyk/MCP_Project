import logging
import os
import sys
import io
from datetime import datetime

# Create logs folder if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Create today's log file name
log_file = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"

# Set up console handler with UTF-8 encoding
console_handler = logging.StreamHandler(sys.stdout)
if sys.platform == 'win32':
    # Windows: set UTF-8 encoding to handle special characters
    try:
        console_handler.setStream(open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1))
    except (AttributeError, io.UnsupportedOperation):
        # In environments like Jupyter, sys.stdout might not have a real file descriptor
        pass

# Set up logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8')
    ]
)

def get_logger(name):
    """
    Get a logger for your module
    
    Usage:
    logger = get_logger(__name__)
    logger.info("Something happened")
    """
    return logging.getLogger(name)
