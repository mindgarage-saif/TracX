from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
)

from TracX.constants import APP_NAME, APP_VERSION, FEATURE_STREAMING_ENABLED
from TracX.ui.styles import PAD_X

from .settings import SettingsDialog


class AppBar(QFrame):
    def __init__(self, parent, height=32):
        super().__init__(parent)
        self.setObjectName("AppBar")
        self.setFixedHeight(height)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        # Create an inner layout for the frame
        self.innerLayout = QHBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(PAD_X)

        # Back button (Unicode Home Character - U+1F3E0)
        back = QLabel("🏠", self)
        back.setObjectName("BackButton")
        back.setProperty("class", "icon")
        self.innerLayout.addWidget(back)

        # Connect back button to the previous page
        back.mousePressEvent = lambda event: parent.back()

        # Title
        title = QLabel(APP_NAME + " by DFKI", self)
        title.setObjectName("Title")
        title.setProperty("class", "h1")
        self.innerLayout.addWidget(title)

        # Fill space
        self.innerLayout.addStretch()

        # Add about button
        about = QPushButton("About", self)
        about.setObjectName("AboutButton")
        about.setProperty("class", "secondary_button")
        about.mousePressEvent = lambda event: self.showAboutDialog()
        self.innerLayout.addWidget(about)

        # Settings button
        if FEATURE_STREAMING_ENABLED:
            settings = QPushButton("⚙️", self)
            settings.setObjectName("SettingsButton")
            settings.setProperty("class", "secondary_button")
            settings.setStyleSheet("font-size: 16pt; padding: 0;")
            settings.setFixedSize(32, 32)
            settings.mousePressEvent = lambda event: self.showSettingsDialog()
            self.innerLayout.addWidget(settings)

    def showAboutDialog(self):
        QMessageBox.about(
            self,
            "About " + APP_NAME + " v" + APP_VERSION,
            f"{APP_NAME} is a markerless human motion analysis software developed by the German Research Center for Artificial Intelligence (DFKI) in Kaiserslautern, Germany.\n\n"
            f"This software is available for research purposes only and is not intended for commercial use. All rights reserved by DFKI.\n\n"
            f"Please visit the https://projects.dfki.uni-kl.de/tracx/ for more information.",
        )

    def showSettingsDialog(self):
        dialog = SettingsDialog(self)
        dialog.exec()
