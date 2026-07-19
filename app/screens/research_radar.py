from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QFrame,
)

from services.universe_service import UniverseService
from services.research_radar_service import ResearchRadarService


# ==========================================================
# RADAR BACKGROUND WORKER
# ==========================================================

class RadarWorker(QThread):

    finished_scan = Signal(dict)
    failed_scan = Signal(str)

    def __init__(
        self,
        symbols,
        force_refresh=False,
    ):
        super().__init__()

        self.symbols = symbols
        self.force_refresh = force_refresh

    def run(self):

        try:

            service = ResearchRadarService()

            result = service.rank_symbols(
                self.symbols,
                limit=30,
                force_refresh=self.force_refresh,
            )

            self.finished_scan.emit(
                result
            )

        except Exception as exc:

            self.failed_scan.emit(
                str(exc)
            )


# ==========================================================
# METRIC CARD
# ==========================================================

class MetricCard(QFrame):

    def __init__(
        self,
        title,
        value="0",
    ):
        super().__init__()

        self.setStyleSheet("""
            QFrame {
                background: #1f2937;
                border-radius: 8px;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout(
            self
        )

        self.value_label = QLabel(
            str(value)
        )

        self.value_label.setStyleSheet(
            "font-size: 24px;"
            "font-weight: bold;"
            "color: white;"
        )

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet(
            "font-size: 12px;"
            "color: #9ca3af;"
        )

        layout.addWidget(
            self.value_label
        )

        layout.addWidget(
            title_label
        )

    def set_value(
        self,
        value,
    ):

        self.value_label.setText(
            str(value)
        )


# ==========================================================
# RESEARCH RADAR SCREEN
# ==========================================================

class ResearchRadar(QWidget):

    def __init__(self):

        super().__init__()

        self.worker = None

        self.universe_service = (
            UniverseService()
        )

        root = QVBoxLayout(
            self
        )

        # ==================================================
        # HEADER
        # ==================================================

        header = QHBoxLayout()

        title_box = QVBoxLayout()

        title = QLabel(
            "Research Radar"
        )

        title.setStyleSheet(
            "font-size: 28px;"
            "font-weight: bold;"
        )

        subtitle = QLabel(
            "Production universe screening and "
            "Top-30 investment research candidates"
        )

        subtitle.setStyleSheet(
            "font-size: 14px;"
            "color: #6b7280;"
        )

        title_box.addWidget(
            title
        )

        title_box.addWidget(
            subtitle
        )

        header.addLayout(
            title_box
        )

        header.addStretch()

        self.scan_btn = QPushButton(
            "Run Radar Scan"
        )

        self.refresh_btn = QPushButton(
            "Force Refresh"
        )

        for button in (
            self.scan_btn,
            self.refresh_btn,
        ):

            button.setMinimumHeight(
                40
            )

            button.setMinimumWidth(
                140
            )

        header.addWidget(
            self.scan_btn
        )

        header.addWidget(
            self.refresh_btn
        )

        root.addLayout(
            header
        )

        # ==================================================
        # STATUS
        # ==================================================

        self.status_label = QLabel(
            "Ready"
        )

        self.status_label.setStyleSheet(
            "padding: 8px;"
            "color: #374151;"
        )

        root.addWidget(
            self.status_label
        )

        # ==================================================
        # METRIC CARDS
        # ==================================================

        cards = QHBoxLayout()

        self.universe_card = MetricCard(
            "Universe"
        )

        self.analyzed_card = MetricCard(
            "Analyzed"
        )

        self.eligible_card = MetricCard(
            "Production Eligible"
        )

        self.review_card = MetricCard(
            "Review Pool"
        )

        self.cache_card = MetricCard(
            "Cache Hits"
        )

        for card in (
            self.universe_card,
            self.analyzed_card,
            self.eligible_card,
            self.review_card,
            self.cache_card,
        ):

            cards.addWidget(
                card
            )

        root.addLayout(
            cards
        )

        # ==================================================
        # RADAR TABLE
        # ==================================================

        self.table = QTableWidget()

        columns = [

            "Rank",
            "Symbol",
            "Company",
            "Sector",
            "Fundamental",
            "Technical",
            "Composite",
            "Readiness",
            "Confidence",
            "Coverage",
            "Data Status",

        ]

        self.table.setColumnCount(
            len(columns)
        )

        self.table.setHorizontalHeaderLabels(
            columns
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        self.table.horizontalHeader().setStretchLastSection(
            True
        )

        self.table.setAlternatingRowColors(
            True
        )

        self.table.setSortingEnabled(
            False
        )

        root.addWidget(
            self.table
        )

        # ==================================================
        # EVENTS
        # ==================================================

        self.scan_btn.clicked.connect(
            lambda: self.start_scan(
                False
            )
        )

        self.refresh_btn.clicked.connect(
            lambda: self.start_scan(
                True
            )
        )

        # ==================================================
        # INITIAL UNIVERSE LOAD
        # ==================================================

        self.load_universe_summary()


    # ======================================================
    # LOAD UNIVERSE SUMMARY
    # ======================================================

    def load_universe_summary(
        self,
    ):

        try:

            universe_result = (
                self.universe_service.get_symbols()
            )

            symbols = universe_result.get(
                "symbols",
                [],
            )

            self.universe_card.set_value(
                len(symbols)
            )

            self.status_label.setText(
                f"Production universe loaded: "
                f"{len(symbols)} stocks"
            )

        except Exception as exc:

            self.universe_card.set_value(
                0
            )

            self.status_label.setText(
                f"Universe load warning: {exc}"
            )


    # ======================================================
    # START RADAR SCAN
    # ======================================================

    def start_scan(
        self,
        force_refresh=False,
    ):

        # --------------------------------------------------
        # PREVENT MULTIPLE SIMULTANEOUS SCANS
        # --------------------------------------------------

        if (
            self.worker
            and self.worker.isRunning()
        ):

            return

        # --------------------------------------------------
        # LOAD PRODUCTION UNIVERSE
        # --------------------------------------------------

        try:

            universe_result = (
                self.universe_service.get_symbols()
            )

            symbols = universe_result.get(
                "symbols",
                [],
            )

            if not symbols:

                QMessageBox.warning(

                    self,

                    "Research Radar",

                    "No enabled symbols found "
                    "in the production universe.",

                )

                return

        except Exception as exc:

            QMessageBox.critical(

                self,

                "Universe Error",

                str(exc),

            )

            return

        # --------------------------------------------------
        # DISABLE CONTROLS DURING SCAN
        # --------------------------------------------------

        self.scan_btn.setEnabled(
            False
        )

        self.refresh_btn.setEnabled(
            False
        )

        mode = (

            "Force-refreshing"

            if force_refresh

            else "Scanning"

        )

        self.status_label.setText(

            f"{mode} "
            f"{len(symbols)} "
            f"universe stocks..."

        )

        # --------------------------------------------------
        # START BACKGROUND WORKER
        # --------------------------------------------------

        self.worker = RadarWorker(

            symbols,

            force_refresh,

        )

        self.worker.finished_scan.connect(
            self.scan_complete
        )

        self.worker.failed_scan.connect(
            self.scan_failed
        )

        self.worker.start()


    # ======================================================
    # SCAN COMPLETE
    # ======================================================

    def scan_complete(
        self,
        result,
    ):

        self.scan_btn.setEnabled(
            True
        )

        self.refresh_btn.setEnabled(
            True
        )

        # --------------------------------------------------
        # SUMMARY METRICS
        # --------------------------------------------------

        self.analyzed_card.set_value(

            result.get(
                "analyzed_count",
                0,
            )

        )

        self.eligible_card.set_value(

            result.get(
                "eligible_count",
                0,
            )

        )

        self.review_card.set_value(

            result.get(
                "review_count",
                0,
            )

        )

        self.cache_card.set_value(

            result.get(
                "cache_hits",
                0,
            )

        )

        # --------------------------------------------------
        # RANKED TOP-30
        # --------------------------------------------------

        ranked = result.get(
            "ranked",
            [],
        )

        self.populate_table(
            ranked
        )

        # --------------------------------------------------
        # STATUS SUMMARY
        # --------------------------------------------------

        errors = result.get(
            "errors",
            [],
        )

        self.status_label.setText(

            "Scan complete | "

            f"Top candidates: "
            f"{len(ranked)} | "

            f"Live analyses: "
            f"{result.get('live_analyses', 0)} | "

            f"Cache hits: "
            f"{result.get('cache_hits', 0)} | "

            f"Errors: "
            f"{len(errors)}"

        )


    # ======================================================
    # SCAN FAILED
    # ======================================================

    def scan_failed(
        self,
        error,
    ):

        self.scan_btn.setEnabled(
            True
        )

        self.refresh_btn.setEnabled(
            True
        )

        self.status_label.setText(
            "Radar scan failed."
        )

        QMessageBox.critical(

            self,

            "Research Radar Error",

            error,

        )


    # ======================================================
    # POPULATE RADAR TABLE
    # ======================================================

    def populate_table(
        self,
        ranked,
    ):

        self.table.setSortingEnabled(
            False
        )

        self.table.clearContents()

        self.table.setRowCount(
            len(ranked)
        )

        fields = [

            "rank",
            "symbol",
            "company_name",
            "sector",
            "fundamental_score",
            "technical_score",
            "composite_score",
            "readiness_score",
            "data_confidence",
            "coverage_score",
            "data_status",

        ]

        for row, stock in enumerate(
            ranked
        ):

            for column, field in enumerate(
                fields
            ):

                value = stock.get(
                    field,
                    "",
                )

                if value is None:

                    value = ""

                elif isinstance(
                    value,
                    float,
                ):

                    value = (
                        f"{value:.2f}"
                    )

                item = QTableWidgetItem(
                    str(value)
                )

                if column in (
                    0,
                    4,
                    5,
                    6,
                    7,
                    9,
                ):

                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.table.setItem(

                    row,

                    column,

                    item,

                )

        self.table.setSortingEnabled(
            True
        )