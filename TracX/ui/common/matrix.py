import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHeaderView,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class MatrixWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
        QTableWidget {
            border: 1px solid #888;
        }
        """)
        self.matrix = None
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        # Create table widget
        self.table = QTableWidget(self)
        self.table.horizontalHeader().setVisible(False)  # Hide header row
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )

        self.table.verticalHeader().setVisible(False)  # Hide header column
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )

        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

    def setMatrix(self, matrix: np.ndarray):
        """Set the matrix and update the table."""
        if matrix is not None:
            assert matrix.ndim in [1, 2], "The input matrix must be 1 or 2-dimensional."
            # If one-dimensional, convert to a 2D column vector
            if matrix.ndim == 1:
                matrix = matrix[:, np.newaxis]

            self.matrix = matrix
            self.updateTable()
        else:
            self.matrix = None
            self.clearTable()

    def updateTable(self):
        """Populate the table with the matrix values."""
        if self.matrix is None:
            return

        self.table.blockSignals(True)  # Prevent signals while updating
        self.table.setRowCount(self.matrix.shape[0])
        self.table.setColumnCount(self.matrix.shape[1])

        for i in range(self.matrix.shape[0]):
            for j in range(self.matrix.shape[1]):
                item = QTableWidgetItem(str(self.matrix[i, j]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)

        self.table.blockSignals(False)

    def clearTable(self):
        """Clear the table."""
        self.table.blockSignals(True)
        self.table.clearContents()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.table.blockSignals(False)

    def onValueChanged(self, item: QTableWidgetItem):
        """Update the NumPy array when a cell value changes."""
        if self.matrix is None:
            return

        try:
            value = float(item.text())
            self.matrix[item.row(), item.column()] = value
        except ValueError:
            # Revert invalid input
            self.table.blockSignals(True)
            item.setText(str(self.matrix[item.row(), item.column()]))
            self.table.blockSignals(False)
