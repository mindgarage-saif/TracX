import os
import sys

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import QPushButton, QWidget

from mocap.core.pipeline import execute_pipeline


class Worker(QObject):
    """
    Worker class that runs a target function in a separate thread.
    Redirects output to a log file if specified, and emits a signal when the function completes.
    """

    finished = pyqtSignal(bool, object)  # Signal emits (success: bool, result: object)

    def __init__(self, target_function, log_file=None, *args, **kwargs):
        super().__init__()
        self.target_function = target_function
        self.log_file = os.path.abspath(log_file) if log_file else None
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """
        Runs the target function with the provided arguments, redirects output to log file (if any),
        and emits a signal upon completion.
        """
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        if self.log_file:
            # Open the log file in append mode
            log_handler = open(self.log_file, "a")

            # Redirect stdout and stderr to the log file
            sys.stdout = log_handler
            sys.stderr = log_handler

        try:
            # Call the target function and capture the result
            result = self.target_function(*self.args, **self.kwargs)
            self.finished.emit(True, result)
        except Exception as e:
            # If an error occurs, log it and emit the signal with failure status
            self.finished.emit(False, e)
        finally:
            # Restore the original stdout and stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr

            # Close the log handler if it was opened
            if self.log_file:
                log_handler.close()


class EstimateMotionButton(QPushButton):
    """
    Custom button to estimate motion by executing a long-running task in a separate thread.
    """

    def __init__(self, parent: QWidget, params, callback) -> None:
        super().__init__("Process Videos", parent)
        self.params = params  # Parameters for the pipeline execution
        self.callback = callback  # Callback function to handle results
        self.worker_thread = None  # Track thread instance
        self.worker = None  # Track worker instance
        self.clicked.connect(
            self.execute_in_thread
        )  # Connect button click to start execution
        self.log_file = None  # Path to the log file
        self.running = False  # Flag to track if the pipeline is running

    def execute_in_thread(self):
        """
        Initiates the long-running pipeline execution in a separate thread.
        """
        if self.worker_thread is None or not self.worker_thread.isRunning():
            self.setEnabled(False)  # Disable the button while the pipeline is running
            self.setText("Processing...")  # Update button text

            def callback(success, result):
                self.setEnabled(True)
                self.setText("Process Videos")

                self.callback(success, result)

            # Create a new worker and thread only if no thread is already running
            self.worker_thread = QThread()
            self.worker = Worker(
                execute_pipeline, log_file=self.log_file, **self.params
            )
            self.worker.moveToThread(self.worker_thread)

            # Connect signals
            self.worker_thread.started.connect(self.worker.run)
            self.worker.finished.connect(callback)
            self.worker.finished.connect(self.cleanup_thread)
            self.worker_thread.finished.connect(self.worker_thread.deleteLater)

            # Start the worker thread
            self.worker_thread.start()

    def cleanup_thread(self, success, result):
        """
        Ensures the worker thread is properly stopped and cleaned up.
        """
        if self.worker_thread:
            self.worker_thread.quit()  # Request thread to exit gracefully
            self.worker_thread.wait()  # Wait until the thread is fully stopped
            self.worker_thread = None  # Clear the thread reference

        # Call the callback with the final result
        self.callback(success, result)
