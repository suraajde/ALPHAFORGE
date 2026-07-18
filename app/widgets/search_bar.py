from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)


class SearchBar(QWidget):

    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            "Enter NSE Symbol (Example: INFY)"
        )

        self.search_box.setStyleSheet("""
            QLineEdit{
                font-size:15px;
                padding:8px;
                border-radius:8px;
                border:1px solid #666;
            }
        """)

        self.search_button = QPushButton("🔍 Search")

        self.search_button.setStyleSheet("""
            QPushButton{
                background-color:#0078D7;
                color:white;
                font-size:15px;
                font-weight:bold;
                padding:8px 18px;
                border-radius:8px;
            }

            QPushButton:hover{
                background-color:#0A84FF;
            }
        """)

        layout.addWidget(self.search_box)
        layout.addWidget(self.search_button)