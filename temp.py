from trailing_stock import TrailingStock

stock1 = TrailingStock("Stock1")
stock1.rating = 1
stock2 = TrailingStock("Stock2")
print(f'{stock1.stock_name} - {stock1.target_removed}')
print(f'{stock2.stock_name} - {stock2.target_removed}')
stock1.target_removed = True
stock2.target_removed = True
print(f'{stock1.stock_name} - {stock1.target_removed}')
print(f'{stock2.stock_name} - {stock2.target_removed}')

print(f'{stock1.stock_name} - {stock1.rating}')
print(f'{stock2.stock_name} - {stock2.rating}')

stock1.target_id = 1223

print(f'{stock1.stock_name} - {stock1.target_id}')
print(f'{stock2.stock_name} - {stock2.target_id}')

stock1.stoploss_id = 3333
print(f'{stock1.stock_name} - {stock1.stoploss_id}')
print(f'{stock2.stock_name} - {stock2.stoploss_id}')

stock1.initial_target = 2934
j = stock1.initial_target
print(f'{stock1.stock_name} - {stock1.initial_target}')
print(f'{stock2.stock_name} - {stock2.initial_target}')
stock1.initial_target = 30000

print(f'{j}')
