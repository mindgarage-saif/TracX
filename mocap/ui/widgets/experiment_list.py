from typing import Optional

from PyQt6.QtWidgets import QListWidget, QListWidgetItem

from mocap.core import Experiment


class ExperimentList(QListWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSpacing(2)
        self.currentItemChanged.connect(self.onSelectionChanged)
        self.onItemSelected = None

        # Refresh the list
        self.refresh()

    @property
    def experiments(self):
        return Experiment.list()

    def onSelectionChanged(self, current, previous):
        if current and self.onItemSelected is not None:
            self.onItemSelected(current.text(), current.data(0x0100))

    def getSelection(self) -> Optional[str]:
        currentItem = self._list_widget.currentItem()
        return currentItem.text() if currentItem else None

    def refresh(self):
        self.clear()
        for exp in self.experiments:
            item = QListWidgetItem(self)
            print(exp)
            item.setData(0x0100, exp["est_type"])
            item.setText(exp["name"])
            self.addItem(item)
