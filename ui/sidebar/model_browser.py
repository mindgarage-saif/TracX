from PyQt5.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget


class ModelBrowser(QWidget):
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.setObjectName("ModelBrowser")
        self.setStyleSheet(
            """
            background-color: transparent;
        """
        )
        self.layout = QVBoxLayout(self)
        self.model_list = QListWidget(self)
        self.layout.addWidget(self.model_list)

        self.model_list.currentItemChanged.connect(self.on_item_selected)
        self.model_list.setSpacing(2)
        self.callback = callback

    def on_item_selected(self, current, previous):
        if previous:
            previous_widget = self.model_list.itemWidget(previous)
            previous_widget.setStyleSheet(
                """
                QLabel {
                    background-color: transparent;
                    padding: 8px;
                    color: #ccc;
                    border-bottom: 1px solid lightgray;
                }
            """
            )
        if current:
            current_widget = self.model_list.itemWidget(current)
            current_widget.setStyleSheet(
                """
                QLabel {
                    background-color: rgba(0, 0, 0, 0.5);
                    padding: 8px;
                    color: white;
                    border-bottom: 1px solid lightgray;
                }
            """
            )

            if self.callback:
                self.callback(current.text())

    def setModels(self, models):
        for model in models:
            label = QLabel(model)
            label.setStyleSheet(
                """
                QLabel {
                    background-color: transparent;
                    padding: 8px;
                    color: #ccc;
                    border-bottom: 1px solid lightgray;
                }
            """
            )

            item = QListWidgetItem(self.model_list)
            item.setText(model)
            item.setSizeHint(label.sizeHint())
            self.model_list.addItem(item)
            self.model_list.setItemWidget(item, label)

    def getModelListView(self):
        return self.model_list
