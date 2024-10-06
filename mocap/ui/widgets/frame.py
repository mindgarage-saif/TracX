from PyQt6.QtWidgets import QFrame, QWidget


class Frame(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

    def setActive(self, active):
        self.setProperty("class", "active" if active else "inactive")
