from PyQt6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget


class ModelBrowser(QWidget):
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.setObjectName("ModelBrowser")
        self.layout = QVBoxLayout(self)
        self.model_list = QListWidget(self)
        self.layout.addWidget(self.model_list)

        self.model_list.currentItemChanged.connect(self.on_item_selected)
        self.model_list.setSpacing(2)
        self.callback = callback

    def on_item_selected(self, current, previous):
        if previous:
            previous_widget = self.model_list.itemWidget(previous)
        if current:
            current_widget = self.model_list.itemWidget(current)

            if self.callback:
                self.callback(current.text())

    def setModels(self, models):
        for model in models:
            label = QLabel(model)
            label.setProperty("class", "list-item")

            item = QListWidgetItem(self.model_list)
            item.setText(model)
            item.setSizeHint(label.sizeHint())
            self.model_list.addItem(item)
            self.model_list.setItemWidget(item, label)

    def getModelListView(self):
        return self.model_list
