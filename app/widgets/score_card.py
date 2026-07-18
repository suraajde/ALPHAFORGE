from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QProgressBar,
)
from PySide6.QtCore import Qt


class ScoreCard(QFrame):

    def __init__(self):
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

            QProgressBar{
                border:1px solid #555;
                border-radius:8px;
                text-align:center;
                height:22px;
            }

            QProgressBar::chunk{
                background-color:#00d084;
                border-radius:8px;
            }
        """)

        layout = QVBoxLayout(self)

        self.title = QLabel("⭐ Alpha Score")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
        """)

        self.score = QLabel("-- /100")
        self.score.setAlignment(Qt.AlignCenter)
        self.score.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
            color:#00d084;
        """)

        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)

        layout.addWidget(self.title)
        layout.addWidget(self.score)
        layout.addWidget(self.progress)

    def setScore(self, score):

        if score is None:
            score = 0

        self.score.setText(f"{score}/100")
        self.progress.setValue(int(score))