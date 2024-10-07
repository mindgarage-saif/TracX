import locale
import signal
import sys

from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from .constants import APP_NAME, create_directories
from .ui.studio import StudioWindow


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


def main():
    studio = Studio()
    apply_stylesheet(studio, theme="dark_purple.xml", css_file="assets/styles/app.css")
    studio.run()


if __name__ == "__main__":
    main()
