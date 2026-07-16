from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QGridLayout,
)


class StockExplorer(QWidget):

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)

        title = QLabel("🔍 Stock Explorer")
        title.setStyleSheet("font-size:28px;font-weight:bold;")

        main_layout.addWidget(title)

        # Search Bar
        search_layout = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter Stock Name")

        self.search_button = QPushButton("Search")

        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.search_button)

        main_layout.addLayout(search_layout)

        # Company Information
        company = QFrame()
        company_layout = QGridLayout(company)

        company_layout.addWidget(QLabel("Company Name"),0,0)
        company_layout.addWidget(QLabel("--"),0,1)

        company_layout.addWidget(QLabel("Sector"),1,0)
        company_layout.addWidget(QLabel("--"),1,1)

        company_layout.addWidget(QLabel("Industry"),2,0)
        company_layout.addWidget(QLabel("--"),2,1)

        company_layout.addWidget(QLabel("Market Cap"),3,0)
        company_layout.addWidget(QLabel("--"),3,1)

        company_layout.addWidget(QLabel("Current Price"),4,0)
        company_layout.addWidget(QLabel("--"),4,1)

        main_layout.addWidget(company)

        # Financial Ratios
        ratios = QFrame()
        ratio_layout = QGridLayout(ratios)

        ratio_layout.addWidget(QLabel("PE"),0,0)
        ratio_layout.addWidget(QLabel("--"),0,1)

        ratio_layout.addWidget(QLabel("PB"),1,0)
        ratio_layout.addWidget(QLabel("--"),1,1)

        ratio_layout.addWidget(QLabel("ROE"),2,0)
        ratio_layout.addWidget(QLabel("--"),2,1)

        ratio_layout.addWidget(QLabel("ROCE"),3,0)
        ratio_layout.addWidget(QLabel("--"),3,1)

        ratio_layout.addWidget(QLabel("Debt/Equity"),4,0)
        ratio_layout.addWidget(QLabel("--"),4,1)

        main_layout.addWidget(ratios)

        score = QLabel("Alpha Score : -- /100")
        score.setStyleSheet("font-size:22px;font-weight:bold;")

        main_layout.addWidget(score)

        main_layout.addStretch()