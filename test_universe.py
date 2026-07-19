from services.universe_service import (
    UniverseService,
)


service = UniverseService()


print()
print("=" * 70)
print("ALPHAFORGE STOCK UNIVERSE")
print("=" * 70)

summary = service.get_summary()

for key, value in summary.items():

    print(
        f"{key:25} : {value}"
    )


print()
print("=" * 70)
print("ENABLED STOCKS")
print("=" * 70)

result = service.get_enabled_stocks()

for stock in result["stocks"]:

    print(
        f"{stock['symbol']:15} | "
        f"{stock['category']:10} | "
        f"{stock['company']}"
    )


print()
print("=" * 70)
print("SYMBOL LIST")
print("=" * 70)

symbols = service.get_symbols()

print(
    symbols["symbols"]
)