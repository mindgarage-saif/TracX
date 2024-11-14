import locale
import logging
import os
import signal
import sys
from logging.handlers import RotatingFileHandler

from colorlog import ColoredFormatter
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from .constants import APP_ASSETS, APP_NAME, create_directories
from .ui.window import StudioWindow


class Studio(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.title = APP_NAME
        locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
        create_directories()

    def sigint_handler(self, *args):
        """Handler for the SIGINT signal."""
        sys.stderr.write("\r")
        if self.window.confirmExit():
            self.quit()

    def run(self):
        # Show the main window
        self.window = StudioWindow(title=self.title)
        self.window.show()
        signal.signal(signal.SIGINT, self.sigint_handler)
        sys.exit(self.exec())


def configure_logging():
    # Set up file handler with rotating logs, limited to 1MB per file with 5 backup files
    file_handler = RotatingFileHandler("mocap.log", maxBytes=1_000_000, backupCount=5)
    file_handler.setLevel(logging.DEBUG)  # TODO: Change to logging.INFO for production
    file_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(file_format)

    # Set up colored console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)s] %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    console_handler.setFormatter(console_format)

    # Set up root logger with both handlers
    logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])

    return logging.getLogger(__name__)


def main():
    # Configure logging
    logger = configure_logging()

    # Create the application and run it
    logger.info("Starting the application")
    studio = Studio()
    apply_stylesheet(
        studio,
        theme="dark_purple.xml",
        css_file=os.path.join(APP_ASSETS, "styles", "app.css"),
    )
    studio.run()


if __name__ == "__main__":
    main()
