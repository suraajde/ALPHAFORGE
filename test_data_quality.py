from services.fundamental_service import (
    get_fundamental_metrics,
)

from services.data_quality_service import (
    calculate_data_quality,
)


for symbol in [
    "INFY",
    "KPITTECH",
    "BSE",
]:

    print()
    print("=" * 60)
    print(
        f"DATA QUALITY TEST: {symbol}"
    )
    print("=" * 60)

    data = get_fundamental_metrics(
        symbol
    )

    quality = calculate_data_quality(
        data
    )

    for key, value in quality.items():

        print(
            f"{key:25} : {value}"
        )