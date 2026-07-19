from services.fundamental_service import (
    get_fundamental_metrics,
)


symbol = "INFY"

data = get_fundamental_metrics(symbol)

print(f"\nFundamental Test: {symbol}")
print("-" * 50)

for key, value in data.items():
    print(f"{key:25} : {value}")