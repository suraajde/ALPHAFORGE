from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PySide6.QtCore import Qt


class MetricCard(QFrame):

    def __init__(self, title, value="--"):
        super().__init__()

        self.setFrameShape(QFrame.StyledPanel)

        self.setStyleSheet("""
            QFrame{
                background-color:#23272e;
                border:1px solid #3c4048;
                border-radius:10px;
            }

            QLabel{
                color:white;
            }
        """)

        layout = QVBoxLayout(self)

        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            font-size:13px;
            color:#BBBBBB;
        """)

        self.value = QLabel(value)
        self.value.setAlignment(Qt.AlignCenter)
        self.value.setStyleSheet("""
            font-size:22px;
            font-weight:bold;
            color:#00d084;
        """)

        layout.addWidget(self.title)
        layout.addWidget(self.value)

    def setValue(self, value):
        self.value.setText(str(value))