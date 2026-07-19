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

from services.fundamental_service import (
    calculate_roce,
    get_fundamental_metrics,
)

from services.fundamental_score_service import (
    calculate_fundamental_score,
)

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

        main_layout.setContentsMargins(
            25,
            25,
            25,
            25,
        )

        main_layout.setSpacing(18)

        # ------------------------------------------
        # Search Bar
        # ------------------------------------------

        self.search_bar = SearchBar()

        main_layout.addWidget(
            self.search_bar
        )

        # ------------------------------------------
        # Company Card
        # ------------------------------------------

        self.company_card = CompanyCard()

        main_layout.addWidget(
            self.company_card
        )

        # ------------------------------------------
        # Financial Metric Cards
        # ------------------------------------------

        metrics_layout = QHBoxLayout()

        metrics_layout.setSpacing(12)

        self.pe_card = MetricCard(
            "PE"
        )

        self.pb_card = MetricCard(
            "PB"
        )

        self.roe_card = MetricCard(
            "ROE"
        )

        self.roce_card = MetricCard(
            "ROCE"
        )

        self.de_card = MetricCard(
            "Debt / Equity"
        )

        metrics_layout.addWidget(
            self.pe_card
        )

        metrics_layout.addWidget(
            self.pb_card
        )

        metrics_layout.addWidget(
            self.roe_card
        )

        metrics_layout.addWidget(
            self.roce_card
        )

        metrics_layout.addWidget(
            self.de_card
        )

        main_layout.addLayout(
            metrics_layout
        )

        # ------------------------------------------
        # Fundamental Component Scores
        # ------------------------------------------

        score_metrics_layout = QHBoxLayout()

        score_metrics_layout.setSpacing(12)

        self.profitability_card = MetricCard(
            "Profitability"
        )

        self.growth_card = MetricCard(
            "Growth"
        )

        self.strength_card = MetricCard(
            "Financial Strength"
        )

        self.valuation_card = MetricCard(
            "Valuation"
        )

        score_metrics_layout.addWidget(
            self.profitability_card
        )

        score_metrics_layout.addWidget(
            self.growth_card
        )

        score_metrics_layout.addWidget(
            self.strength_card
        )

        score_metrics_layout.addWidget(
            self.valuation_card
        )

        main_layout.addLayout(
            score_metrics_layout
        )

        # ------------------------------------------
        # Fundamental Score
        # ------------------------------------------

        self.score_card = ScoreCard()

        self.score_card.title.setText(
            "⭐ Fundamental Score"
        )

        main_layout.addWidget(
            self.score_card
        )

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

        # ------------------------------------------
        # Basic Stock Data
        # ------------------------------------------

        data = get_stock_data(
            symbol
        )

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

        # ------------------------------------------
        # Fundamental Data
        # ------------------------------------------

        fundamental_data = (
            get_fundamental_metrics(
                symbol
            )
        )

        if "error" in fundamental_data:

            fundamental_data = {}

        fundamental_scores = (
            calculate_fundamental_score(
                fundamental_data
            )
        )

        # Prefer ROCE already fetched by the
        # broader fundamental data service.

        roce = fundamental_data.get(
            "roce"
        )

        if roce is None:

            roce = calculate_roce(
                symbol
            )

        self.update_ui(
            data,
            roce,
            fundamental_scores,
        )

    def update_ui(
        self,
        data,
        roce,
        fundamental_scores,
    ):

        # ------------------------------------------
        # Company Information
        # ------------------------------------------

        company = str(
            data.get(
                "name"
            ) or "N/A"
        )

        sector = str(
            data.get(
                "sector"
            ) or "N/A"
        )

        industry = str(
            data.get(
                "industry"
            ) or "N/A"
        )

        price = format_price(
            data.get(
                "price"
            )
        )

        market_cap = format_market_cap(
            data.get(
                "market_cap"
            )
        )

        self.company_card.updateData(
            company,
            sector,
            industry,
            price,
            market_cap,
        )

        # ------------------------------------------
        # PE
        # ------------------------------------------

        self.pe_card.setValue(
            format_number(
                data.get(
                    "pe"
                )
            )
        )

        # ------------------------------------------
        # PB
        # ------------------------------------------

        self.pb_card.setValue(
            format_number(
                data.get(
                    "pb"
                )
            )
        )

        # ------------------------------------------
        # ROE
        # ------------------------------------------

        self.roe_card.setValue(
            format_percentage(
                data.get(
                    "roe"
                ),
                multiply=True,
            )
        )

        # ------------------------------------------
        # ROCE
        # ------------------------------------------

        if roce is not None:

            roce_text = (
                format_percentage(
                    roce
                )
            )

        else:

            roce_text = "N/A"

        self.roce_card.setValue(
            roce_text
        )

        # ------------------------------------------
        # Debt / Equity
        #
        # Yahoo commonly supplies debtToEquity
        # as a percentage-style value.
        #
        # Example:
        # 9.827 = approximately 0.09827 D/E
        # ------------------------------------------

        debt_equity = data.get(
            "debt_equity"
        )

        if debt_equity is not None:

            try:

                debt_equity = (
                    float(
                        debt_equity
                    ) / 100
                )

                debt_equity_text = (
                    f"{debt_equity:.2f}"
                )

            except (
                TypeError,
                ValueError,
            ):

                debt_equity_text = "N/A"

        else:

            debt_equity_text = "N/A"

        self.de_card.setValue(
            debt_equity_text
        )

        # ------------------------------------------
        # Fundamental Component Scores
        # ------------------------------------------

        profitability = (
            fundamental_scores.get(
                "profitability_score"
            )
        )

        growth = (
            fundamental_scores.get(
                "growth_score"
            )
        )

        strength = (
            fundamental_scores.get(
                "financial_strength_score"
            )
        )

        valuation = (
            fundamental_scores.get(
                "valuation_score"
            )
        )

        self.profitability_card.setValue(
            self.format_score(
                profitability
            )
        )

        self.growth_card.setValue(
            self.format_score(
                growth
            )
        )

        self.strength_card.setValue(
            self.format_score(
                strength
            )
        )

        self.valuation_card.setValue(
            self.format_score(
                valuation
            )
        )

        # ------------------------------------------
        # Overall Fundamental Score
        # ------------------------------------------

        fundamental_score = (
            fundamental_scores.get(
                "fundamental_score"
            )
        )

        if fundamental_score is None:

            self.score_card.setScore(
                0
            )

        else:

            self.score_card.setScore(
                round(
                    fundamental_score
                )
            )

    def format_score(
        self,
        value,
    ):

        if value is None:

            return "N/A"

        return (
            f"{value:.1f} / 100"
        )

    def reset_metrics(self):

        self.pe_card.setValue(
            "--"
        )

        self.pb_card.setValue(
            "--"
        )

        self.roe_card.setValue(
            "--"
        )

        self.roce_card.setValue(
            "--"
        )

        self.de_card.setValue(
            "--"
        )

        self.profitability_card.setValue(
            "--"
        )

        self.growth_card.setValue(
            "--"
        )

        self.strength_card.setValue(
            "--"
        )

        self.valuation_card.setValue(
            "--"
        )

        self.score_card.setScore(
            0
        )