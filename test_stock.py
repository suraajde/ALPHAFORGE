from services.stock_service import get_stock_data
from services.fundamental_service import calculate_roce

symbol = "INFY"

print(get_stock_data(symbol))

print("ROCE =", calculate_roce(symbol))