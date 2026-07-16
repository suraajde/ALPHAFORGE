from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Dashboard")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setStyleSheet("font-size:28px; font-weight:bold;")

        welcome = QLabel(
            "Welcome to AlphaForge\n\n"
            "This is the beginning of your Investment Operating System."
        )
        welcome.setStyleSheet("font-size:16px;")

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(welcome)
        layout.addStretch()