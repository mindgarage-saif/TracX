from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout

from ..config.constants import PAD_X, PAD_Y


class AppBar(QWidget):
    def __init__(self, parent, height=32):
        super().__init__(parent)
        self.setFixedWidth(parent.width())
        self.setFixedHeight(height)

        # Create an inner layout for the frame
        self.innerLayout = QHBoxLayout(self)
        self.innerLayout.setContentsMargins(0, 0, 0, 0)
        self.innerLayout.setSpacing(PAD_X)

        # Back button
        back = QLabel("←", self)
        back.setObjectName("BackButton")
        back.setStyleSheet(
            """
            #BackButton {
                font-size: 20px;
            }
        """
        )
        self.innerLayout.addWidget(back)

        # Connect back button to the previous page
        back.mousePressEvent = lambda event: parent.back()

        # Title
        title = QLabel("MoCap Studio", self)
        title.setObjectName("Title")
        title.setStyleSheet(
            """
            #Title {
                font-size: 20px;
                font-weight: bold;
            }
        """
        )
        self.innerLayout.addWidget(title)

        # Fill space
        self.innerLayout.addStretch()
