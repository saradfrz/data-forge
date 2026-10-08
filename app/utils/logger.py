import logging
from pathlib import Path


def setup_logger() -> logging.Logger:
    """
    Configure the application's logger.

    Creates the logs directory if it does not exist and writes all
    INFO and ERROR messages to logs/application.log.
    """

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    info_log_file = logs_dir / "info.log"
    error_log_file = logs_dir / "error.log"

    logger = logging.getLogger("invoice_pipeline")

    # Prevent duplicate handlers if called more than once
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    info_file_handler = logging.FileHandler(info_log_file, encoding="utf-8")
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(formatter)

    error_file_handler = logging.FileHandler(error_log_file, encoding="utf-8")
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)

    logger.addHandler(info_file_handler)
    logger.addHandler(error_file_handler)

    return logger

