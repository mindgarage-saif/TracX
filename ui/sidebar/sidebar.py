from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout

from .inferencer_settings import InferencerSettings
from .visualizer_settings import VisualizerSettings


class Sidebar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.statusBar = parent.statusBar()
        self.setFixedWidth(int(parent.width() * 0.3))
        self.setFixedHeight(parent.height() - 20)
        self.setStyleSheet(
            """
            QFrame {
            }
        """
        )

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(0)

        # Add the pocketpose logo in sidebar with 200x100 size and centered
        logo_p = QPixmap("assets/logo.png")
        logo_w = self.width() - 32
        logo_h = int(logo_w / 2)
        logo = QLabel(self)
        logo.setPixmap(
            logo_p.scaled(logo_w, logo_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        logo.setAlignment(Qt.AlignCenter)
        self.innerLayout.addWidget(logo)
        self.innerLayout.addSpacing(16)

        # Inferencer and visualizer settings
        self.visualizerSettings = VisualizerSettings(self)
        inferencer_height = (
            self.height()
            - logo_h
            - self.visualizerSettings.innerLayout.sizeHint().height()
            + 20
        )
        self.inferencerSettings = InferencerSettings(self, height=inferencer_height)

        # Add to inner layout
        self.innerLayout.addWidget(self.inferencerSettings)
        self.innerLayout.addSpacing(16)
        self.innerLayout.addWidget(self.visualizerSettings)
        self.innerLayout.addStretch()
