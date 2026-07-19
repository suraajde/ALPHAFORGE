from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
)

from app.screens.sidebar import Sidebar
from app.screens.dashboard import Dashboard
from app.screens.stock_explorer import StockExplorer
from app.screens.research_radar import ResearchRadar


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("AlphaForge")
        self.resize(1600, 900)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)

        # ---------------- Sidebar ----------------

        self.sidebar = Sidebar()

        # ---------------- Pages ----------------

        self.pages = QStackedWidget()

        self.dashboard = Dashboard()
        self.stock_explorer = StockExplorer()
        self.research_radar = ResearchRadar()

        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.stock_explorer)
        self.pages.addWidget(self.research_radar)

        # ---------------- Layout ----------------

        layout.addWidget(self.sidebar)
        layout.addWidget(self.pages)

        # ---------------- Navigation ----------------

        self.sidebar.dashboard_btn.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.dashboard)
        )

        self.sidebar.stock_btn.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.stock_explorer)
        )

        self.sidebar.research_btn.clicked.connect(
            lambda: self.pages.setCurrentWidget(self.research_radar)
        )