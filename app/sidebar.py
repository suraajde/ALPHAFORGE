from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class Sidebar(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.dashboard_btn = QPushButton("🏠 Dashboard")
        self.stock_btn = QPushButton("📈 Stock Explorer")
        self.radar_btn = QPushButton("🎯 Research Radar")
        self.portfolio_btn = QPushButton("💼 Portfolio")
        self.watch_btn = QPushButton("👁 Watchtower")
        self.settings_btn = QPushButton("⚙ Settings")

        for btn in [
            self.dashboard_btn,
            self.stock_btn,
            self.radar_btn,
            self.portfolio_btn,
            self.watch_btn,
            self.settings_btn,
        ]:
            btn.setMinimumHeight(45)
            layout.addWidget(btn)

        layout.addStretch()