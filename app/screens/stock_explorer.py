from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)

from app.widgets.search_bar import SearchBar
from app.widgets.company_card import CompanyCard
from app.widgets.metric_card import MetricCard
from app.widgets.score_card import ScoreCard

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

        self.build_ui()
        self.connect_signals()

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(18)

        # Search

        self.search_bar = SearchBar()

        main_layout.addWidget(self.search_bar)

        # Company Information

        self.company_card = CompanyCard()

        main_layout.addWidget(self.company_card)

        # Financial Metric Cards

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(12)

        self.pe_card = MetricCard("PE")
        self.pb_card = MetricCard("PB")
        self.roe_card = MetricCard("ROE")
        self.roce_card = MetricCard("ROCE")
        self.de_card = MetricCard("Debt / Equity")

        metrics_layout.addWidget(self.pe_card)
        metrics_layout.addWidget(self.pb_card)
        metrics_layout.addWidget(self.roe_card)
        metrics_layout.addWidget(self.roce_card)
        metrics_layout.addWidget(self.de_card)

        main_layout.addLayout(metrics_layout)

        # Alpha Score

        self.score_card = ScoreCard()

        main_layout.addWidget(self.score_card)

        main_layout.addStretch()

    def connect_signals(self):

        self.search_bar.search_button.clicked.connect(
            self.search_stock
        )

        self.search_bar.search_box.returnPressed.connect(
            self.search_stock
        )

    def search_stock(self):

        symbol = (
            self.search_bar
            .search_box
            .text()
            .strip()
            .upper()
        )

        if not symbol:
            return

        data = get_stock_data(symbol)

        if "error" in data:

            self.company_card.updateData(
                "Stock Not Found",
                "Please check the NSE symbol",
                "",
                "--",
                "--",
            )

            self.reset_metrics()

            return

        roce = calculate_roce(symbol)

        self.update_ui(data, roce)

    def update_ui(self, data, roce):

        # Company Card

        company = str(
            data.get("name") or "N/A"
        )

        sector = str(
            data.get("sector") or "N/A"
        )

        industry = str(
            data.get("industry") or "N/A"
        )

        price = format_price(
            data.get("price")
        )

        market_cap = format_market_cap(
            data.get("market_cap")
        )

        self.company_card.updateData(
            company,
            sector,
            industry,
            price,
            market_cap,
        )

        # Metric Cards

        self.pe_card.setValue(
            format_number(
                data.get("pe")
            )
        )

        self.pb_card.setValue(
            format_number(
                data.get("pb")
            )
        )

        self.roe_card.setValue(
            format_percentage(
                data.get("roe"),
                multiply=True,
            )
        )

        if roce is not None:

            roce_text = format_percentage(
                roce
            )

        else:

            roce_text = "N/A"

        self.roce_card.setValue(
            roce_text
        )

        self.de_card.setValue(
            format_number(
                data.get("debt_equity")
            )
        )

        # Alpha Score remains inactive until
        # the real Alpha Score Engine is built.

        self.score_card.setScore(0)

    def reset_metrics(self):

        self.pe_card.setValue("--")
        self.pb_card.setValue("--")
        self.roe_card.setValue("--")
        self.roce_card.setValue("--")
        self.de_card.setValue("--")

        self.score_card.setScore(0)