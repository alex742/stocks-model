class Strategy:
    def __init__(self, buy_threshold, sell_threshold):
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def getMetrics(self, symbol):
        return

    def makeBuySellDecision(self):
        if data.iloc[[-1]] < timestamp:
            return (0,1)
        else:
            return (1,0)


class Backtesting:
    def __init__(self, start_date, end_date, symbols, strategy, timestep, cash):
        self.start_date = start_date
        self.datetime = start_date
        self.end_date = end_date
        self.symbols = symbols
        self.strategy = strategy
        self.timestep = timestep
        
        self.positions = {"Cash": cash}
        for symbol in symbols: positions[symbol] = 0
        self.trades = [] # list of trade dictionaries {date, symbol, amount, buy/sell, total_amount}
        
        self.data = getSymbolData()

    def getSymbolData(self):
        column_names = [date] + self.symbols
        data = []
        for symbol in self.symbols
            getData(symbol) # from get_data.py
        return pd.DataFrame(data, columns=column_names)

    def getPastSymbolData(self):
        filtered_df = df[df["Date"] < self.datetime]
        return filtered_df
    
    def trade(self, symbol, cash_diff, symbol_diff):
        positions["Cash"] += cash_diff
        positions[symbol] += symbol_diff

    def step(self):
        symbol_data = getPastSymbolData()
        ideal_positions = Strategy.makeBuySellDecision(symbol_data, symbols)
        updatePositions(ideal_positions)
        self.datetime += self.timestep

    def updatePositions(self, ideal_positions):
        total_cash = 0
        for symbol in self.position:
            total_cash += symbol * getPastSymbolData().iloc[[-1]] # get the last row of the df
        for symbol in self.position:
            symbol_diff = ideal_positions[symbol] * total_cash - self.positions[symbol]
            cash_diff = symbol_diff / getPastSymbolData().iloc[[-1]]
            trade(symbol, cash_diff, symbol_diff)
        self.positions = ideal_positions


    def runBacktest():
        while self.datetime < self.end_date:
            self.step()



s = Strategy()
b = Backtesting()
b.runBacktest()

