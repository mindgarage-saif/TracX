from PyQt6.QtWidgets import QFrame, QVBoxLayout

from .inferencer_settings import InferencerSettings
from .visualizer_settings import VisualizerSettings


class Sidebar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedWidth(int(parent.width() * 0.3))
        self.setFixedHeight(parent.height())

        # Create an inner layout for the frame
        self.innerLayout = QVBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(16)

        # Inferencer and visualizer settings
        self.visualizerSettings = VisualizerSettings(self)
        inferencer_height = (
            self.height()
            - self.visualizerSettings.innerLayout.sizeHint().height()
            - 16 * 2
        )
        self.inferencerSettings = InferencerSettings(self, height=inferencer_height)

        # Add to inner layout
        self.innerLayout.addWidget(self.inferencerSettings)
        self.innerLayout.addWidget(self.visualizerSettings)
