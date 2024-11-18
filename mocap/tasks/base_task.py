from PyQt6.QtCore import QObject


class BaseTask(QObject):
    """Base class representing a task to be executed.
    Subclasses should implement the `_execute_impl` method.
    """

    def __init__(self, config):
        super().__init__()
        self.config = config

    def _execute_impl(self, *args, **kwargs):
        """Executes the task. This method should be overridden in subclasses
        to define specific task logic.
        """
        raise NotImplementedError(
            "Subclasses must implement the `_execute_impl` method."
        )

    def execute(self, *args, **kwargs):
        """Executes the task."""
        return self._execute_impl(*args, **kwargs)
