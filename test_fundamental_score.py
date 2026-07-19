from services.fundamental_service import (
    get_fundamental_metrics,
)

from services.fundamental_score_service import (
    calculate_fundamental_score,
)


symbol = "INFY"

data = get_fundamental_metrics(symbol)

scores = calculate_fundamental_score(data)

print(f"\nAlphaForge Fundamental Score: {symbol}")
print("-" * 50)

for key, value in scores.items():
    print(f"{key:30} : {value}")