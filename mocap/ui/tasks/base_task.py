from easydict import EasyDict as edict
from PyQt6.QtCore import QObject


class TaskConfig(edict):
    """Task configuration class that extends the EasyDict class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BaseTask(QObject):
    """Base class representing a task to be executed.
    Subclasses should implement the `execute` method.
    """

    def __init__(self, config: TaskConfig):
        super().__init__()
        self.config = config

    def _execute_impl(self):
        """Executes the task. This method should be overridden in subclasses
        to define specific task logic.
        """
        raise NotImplementedError("Subclasses must implement the `execute` method.")

    def execute(self):
        """Executes the task."""
        return self._execute_impl()
