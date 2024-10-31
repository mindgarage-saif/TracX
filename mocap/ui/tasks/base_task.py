import json

from easydict import EasyDict as edict
from PyQt6.QtCore import QObject


class TaskConfig(edict):
    """Task configuration class that extends the EasyDict class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validate()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._validate()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._validate()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self._validate()

    def _validate(self):
        success = self.validate()
        if not success:
            raise ValueError("Validation failed")

    def validate(self):
        return True

    def to_dict(self):
        """Converts the TaskConfig instance to a standard dictionary."""
        return {
            key: (value.to_dict() if isinstance(value, TaskConfig) else value)
            for key, value in self.items()
            if not callable(value)
        }

    def to_json(self):
        """Serializes the TaskConfig instance to JSON format."""
        return json.dumps(self.to_dict(), indent=2)

    def __str__(self):
        return self.to_json()


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
