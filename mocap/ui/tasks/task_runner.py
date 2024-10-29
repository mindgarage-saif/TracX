import os
import sys

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

    def run(self):
        """Runs the provided task with the specified arguments, optionally logs output,
        and emits a signal when the task finishes.
        """
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        log_handler = None

        if self.log_file_path:
            try:
                # Open the log file in append mode
                log_handler = open(self.log_file_path, "a")

                # Redirect stdout and stderr to the log file
                sys.stdout = log_handler
                sys.stderr = log_handler
            except Exception as e:
                self.finished.emit(False, e)
                return

        try:
            # Execute the task and capture the result
            result = self.task_instance.execute(*self.task_args, **self.task_kwargs)
            self.finished.emit(True, result)
        except Exception as e:
            # If an error occurs, log it and emit the signal with failure status
            self.finished.emit(False, e)
        finally:
            # Restore the original stdout and stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr

            # Close the log handler if it was opened
            if log_handler:
                log_handler.close()
