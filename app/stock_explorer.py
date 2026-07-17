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


class StockExplorer(QWidget):

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)

        title = QLabel("🔍 Stock Explorer")
        title.setStyleSheet("font-size:28px;font-weight:bold;")
        main_layout.addWidget(title)

        # -----------------------------
        # Search Bar
        # -----------------------------
        search_layout = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter NSE Symbol (Example: INFY)")

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_stock)

        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.search_button)

        main_layout.addLayout(search_layout)

        # -----------------------------
        # Company Information
        # -----------------------------
        company = QFrame()
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

        # -----------------------------
        # Financial Ratios
        # -----------------------------
        ratios = QFrame()
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
        self.score.setStyleSheet("font-size:22px;font-weight:bold;")
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

        # -----------------------------
        # Company Details
        # -----------------------------
        self.name_label.setText(str(data.get("name", "N/A")))
        self.sector_label.setText(str(data.get("sector", "N/A")))
        self.industry_label.setText(str(data.get("industry", "N/A")))

        # -----------------------------
        # Market Cap
        # -----------------------------
        market_cap = data.get("market_cap")

        if isinstance(market_cap, (int, float)):
            self.marketcap_label.setText(f"{market_cap:,}")
        else:
            self.marketcap_label.setText("N/A")

        # -----------------------------
        # Price
        # -----------------------------
        price = data.get("price")

        if isinstance(price, (int, float)):
            self.price_label.setText(f"₹ {price:,.2f}")
        else:
            self.price_label.setText("N/A")

        # -----------------------------
        # PE
        # -----------------------------
        pe = data.get("pe")

        if isinstance(pe, (int, float)):
            self.pe_label.setText(f"{pe:.2f}")
        else:
            self.pe_label.setText("N/A")

        # -----------------------------
        # PB
        # -----------------------------
        pb = data.get("pb")

        if isinstance(pb, (int, float)):
            self.pb_label.setText(f"{pb:.2f}")
        else:
            self.pb_label.setText("N/A")

        # -----------------------------
        # ROE
        # -----------------------------
        roe = data.get("roe")

        if isinstance(roe, (int, float)):
            self.roe_label.setText(f"{roe * 100:.2f} %")
        else:
            self.roe_label.setText("N/A")

        # -----------------------------
        # ROCE
        # -----------------------------
        if roce is not None:
            self.roce_label.setText(f"{roce:.2f} %")
        else:
            self.roce_label.setText("N/A")

        # -----------------------------
        # Debt / Equity
        # -----------------------------
        de = data.get("debt_equity")

        if isinstance(de, (int, float)):
            self.de_label.setText(f"{de:.2f}")
        else:
            self.de_label.setText("N/A")