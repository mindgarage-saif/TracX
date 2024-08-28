#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPalette,
    QPen,
    QPolygon,
)
from PyQt5.QtWidgets import QWidget

__textColor__ = QColor(187, 187, 187)
__backgroudColor__ = QColor(100, 63, 65)
__font__ = QFont("Decorative", 10)


class QTimeLine(QWidget):

    startChanged = pyqtSignal(float)
    endChanged = pyqtSignal(float)

    def __init__(self, duration, fps, parent):
        super(QWidget, self).__init__(parent)
        self.setObjectName("QTimeLine")
        self.setFixedHeight(100)
        self.setFixedWidth(parent.width() - 16)

        # Set variables
        self.backgroundColor = __backgroudColor__
        self.textColor = __textColor__
        self.font = __font__
        self.pointerStartPos = 0  # Default starting pointer position
        self.pointerEndPos = 0  # Default ending pointer position
        self.activePointer = None  # Track which pointer is active
        self.setDuration(duration)
        self.fps = fps

        self.pos = None
        self.is_in = False  # check if mouse is inside the widget

        self.setMouseTracking(True)  # Mouse events
        self.setAutoFillBackground(True)  # background

        pal = QPalette()
        pal.setColor(QPalette.Background, self.backgroundColor)
        self.setPalette(pal)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setPen(self.textColor)
        qp.setFont(self.font)
        qp.setRenderHint(QPainter.Antialiasing)
        w = 0
        # Draw time
        scale = self.getScale()
        while w <= self.width():
            qp.drawText(
                w - 50, 0, 100, 100, Qt.AlignHCenter, self.getTimeString(w * scale)
            )
            w += 100
        # Draw down line
        qp.setPen(QPen(Qt.darkCyan, 5, Qt.SolidLine))
        qp.drawLine(0, 40, self.width(), 40)

        # Draw dash lines
        point = 0
        qp.setPen(QPen(self.textColor))
        qp.drawLine(0, 40, self.width(), 40)
        while point <= self.width():
            if point % 30 != 0:
                qp.drawLine(3 * point, 40, 3 * point, 30)
            else:
                qp.drawLine(3 * point, 40, 3 * point, 20)
            point += 10

        if self.pos is not None and self.is_in:
            qp.drawLine(self.pos.x(), 0, self.pos.x(), 40)

        self.drawPointers(qp)

        # Clear clip path
        path = QPainterPath()
        path.addRect(
            self.rect().x(), self.rect().y(), self.rect().width(), self.rect().height()
        )
        qp.setClipPath(path)
        qp.end()

    def drawPointers(self, qp):
        # Draw the region between pointers
        qp.setBrush(QBrush(Qt.lightGray, Qt.Dense4Pattern))
        qp.drawRect(
            self.pointerStartPos, 20, self.pointerEndPos - self.pointerStartPos, 20
        )

        # Draw pointers
        for pos in [self.pointerStartPos, self.pointerEndPos]:
            qp.setPen(Qt.darkCyan)
            qp.setBrush(QBrush(Qt.darkCyan))
            poly = QPolygon(
                [QPoint(pos - 10, 20), QPoint(pos + 10, 20), QPoint(pos, 40)]
            )
            qp.drawPolygon(poly)
            qp.drawLine(QPoint(pos, 40), QPoint(pos, self.height()))

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton and self.activePointer:
            x = e.pos().x()
            if self.activePointer == "start":
                self.pointerStartPos = max(
                    0, min(x, self.pointerEndPos - 10)
                )  # Prevent overlap
            else:
                self.pointerEndPos = min(
                    self.width(), max(x, self.pointerStartPos + 10)
                )
            self.update()

    def mousePressEvent(self, e):
        x = e.pos().x()
        # Determine which pointer is closer
        if abs(x - self.pointerStartPos) < abs(x - self.pointerEndPos):
            self.activePointer = "start"
            self.pointerStartPos = x
        else:
            self.activePointer = "end"
            self.pointerEndPos = x
        self.update()

    def mouseReleaseEvent(self, e):
        if self.activePointer:
            self.emitPositionChanged()
        self.activePointer = None

    # Enter
    def enterEvent(self, e):
        self.is_in = True

    # Leave
    def leaveEvent(self, e):
        self.is_in = False
        self.update()

    # Get time string from seconds
    def getTimeString(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d" % (h, m, s)

    # Get scale from length
    def getScale(self):
        return float(self.duration) / float(self.width())

    def emitPositionChanged(self):
        self.startChanged.emit(self.pointerStartPos * self.getScale())
        self.endChanged.emit(self.pointerEndPos * self.getScale())

    # Get duration
    def getDuration(self):
        return self.duration

    # Set background color
    def setBackgroundColor(self, color):
        self.backgroundColor = color

    # Set text color
    def setTextColor(self, color):
        self.textColor = color

    # Set Font
    def setTextFont(self, font):
        self.font = font

    def setDuration(self, duration):
        self.duration = duration
        if duration <= 0:
            self.duration = 0
            self.setEnabled(False)

            # Set pointer positions
            self.pointerStartPos = 0
            self.pointerEndPos = 0

        else:
            self.setEnabled(True)

            # Set pointer positions
            self.pointerStartPos = 0
            self.pointerEndPos = int(duration / self.getScale())
        
        self.update()