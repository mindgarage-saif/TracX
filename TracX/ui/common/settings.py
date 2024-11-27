from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from TracX.ui.styles import PAD_X, PAD_Y


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setFixedWidth(400)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(PAD_X, PAD_Y, PAD_X, PAD_Y)
        main_layout.setSpacing(PAD_Y)

        # Live Streaming Section
        live_streaming_group = QGroupBox("Live Streaming Server")
        live_streaming_layout = QVBoxLayout()
        live_streaming_layout.setContentsMargins(0, 0, 0, 0)
        live_streaming_group.setLayout(live_streaming_layout)

        # Description
        live_streaming_description = QLabel(
            "Initialize a live streaming server to transmit motion data to a remote client. "
            "A WebSocket server will be launched on the specified port, allowing a client to "
            "connect for data analysis or rendering."
        )
        live_streaming_description.setWordWrap(True)
        live_streaming_layout.addWidget(live_streaming_description)

        # Live Streaming Server Settings
        live_streaming_form = QFormLayout()
        live_streaming_form.setContentsMargins(0, 0, 0, 0)
        self.port_input = QLineEdit()
        self.port_input.setMaxLength(4)
        self.port_input.setFixedWidth(100)
        self.port_input.setText("8765")  # Default port: 8765
        self.port_input.setEnabled(
            False
        )  # Disable editing for now (TODO: Implement a mechanism to persist settings)

        # Start Server Button
        start_server_button = QPushButton("Start Server")
        start_server_button.clicked.connect(self.start_server)

        # Add port input and button to the same row
        port_layout = QHBoxLayout()
        port_layout.setContentsMargins(0, 0, 0, 0)
        port_layout.addWidget(self.port_input)
        port_layout.addWidget(start_server_button)
        live_streaming_form.addRow("Port:", port_layout)

        # Add another row with server status
        self.server_status_label = QLabel("Not Running")
        live_streaming_form.addRow("Status:", self.server_status_label)

        live_streaming_layout.addLayout(live_streaming_form)

        main_layout.addWidget(live_streaming_group)

        # # Other Settings Section
        # other_settings_group = QGroupBox("Other Settings")
        # other_settings_layout = QVBoxLayout()
        # other_settings_layout.setContentsMargins(0, 0, 0, 0)
        # other_settings_label = QLabel("Placeholder for other settings.")
        # other_settings_layout.addWidget(other_settings_label)
        # other_settings_group.setLayout(other_settings_layout)

        # main_layout.addWidget(other_settings_group)
        main_layout.addStretch()

        # Set Layout
        self.setLayout(main_layout)

    def start_server(self):
        # Is it already running?
        if self.sender().text() == "Stop Server":
            self.server_status_label.setText("Not Running")
            # self.port_input.setEnabled(True)
            self.sender().setText("Start Server")
        else:
            port = self.port_input.text()
            if port.isdigit():
                self.server_status_label.setText(f"Running on port {port}")
                self.port_input.setEnabled(False)
                self.sender().setText("Stop Server")
            else:
                self.port_input.setFocus()
