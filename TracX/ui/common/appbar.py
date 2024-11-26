from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
)

from TracX.constants import APP_NAME, APP_VERSION
from TracX.ui.styles import PAD_X


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
            f"{APP_NAME} is a sophisticated tool designed for recording and processing motion capture data, primarily aimed at advancing research in the field of biomechanics and human motion analysis. "
            + "Developed by the German Research Center for Artificial Intelligence (DFKI) in Kaiserslautern, Germany, it integrates state-of-the-art algorithms and user-friendly interfaces to facilitate high-precision data acquisition and analysis."
            + "\n\n"
            + f"The name {APP_NAME} is derived from 'Positura Animata', which translates to 'animated posture' in Latin, reflecting the tool's focus on capturing and analyzing dynamic human postures.",
        )

    def showSettingsDialog(self):
        QMessageBox.information(
            self,
            "Settings",
            "Settings functionality is under development and will be available in a future update.",
        )
