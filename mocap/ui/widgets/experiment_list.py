from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from mocap.core import Experiment


class ExperimentList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self._list_widget = QListWidget(self)
        self.layout.addWidget(self._list_widget)

        self._list_widget.currentItemChanged.connect(self._on_selected)
        self._list_widget.setSpacing(2)

        # Default callback
        self.callback = lambda x: print(f"Selected: {x}")

        for name in Experiment.list():
            item = QListWidgetItem(self._list_widget)
            item.setText(name)
            self._list_widget.addItem(item)

    def _on_selected(self, current, previous):
        if current:
            self.callback(current.text())
