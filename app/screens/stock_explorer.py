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

from services.stock_service import get_stock_data
from services.fundamental_service import calculate_roce

from utils.formatter import (
    format_price,
    format_market_cap,
    format_percentage,
    format_number,
)


class StockExplorer(QWidget):

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)

        title = QLabel("🔍 Stock Explorer")
        title.setStyleSheet("font-size:28px;font-weight:bold;")
        main_layout.addWidget(title)

        # ---------------------------------------------------
        # Search
        # ---------------------------------------------------

        search_layout = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            "Enter NSE Symbol (Example: INFY)"
        )

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_stock)

        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.search_button)

        main_layout.addLayout(search_layout)

        # ---------------------------------------------------
        # Company Information
        # ---------------------------------------------------

        company = QFrame()
        company.setFrameShape(QFrame.StyledPanel)

        company_layout = QGridLayout(company)

        company_layout.addWidget(QLabel("Company Name"), 0, 0)
        self.name_label = QLabel("--")
        company_layout.addWidget(self.name_label, 0, 1)

        company_layout.addWidget(QLabel("Sector"), 1, 0)
        self.sector_label = QLabel("--")
        company_layout.addWidget(self.sector_label, 1, 1)

        company_layout.addWidget(QLabel("Industry"), 2, 0)
        self.industry_label = QLabel("--")
        company_layout.addWidget(self.industry_label, 2, 1)

        company_layout.addWidget(QLabel("Market Cap"), 3, 0)
        self.marketcap_label = QLabel("--")
        company_layout.addWidget(self.marketcap_label, 3, 1)

        company_layout.addWidget(QLabel("Current Price"), 4, 0)
        self.price_label = QLabel("--")
        company_layout.addWidget(self.price_label, 4, 1)

        main_layout.addWidget(company)

        # ---------------------------------------------------
        # Ratios
        # ---------------------------------------------------

        ratios = QFrame()
        ratios.setFrameShape(QFrame.StyledPanel)

        ratio_layout = QGridLayout(ratios)

        ratio_layout.addWidget(QLabel("PE"), 0, 0)
        self.pe_label = QLabel("--")
        ratio_layout.addWidget(self.pe_label, 0, 1)

        ratio_layout.addWidget(QLabel("PB"), 1, 0)
        self.pb_label = QLabel("--")
        ratio_layout.addWidget(self.pb_label, 1, 1)

        ratio_layout.addWidget(QLabel("ROE"), 2, 0)
        self.roe_label = QLabel("--")
        ratio_layout.addWidget(self.roe_label, 2, 1)

        ratio_layout.addWidget(QLabel("ROCE"), 3, 0)
        self.roce_label = QLabel("--")
        ratio_layout.addWidget(self.roce_label, 3, 1)

        ratio_layout.addWidget(QLabel("Debt / Equity"), 4, 0)
        self.de_label = QLabel("--")
        ratio_layout.addWidget(self.de_label, 4, 1)

        main_layout.addWidget(ratios)

        self.score = QLabel("Alpha Score : -- /100")
        self.score.setStyleSheet(
            "font-size:22px;font-weight:bold;"
        )

        main_layout.addWidget(self.score)

        main_layout.addStretch()

    def search_stock(self):

        symbol = self.search_box.text().strip()

        if not symbol:
            return

        data = get_stock_data(symbol)
        roce = calculate_roce(symbol)

        if "error" in data:
            self.name_label.setText("Stock Not Found")
            return

        # Company

        self.name_label.setText(str(data.get("name", "N/A")))
        self.sector_label.setText(str(data.get("sector", "N/A")))
        self.industry_label.setText(str(data.get("industry", "N/A")))

        # Price

        self.price_label.setText(
            format_price(data.get("price"))
        )

        # Market Cap

        self.marketcap_label.setText(
            format_market_cap(data.get("market_cap"))
        )

        # PE

        self.pe_label.setText(
            format_number(data.get("pe"))
        )

        # PB

        self.pb_label.setText(
            format_number(data.get("pb"))
        )

        # ROE

        self.roe_label.setText(
            format_percentage(
                data.get("roe"),
                multiply=True,
            )
        )

        # ROCE

        if roce is not None:
            self.roce_label.setText(
                format_percentage(roce)
            )
        else:
            self.roce_label.setText("N/A")

        # Debt / Equity

        self.de_label.setText(
            format_number(
                data.get("debt_equity")
            )
        )