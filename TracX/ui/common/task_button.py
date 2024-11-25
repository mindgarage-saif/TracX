import logging

from PyQt6.QtCore import QThread

from TracX.tasks import TaskRunner

from .icon_button import IconButton


class BaseTaskButton(IconButton):
    """Base class for buttons associated with tasks.
    Clicking the button will trigger the associated task.
    """

    def __init__(self, label, task_class, task_config, callback):
        """Initializes the button with a label and task to be executed on click.

        Args:
            label: The label to display on the button.
            task_class: The class of the task to be executed (must inherit from BaseTask).
            task_config: The configuration for the task.
        """
        super().__init__(label, iconSize=24)
        self.task = task_class(task_config)
        self.callback = callback  # Callback function to handle the task result
        self.task_thread = None  # Track thread instance
        self.task_runner = None  # Track task runner instance
        self.log_file = None  # Path to the log file
        self.clicked.connect(self.on_click)

    def on_click(self):
        if self.task_thread is None or not self.task_thread.isRunning():
            logging.info(f"Starting task: {self.task.__class__.__name__}")
            self.on_start()

            # Create a new worker and thread only if no thread is already running
            self.task_thread = QThread()
            self.task_runner = TaskRunner(self.task, log_file_path=self.log_file)
            self.task_runner.moveToThread(self.task_thread)

            # Connect signals
            self.task_thread.started.connect(self.task_runner.run)
            self.task_runner.finished.connect(self.finalize_thread)
            self.task_thread.finished.connect(self.task_thread.deleteLater)

            # Start the worker thread
            self.task_thread.start()

    def finalize_thread(self, success, result):
        """Ensures the worker thread is properly stopped and cleaned up."""
        if self.task_thread:
            if success:
                logging.info(
                    f"Task completed: {self.task.__class__.__name__} - Success"
                )
            else:
                logging.error(
                    f"Task completed: {self.task.__class__.__name__} - Failure"
                )
            logging.debug(f"Result: {result}")
            self.task_thread.quit()  # Request thread to exit gracefully
            self.task_thread.wait()  # Wait until the thread is fully stopped
            self.task_thread = None  # Clear the thread reference

        # Call the callback with the final result
        self.on_finish(success, result)

    def on_start(self):
        self.setEnabled(False)

    def on_finish(self, success, result):
        """Callback function to handle the task result.

        Args:
            success: A boolean indicating if the task was successful.
            result: The result of the task execution.

        """
        self.setEnabled(True)
        self.callback(success, result)
