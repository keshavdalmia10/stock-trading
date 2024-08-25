from stock import Stock
class TrailingStock(Stock):
    def __init__(self, stock_name):
        super().__init__(stock_name)
        self._target_removed = False
        self._target_id = 0
        self._stoploss_id = 0
        self._initial_target = 0

    @property
    def target_removed(self):
        return self._target_removed

    @target_removed.setter
    def target_removed(self, target_removed):
        if isinstance(target_removed, (bool)):
            self._target_removed = target_removed
        else:
            raise ValueError("target_removed should be boolean")

    @property
    def target_id(self):
        return self._target_id

    @target_id.setter
    def target_id(self, new_target_id):
        if isinstance(new_target_id, (int)):
            self._target_id = new_target_id
        else:
            raise ValueError("Target ID must be a number.")
        
    @property
    def stoploss_id(self):
        return self._stoploss_id

    @stoploss_id.setter
    def stoploss_id(self, new_stoploss_id):
        if isinstance(new_stoploss_id, (int)):
            self._stoploss_id = new_stoploss_id
        else:
            raise ValueError("Order ID must be a number.")
        
    @property
    def initial_target(self):
        return self._initial_target

    @initial_target.setter
    def initial_target(self, new_initial_target):
        if isinstance(new_initial_target, (int, float)):
            self._initial_target = new_initial_target
        else:
            raise ValueError("Initial target must be a number/float.")