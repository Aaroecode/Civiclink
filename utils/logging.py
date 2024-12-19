import logging, os
from typing import Union
from datetime import datetime


def get_logger(name: Union[str, None] = "global", filepath: Union[str, None] = str(os.path.join(os.getcwd(), "logs")), level = logging.DEBUG):
    if not os.path.exists(filepath):
            os.makedirs(filepath, exist_ok=True)

        # Generate the timestamped log file name
    timestamp = datetime.now().strftime("%Y_%m_%d_%H")
    file_name = f"{timestamp} - log.log"
    file_path = os.path.join(filepath, file_name)

    # Create a logger instance
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if the logger is already configured
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(level)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%m/%d/%Y %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(file_handler)

    if level == logging.DEBUG:
        def log_uncaught_exceptions(ex_cls, ex, tb):
            logger.critical("Uncaught Exception", exc_info=(ex_cls, ex, tb))
        import sys
        sys.excepthook = log_uncaught_exceptions
    
    return logger




outbound_payload_logger = get_logger("Outbound Payload", os.path.join("logs", "outbound_payload"))
inbound_payload_logger = get_logger("Inbound Payload", os.path.join("logs", "inbound_payload"))
global_logger = get_logger("Global", os.path.join("logs", "global"))
elastic_logger = get_logger("elasticsearch", os.path.join("logs", "elastic"))

