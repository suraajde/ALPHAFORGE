class SectorClassifierService:

    BANK_KEYWORDS = [
        "bank",
        "banks",
    ]

    NBFC_KEYWORDS = [
        "credit services",
        "consumer finance",
        "mortgage finance",
        "housing finance",
        "non banking",
        "non-banking",
        "nbfc",
        "financial services",
        "asset management",
        "capital markets",
    ]

    IT_KEYWORDS = [
        "information technology",
        "software",
        "it services",
        "technology",
        "computer services",
    ]

    def _clean(self, value):

        if value is None:
            return ""

        return str(
            value
        ).strip().lower()

    def _contains_any(
        self,
        text,
        keywords,
    ):

        return any(
            keyword in text
            for keyword in keywords
        )

    def classify(
        self,
        sector=None,
        industry=None,
        company_name=None,
    ):

        sector_text = self._clean(
            sector
        )

        industry_text = self._clean(
            industry
        )

        company_text = self._clean(
            company_name
        )

        combined = " ".join(
            [
                sector_text,
                industry_text,
                company_text,
            ]
        )

        # --------------------------------------
        # BANK
        #
        # Bank classification gets priority
        # over generic financial-services rules.
        # --------------------------------------

        if (
            self._contains_any(
                industry_text,
                self.BANK_KEYWORDS,
            )
            or (
                "bank" in company_text
                and "banking" in sector_text
            )
        ):

            return {
                "profile": "BANK",
                "sector": sector,
                "industry": industry,
            }

        # --------------------------------------
        # NBFC / FINANCIAL SERVICES
        # --------------------------------------

        if self._contains_any(
            combined,
            self.NBFC_KEYWORDS,
        ):

            return {
                "profile":
                    "FINANCIAL_SERVICES",

                "sector":
                    sector,

                "industry":
                    industry,
            }

        # --------------------------------------
        # IT / SOFTWARE
        # --------------------------------------

        if self._contains_any(
            combined,
            self.IT_KEYWORDS,
        ):

            return {
                "profile":
                    "IT_SOFTWARE",

                "sector":
                    sector,

                "industry":
                    industry,
            }

        # --------------------------------------
        # GENERAL PROFILE
        #
        # Manufacturing, consumer, pharma,
        # energy and other sectors currently
        # use the general scoring framework.
        # More profiles will be added later.
        # --------------------------------------

        return {
            "profile": "GENERAL",
            "sector": sector,
            "industry": industry,
        }


def classify_sector(
    sector=None,
    industry=None,
    company_name=None,
):

    service = (
        SectorClassifierService()
    )

    return service.classify(
        sector,
        industry,
        company_name,
    )