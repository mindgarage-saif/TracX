import logging
import os

from PyQt6.QtCore import QObject, pyqtSignal


class TaskRunner(QObject):
    """TaskRunner class runs a provided task in a separate thread, optionally logging the output.
    Emits a signal upon task completion indicating success or failure, along with the result or error.
    """

    # Signal that emits (success: bool, result: object)
    finished = pyqtSignal(bool, object)

    def __init__(self, task_instance, log_file_path=None, *task_args, **task_kwargs):
        """Initializes the TaskRunner with a task instance to execute, optional logging, and task arguments.

        Args:
            task_instance: Instance of a class that inherits from BaseTask.
            log_file_path: Optional file path to log the output (stdout and stderr).
            task_args: Positional arguments to pass to the task's execute function.
            task_kwargs: Keyword arguments to pass to the task's execute function.

        """
        super().__init__()
        self.task_instance = task_instance
        self.log_file_path = os.path.abspath(log_file_path) if log_file_path else None
        self.task_args = task_args
        self.task_kwargs = task_kwargs

        # Set up logging if a log file path is provided
        if self.log_file_path:
            self.setup_logging()

    def setup_logging(self):
        """Configures the logging module to write logs to the specified file."""
        log_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        log_handler = logging.FileHandler(self.log_file_path)
        log_handler.setFormatter(log_formatter)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)  # Set desired logging level
        logger.addHandler(log_handler)

        # Prevent duplicate log messages in the console
        logger.propagate = False

    def run(self):
        """Runs the provided task with the specified arguments, optionally logs output,
        and emits a signal when the task finishes.
        """
        try:
            # Execute the task and capture the result
            logging.info(f"Running task: {self.task_instance}")
            logging.debug(f"Task arguments: {self.task_args}, {self.task_kwargs}")
            result = self.task_instance.execute(*self.task_args, **self.task_kwargs)
            self.finished.emit(True, result)
        except Exception as e:
            # If an error occurs, log it and emit the signal with failure status
            import traceback

            trace = traceback.format_exc()
            logging.error(f"Task failed with error: {e}\n{trace}")
            self.finished.emit(False, f"{e}\n{trace}")
        finally:
            # Clean up resources if needed
            logging.info("Task completed.")
