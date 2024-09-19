from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from ..config.constants import PAD_X, PAD_Y


class AppBar(QWidget):
    def __init__(self, parent, height=32):
        super().__init__(parent)
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
        title = QLabel("MoCap Studio", self)
        title.setObjectName("Title")
        title.setProperty("class", "h1")
        self.innerLayout.addWidget(title)

        # Fill space
        self.innerLayout.addStretch()
