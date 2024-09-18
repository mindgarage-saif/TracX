from PyQt6.QtWidgets import QFrame, QLabel, QHBoxLayout

from ..config.constants import PAD_X, PAD_Y


class AppBar(QFrame):
    def __init__(self, parent, height=32):
        super().__init__(parent)
        self.setFixedWidth(parent.width())
        self.setFixedHeight(height + PAD_Y * 2)

        # Create an inner layout for the frame
        self.innerLayout = QHBoxLayout(self)
        self.innerLayout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        self.innerLayout.setSpacing(PAD_X)

        # Back button
        back = QLabel("←", self)
        back.setObjectName("BackButton")
        back.setStyleSheet(
            """
            #BackButton {
                color: #E3F2FD;
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
                color: #E3F2FD;
                font-size: 20px;
                font-weight: bold;
            }
        """
        )
        self.innerLayout.addWidget(title)

        # Fill space
        self.innerLayout.addStretch()
