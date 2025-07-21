# standard library imports
import logging
import sys
from pathlib import Path

# Internal project module imports
from midjourney.utils.logger.logger import Logger


class AppLogger(Logger):
    # Private method to print a startup banner when logging is initialized
    def _init_banner(self) -> None:
        print("=============== Logging started ================")

    # Constructor for AppLogger
    def __init__(self, name: str = "midJourney", level: int = logging.INFO,
                 log_file: bool = False) -> None:
        # Create a logger with the given name
        self.logger = logging.getLogger(name)

        # Set the logging level (e.g., DEBUG, INFO)
        try:
            self.logger.setLevel(level)
        except Exception as e:
            print("Failed to set logging level in app_logger.py")
            print(f"\nWith exception: {str(e)}")
            raise ValueError(f"Exception occurred: {str(e)}")

        # Prevent log messages from being propagated to the root logger
        self.logger.propagate = False

        # Configure handlers only once (to prevent duplicate logs on re-import)
        if not self.logger.handlers:
            # Define standard log message format
            log_format = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
                "%Y-%m-%d %H:%M:%S"
            )

            # StreamHandler for console output
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(log_format)
            self.logger.addHandler(stream_handler)

            # Optional: FileHandler if `log_file` is True
            if log_file:
                log_dir = Path('logs')
                log_dir.mkdir(exist_ok=True)  # Ensuring directory exists
                file_handler = logging.FileHandler(
                    log_dir / f"{name}_logs.log",
                    encoding='utf-8'
                )
                file_handler.setFormatter(log_format)
                self.logger.addHandler(file_handler)

            # Print banner when logger is initialized
            self._init_banner()

    # Log an info-level message
    def info(self, message: str) -> None:
        self.logger.info(message)

    # Log a debug-level message
    def debug(self, message: str) -> None:
        self.logger.debug(message)

    # Log a warning-level message
    def warning(self, message: str) -> None:
        self.logger.warning(message)

    # Log an error-level message
    def error(self, message: str) -> None:
        self.logger.error(message)

    # Log an exception with stack trace
    def exception(self, message: str) -> None:
        self.logger.exception(message)

    # Custom wrapper to print debug info in a boxed format
    def custom_debug_log(self, message: str) -> None:
        self.logger.info("\n=========================\n")
        self.logger.info(message)
        self.logger.info("\n=========================\n")
    # TODO add any other method as per required
