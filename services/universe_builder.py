from __future__ import annotations

from datetime import date
from pathlib import Path
import csv
import io
import shutil
import urllib.request


class UniverseBuilder:
    """
    AlphaForge Production Universe Builder

    Builds the research universe from official Nifty Indices
    constituent CSV files:

        Nifty Midcap 150
        Nifty Smallcap 250

    Output schema:

        symbol
        company
        category
        enabled
        source
        as_of_date

    Existing production universe is backed up before replacement.
    """

    MIDCAP_URL = (
        "https://www.niftyindices.com/"
        "IndexConstituent/"
        "ind_niftymidcap150list.csv"
    )

    SMALLCAP_URL = (
        "https://www.niftyindices.com/"
        "IndexConstituent/"
        "ind_niftysmallcap250list.csv"
    )

    EXPECTED_MIDCAP_COUNT = 150
    EXPECTED_SMALLCAP_COUNT = 250
    EXPECTED_TOTAL_COUNT = 400

    OUTPUT_FIELDS = [
        "symbol",
        "company",
        "category",
        "enabled",
        "source",
        "as_of_date",
    ]

    def __init__(
        self,
        output_file=None,
    ):

        project_root = (
            Path(__file__).resolve().parent.parent
        )

        if output_file is None:

            self.output_file = (
                project_root
                / "data"
                / "universe"
                / "stock_universe.csv"
            )

        else:

            self.output_file = Path(
                output_file
            )

    # ======================================================
    # DOWNLOAD
    # ======================================================

    def _download_csv(
        self,
        url,
    ):

        request = urllib.request.Request(

            url,

            headers={
                "User-Agent":
                    "Mozilla/5.0 "
                    "AlphaForge Universe Builder",
            },

        )

        with urllib.request.urlopen(
            request,
            timeout=30,
        ) as response:

            raw = response.read()

        # Nifty CSV files may contain BOM.

        text = raw.decode(
            "utf-8-sig"
        )

        return text

    # ======================================================
    # PARSE OFFICIAL CONSTITUENT CSV
    # ======================================================

    def _parse_constituents(
        self,
        csv_text,
        category,
        source,
        as_of_date,
    ):

        reader = csv.DictReader(
            io.StringIO(csv_text)
        )

        rows = []

        for raw_row in reader:

            # Official Nifty constituent files normally use:
            #
            # Company Name
            # Industry
            # Symbol
            # Series
            # ISIN Code

            symbol = str(
                raw_row.get(
                    "Symbol",
                    "",
                )
            ).strip().upper()

            company = str(
                raw_row.get(
                    "Company Name",
                    "",
                )
            ).strip()

            if not symbol:

                continue

            rows.append({

                "symbol":
                    symbol,

                "company":
                    company,

                "category":
                    category,

                "enabled":
                    "True",

                "source":
                    source,

                "as_of_date":
                    as_of_date,

            })

        return rows

    # ======================================================
    # VALIDATE
    # ======================================================

    def validate(
        self,
        rows,
    ):

        errors = []
        warnings = []

        symbols = [
            row["symbol"]
            for row in rows
        ]

        unique_symbols = set(
            symbols
        )

        midcap_count = sum(

            1

            for row in rows

            if row["category"]
            == "MIDCAP"

        )

        smallcap_count = sum(

            1

            for row in rows

            if row["category"]
            == "SMALLCAP"

        )

        duplicate_count = (
            len(symbols)
            - len(unique_symbols)
        )

        if (
            midcap_count
            != self.EXPECTED_MIDCAP_COUNT
        ):

            errors.append(

                "Expected "
                f"{self.EXPECTED_MIDCAP_COUNT} "
                "MIDCAP stocks, found "
                f"{midcap_count}"

            )

        if (
            smallcap_count
            != self.EXPECTED_SMALLCAP_COUNT
        ):

            errors.append(

                "Expected "
                f"{self.EXPECTED_SMALLCAP_COUNT} "
                "SMALLCAP stocks, found "
                f"{smallcap_count}"

            )

        if duplicate_count:

            errors.append(

                f"Duplicate symbols found: "
                f"{duplicate_count}"

            )

        if (
            len(unique_symbols)
            != self.EXPECTED_TOTAL_COUNT
        ):

            errors.append(

                "Expected "
                f"{self.EXPECTED_TOTAL_COUNT} "
                "unique universe stocks, found "
                f"{len(unique_symbols)}"

            )

        missing_company = [

            row["symbol"]

            for row in rows

            if not row["company"]

        ]

        if missing_company:

            warnings.append(

                "Missing company names: "
                + ", ".join(
                    missing_company
                )

            )

        return {

            "valid":
                not errors,

            "errors":
                errors,

            "warnings":
                warnings,

            "total_count":
                len(rows),

            "unique_count":
                len(unique_symbols),

            "midcap_count":
                midcap_count,

            "smallcap_count":
                smallcap_count,

            "duplicate_count":
                duplicate_count,

        }

    # ======================================================
    # BUILD IN MEMORY
    # ======================================================

    def build(
        self,
        as_of_date=None,
    ):

        if as_of_date is None:

            as_of_date = (
                date.today().isoformat()
            )

        print(
            "Downloading official "
            "Nifty Midcap 150 constituents..."
        )

        midcap_csv = self._download_csv(
            self.MIDCAP_URL
        )

        print(
            "Downloading official "
            "Nifty Smallcap 250 constituents..."
        )

        smallcap_csv = self._download_csv(
            self.SMALLCAP_URL
        )

        midcap_rows = (
            self._parse_constituents(

                midcap_csv,

                category="MIDCAP",

                source="NIFTY_MIDCAP_150",

                as_of_date=as_of_date,

            )
        )

        smallcap_rows = (
            self._parse_constituents(

                smallcap_csv,

                category="SMALLCAP",

                source="NIFTY_SMALLCAP_250",

                as_of_date=as_of_date,

            )
        )

        rows = (
            midcap_rows
            + smallcap_rows
        )

        validation = self.validate(
            rows
        )

        return {

            "rows":
                rows,

            "validation":
                validation,

            "as_of_date":
                as_of_date,

        }

    # ======================================================
    # WRITE PRODUCTION UNIVERSE
    # ======================================================

    def write(
        self,
        rows,
    ):

        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        backup_file = None

        if self.output_file.exists():

            backup_file = (
                self.output_file.with_name(
                    "stock_universe.backup.csv"
                )
            )

            shutil.copy2(
                self.output_file,
                backup_file,
            )

        with self.output_file.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:

            writer = csv.DictWriter(

                handle,

                fieldnames=
                    self.OUTPUT_FIELDS,

            )

            writer.writeheader()

            writer.writerows(
                rows
            )

        return {

            "output_file":
                str(self.output_file),

            "backup_file":
                (
                    str(backup_file)
                    if backup_file
                    else None
                ),

            "written_count":
                len(rows),

        }

    # ======================================================
    # BUILD + VALIDATE + WRITE
    # ======================================================

    def refresh(
        self,
        as_of_date=None,
    ):

        result = self.build(
            as_of_date=as_of_date
        )

        validation = result[
            "validation"
        ]

        if not validation[
            "valid"
        ]:

            return {

                **result,

                "written":
                    False,

                "write_result":
                    None,

            }

        write_result = self.write(
            result["rows"]
        )

        return {

            **result,

            "written":
                True,

            "write_result":
                write_result,

        }


# ==========================================================
# COMMAND-LINE ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    builder = UniverseBuilder()

    result = builder.build()

    validation = result[
        "validation"
    ]

    print()
    print("=" * 70)
    print(
        "ALPHAFORGE PRODUCTION UNIVERSE BUILDER"
    )
    print("=" * 70)

    print(
        "As-of date       :",
        result["as_of_date"],
    )

    print(
        "Total rows       :",
        validation["total_count"],
    )

    print(
        "Unique stocks    :",
        validation["unique_count"],
    )

    print(
        "MIDCAP           :",
        validation["midcap_count"],
    )

    print(
        "SMALLCAP         :",
        validation["smallcap_count"],
    )

    print(
        "Duplicates       :",
        validation["duplicate_count"],
    )

    print(
        "Validation       :",
        (
            "PASS"
            if validation["valid"]
            else "FAIL"
        ),
    )

    if validation["errors"]:

        print()
        print("ERRORS:")

        for error in validation[
            "errors"
        ]:

            print(
                " -",
                error,
            )

    if validation["warnings"]:

        print()
        print("WARNINGS:")

        for warning in validation[
            "warnings"
        ]:

            print(
                " -",
                warning,
            )

    print("=" * 70)

    # IMPORTANT:
    #
    # Running this file performs BUILD + VALIDATION ONLY.
    # It does NOT overwrite stock_universe.csv.
    #
    # Production write will be performed only after
    # validation has been reviewed.