class SectorClassifierService:

    # --------------------------------------------------
    # BANK KEYWORDS
    # --------------------------------------------------

    BANK_KEYWORDS = [
        "bank",
        "banks",
    ]

    # --------------------------------------------------
    # NBFC / FINANCIAL SERVICES KEYWORDS
    # --------------------------------------------------

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
        "financial data & stock exchanges",
        "financial data",
        "stock exchanges",
    ]

    # --------------------------------------------------
    # IT / SOFTWARE KEYWORDS
    #
    # IMPORTANT:
    # Do NOT use the generic word "technology".
    #
    # Companies such as:
    # Dixon Technologies
    # Kaynes Technology
    #
    # are manufacturing/electronics businesses,
    # not software companies.
    # --------------------------------------------------

    IT_KEYWORDS = [
        "information technology services",
        "software",
        "software infrastructure",
        "software application",
        "it services",
        "computer services",
    ]

    # --------------------------------------------------
    # TEXT CLEANER
    # --------------------------------------------------

    def _clean(self, value):

        if value is None:
            return ""

        return (
            str(value)
            .strip()
            .lower()
        )

    # --------------------------------------------------
    # KEYWORD MATCHER
    # --------------------------------------------------

    def _contains_any(
        self,
        text,
        keywords,
    ):

        return any(
            keyword in text
            for keyword in keywords
        )

    # --------------------------------------------------
    # MAIN CLASSIFIER
    # --------------------------------------------------

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

        # --------------------------------------------------
        # 1. BANK
        #
        # Bank classification gets priority over generic
        # Financial Services classification.
        # --------------------------------------------------

        if (
            self._contains_any(
                industry_text,
                self.BANK_KEYWORDS,
            )
            or (
                "bank" in company_text
                and (
                    "financial" in sector_text
                    or "banking" in sector_text
                )
            )
        ):

            return {

                "profile":
                    "BANK",

                "sector":
                    sector,

                "industry":
                    industry,
            }

        # --------------------------------------------------
        # 2. FINANCIAL SERVICES
        #
        # Includes:
        # NBFC
        # Credit businesses
        # Asset managers
        # Capital-market businesses
        # Exchanges
        #
        # These remain PROVISIONAL in the scoring engine
        # until specialized profiles are developed.
        # --------------------------------------------------

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

        # --------------------------------------------------
        # 3. IT / SOFTWARE
        #
        # Classification is based mainly on specific
        # software / IT-service descriptions.
        #
        # Generic "Technology" is deliberately excluded.
        # --------------------------------------------------

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

        # --------------------------------------------------
        # 4. GENERAL
        #
        # Currently includes businesses such as:
        #
        # Manufacturing
        # Electronics manufacturing
        # Auto / Auto components
        # Consumer
        # Healthcare / Pharma
        # Energy
        # Industrials
        # Hotels
        # Chemicals
        #
        # More specialized profiles will be added later.
        # --------------------------------------------------

        return {

            "profile":
                "GENERAL",

            "sector":
                sector,

            "industry":
                industry,
        }


# --------------------------------------------------
# CONVENIENCE FUNCTION
# --------------------------------------------------

def classify_sector(
    sector=None,
    industry=None,
    company_name=None,
):

    service = (
        SectorClassifierService()
    )

    return service.classify(
        sector=sector,
        industry=industry,
        company_name=company_name,
    )