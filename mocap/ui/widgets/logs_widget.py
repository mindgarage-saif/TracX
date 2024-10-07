import os
import time

from PyQt6.QtCore import QFileSystemWatcher, QThread, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QPushButton, QTextEdit, QVBoxLayout, QWidget


class LogStreamer(QThread):
    """
    A QThread that continuously streams log file updates.

    Signals:
        new_log_signal (str): Emitted when new log data is read.
    """

    new_log_signal = pyqtSignal(str)

    def __init__(self, log_file_path, wait_for_file=True):
        super().__init__()
        self.log_file_path = log_file_path
        self.wait = wait_for_file
        self._is_running = True

    def wait_for_file(self):
        # Wait for the log file to be created
        while not os.path.exists(self.log_file_path):
            time.sleep(1)

    def run(self):
        if self.wait:
            self.wait_for_file()

        if not os.path.exists(self.log_file_path):
            return

        with open(self.log_file_path, "r") as log_file:
            # Move to the end of the file to only read new changes
            log_file.seek(0, os.SEEK_END)
            while self._is_running:
                line = log_file.readline()
                if line:
                    self.new_log_signal.emit(line)  # Emit signal with the new log line
                else:
                    time.sleep(1)  # Poll every second

    def stop(self):
        self._is_running = False


class LogsWidget(QWidget):
    """
    A widget for displaying and downloading log files.

    Attributes:
        log_file_path (str): The path to the log file.
        layout (QVBoxLayout): The layout for the widget.
        log_display (QTextEdit): The widget to display log content.
        download_button (QPushButton): The button to download the log file.
        log_thread (LogStreamer): The thread for streaming logs.
        file_watcher (QFileSystemWatcher): Watches the log file for changes.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()
        self.log_file_path = None

    def init_ui(self):
        # Set up the layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(16)

        # Use QTextEdit to simulate a console log with formatting and scroll behavior
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.layout.addWidget(self.log_display)

        # Add the download button
        self.download_button = QPushButton("Download Logs")
        self.download_button.setProperty("class", "secondary_button")
        self.download_button.clicked.connect(self.download_log)
        self.download_button.setEnabled(False)
        self.layout.addWidget(self.download_button)

        self.setLayout(self.layout)

    def start_log_streaming(self, log_file_path):
        self.log_file_path = os.path.abspath(log_file_path)
        self.download_button.setEnabled(True)

        # Clear the log display
        self.log_display.clear()

        # Start the log streaming thread
        self.log_thread = LogStreamer(self.log_file_path, wait_for_file=True)
        self.log_thread.new_log_signal.connect(
            self.update_log_display
        )  # Connect the signal
        self.log_thread.start()

        # Setup QFileSystemWatcher to listen for changes in the log file
        self.file_watcher = QFileSystemWatcher([self.log_file_path])
        self.file_watcher.fileChanged.connect(self.on_log_file_changed)

    def update_log_display(self, text):
        # Append the new text to the log display
        texts = self.log_display.toPlainText().split("\n")
        texts.append(text)
        text = "\n".join(texts[-100:])  # Limit the number of lines displayed

        self.log_display.setText(text)
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )

    def download_log(self):
        if not self.log_file_path:
            return

        # Open a file dialog to save the log file
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Log File", os.path.basename(self.log_file_path)
        )
        if save_path:
            with open(self.log_file_path, "r") as log_file:
                with open(save_path, "w") as save_file:
                    save_file.write(log_file.read())

    def on_log_file_changed(self):
        # Triggered when the file watcher detects changes to the log file
        with open(self.log_file_path, "r") as log_file:
            self.log_display.clear()
            self.log_display.setText(log_file.read())

    def closeEvent(self, event):
        # Stop the log streaming thread when the widget is closed
        self.log_thread.stop()
        self.log_thread.wait()
        event.accept()
