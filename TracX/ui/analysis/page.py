import os

from PyQt6.QtWidgets import QWidget

from TracX.constants import APP_ASSETS
from TracX.ui.common import (
    BasePage,
    EmptyState,
)

from .monocular2d import Monocular2DAnalysisPage
from .monocular3d import Monocular3DAnalysisPage
from .multiview3d import Multiview3DAnalysisPage


class AnalysisPage(BasePage):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        # Create an empty state layout
        self.emptyState = EmptyState(
            self,
            os.path.join(APP_ASSETS, "empty-state", "no-experiment-selected.png"),
            "Select or create an experiment to get started",
        )
        self.innerLayout.addWidget(self.emptyState)

        # Create the project details layout for Monocular
        self.monocular2d_analysis = Monocular2DAnalysisPage(self)
        self.innerLayout.addWidget(self.monocular2d_analysis)

        self.monocular3d_analysis = Monocular3DAnalysisPage(self)
        self.innerLayout.addWidget(self.monocular3d_analysis)

        # Create the project details layout
        self.multiview3d_analysis = Multiview3DAnalysisPage(self)
        self.innerLayout.addWidget(self.multiview3d_analysis)

        # Set the initial state
        self.emptyState.show()
        self.monocular2d_analysis.hide()
        self.monocular3d_analysis.hide()
        self.multiview3d_analysis.hide()

        # Connect the sidebar event
        parent.analysisTab.experimentSelected.connect(self.showExperiment)

    def showExperiment(self, name, experiment):
        try:
            self.emptyState.hide()
            self.monocular2d_analysis.hide()
            self.monocular3d_analysis.hide()
            self.multiview3d_analysis.hide()
            if not experiment["monocular"]:
                self.multiview3d_analysis.setExperiment(name)
                self.multiview3d_analysis.show()
            elif not experiment["is_2d"]:
                self.monocular3d_analysis.setExperiment(name)
                self.monocular3d_analysis.show()
            else:
                self.monocular2d_analysis.setExperiment(name)
                self.monocular2d_analysis.show()

            self.log(f"Opened experiment: {name}")
        except Exception as e:
            self.monocular2d_analysis.hide()
            self.monocular3d_analysis.hide()
            self.multiview3d_analysis.hide()
            self.emptyState.show()

            # Show the error message
            import traceback

            error_message = (
                f"Error opening experiment: {str(e)}\n\n{traceback.format_exc()}"
            )
            self.showAlert(error_message, "Error")
            traceback.print_exc()
