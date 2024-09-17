import signal
import sys

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QSplashScreen

from .ui.studio import StudioWindow


class Studio(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.title = "PocketPose Studio"

    def sigint_handler(self, *args):
        """Handler for the SIGINT signal."""
        sys.stderr.write("\r")
        if self.window.confirmExit():
            self.quit()

    def run(self):
        # Show splash screen
        pixmap = QPixmap("assets/splash.png")
        splash = QSplashScreen(pixmap)
        splash.show()
        self.processEvents()

        # Show the main window
        self.window = StudioWindow(title=self.title)
        self.window.show()
        splash.finish(self.window)
        signal.signal(signal.SIGINT, self.sigint_handler)
        sys.exit(self.exec())


def main():
    studio = Studio()
    studio.run()


if __name__ == "__main__":
    main()
