from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStatusBar,
    QStackedWidget,
)

from app.sidebar import Sidebar
from app.dashboard import Dashboard
from app.stock_explorer import StockExplorer

from core.theme import APP_STYLE
from core.version import APP_NAME, APP_VERSION


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.resize(1400, 900)
        self.setStyleSheet(APP_STYLE)

        central = QWidget()
        layout = QHBoxLayout(central)

        self.sidebar = Sidebar()

        self.stack = QStackedWidget()

        self.dashboard = Dashboard()
        self.stock = StockExplorer()

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.stock)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)

        self.setCentralWidget(central)

        self.sidebar.dashboard_btn.clicked.connect(
            lambda: self.stack.setCurrentIndex(0)
        )

        self.sidebar.stock_btn.clicked.connect(
            lambda: self.stack.setCurrentIndex(1)
        )

        status = QStatusBar()
        status.showMessage(
            f"{APP_NAME}   Version {APP_VERSION}   |   Ready"
        )

        self.setStatusBar(status)