from stock import Stock
my_dict = {"apple": Stock("APPLE"), "banana": 3}
# my_dict.update({"orange": 2, "grape": 10})
my_dict["appledd"] = 10
stock = my_dict["apple"]
print(stock.stock_namde)
# print((Stock)(my_dict["apple"]).stock_name)