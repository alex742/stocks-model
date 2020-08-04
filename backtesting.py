import pandas as pd
import numpy as np
import database_data as dd

class Strategy:
    def __init__(self, buy_threshold, sell_threshold):
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def get_metrics(self, symbol):
        return

    def make_buy_sell_decision(self, symbol_data, symbols):
        # Dict of the form (cash, symbol[i])
        if symbol_data["Date"].iloc[-1].item() < int("1577840200000"):
            return {"Cash": 0, symbols[0]:1}
        else:
            return {"Cash": 0.5, symbols[0]:0.5}

class Backtesting:
    """[summary]
    """
    def __init__(self, start_date, end_date, symbols, strategy, timestep, cash):
        """[summary]

        Args:
            start_date ([type]): [description]
            end_date ([type]): [description]
            symbols ([type]): [description]
            strategy ([type]): [description]
            timestep ([type]): [description]
            cash ([type]): [description]
        """
        self.start_date = start_date
        self.datetime = int(start_date)
        self.end_date = int(end_date)
        self.symbols = symbols
        self.strategy = strategy
        self.timestep = int(timestep)
        
        self.positions = {"Cash": cash}
        # for symbol in symbols: self.positions[symbol] = 0
        self.positions = {**{key:0 for key in self.symbols}, **self.positions}
        self.positions_list = [] # list of positions at each timestep
        self.trades_list = [] # list of trade dictionaries {date, symbol, amount, buy/sell, total_amount}
        self.dailyPL = [] # list of profit/loss for all days
        self.data = self.get_symbol_data()
        self.total_cash = 0
        
    def get_symbol_data(self):
        """Gets the symbol data from the database for the given period.

        Returns:
            DataFrame: A dataframe with the symbols as columns and dates as rows.
        """
        
        column_names = ["Date"] + self.symbols
        # TODO make work with multiple symbols, atmo gets overwritten with last symbol
        # TODO loop to add the datetime and also change the ddatabase_data to only spit out price not datetime
        # data = [(datetime, symbol1price, symbol2price, ...)]
        for symbol in self.symbols:
            data = dd.get_database_data(symbol, self.start_date, self.end_date) # get data from database
    
        return pd.DataFrame(data, columns=column_names).join(pd.DataFrame([1]*len(data), columns=["Cash"]))

    def get_past_symbol_data(self, start=0, end=float("inf")):
        """ Getting only the symbol data for the last X days
    
        Returns:
            [type]: [description]
        """
        end = min(int(self.datetime), end)
        df = self.data
        mask = (df['Date'] > start) & (df['Date'] <= end)
        filtered_df = df.loc[mask]
        return filtered_df

    def step(self):
        """[summary]

        Args:
            data ([type], optional): [description]. Defaults to None.
        """
        symbol_data = self.get_past_symbol_data()
        ideal_positions = self.strategy.make_buy_sell_decision(symbol_data, self.symbols)
        self.update_positions(ideal_positions)
        self.positions_list.append({**self.positions, **{"date":self.datetime}}) 
        self.datetime += self.timestep

    def get_position_to_cash(self, symbol, date=None, amount=None):

        if date is None:
            date = self.datetime
            
        if amount is None:
            amount = self.positions[symbol]
            

        # if type(amount) == int:
        #     num holding calculations
        # elif type(amount) == str and amount[-1] == '%':
        #     percentage 
        return amount * self.data[self.data["Date"] == int(date)][symbol].values[0]

    def get_cash_to_position(self, symbol, date=None, amount=None):
        
        if date is None:
            date = self.datetime
            
        if amount is None:
            amount = self.total_cash
        
        return amount / self.data[symbol][self.data["Date"] == date]   # Rounding issue (pretend it doesn't exist) -  # ! NON ISSUE 

    def trade(self, symbol, cash_diff, symbol_diff):
        """Purchases

        Args:
            symbol ([type]): [description]
            cash_diff ([type]): [description]
            symbol_diff ([type]): [description]
        """

        self.positions["Cash"] -= cash_diff
        self.positions[symbol] += symbol_diff

        self.trades_list.append({"date":self.datetime, "symbol":symbol, "amount":symbol_diff, "cost":(cash_diff * -1), "total_amount":self.positions[symbol]}) 

    def update_positions(self, ideal_positions):
        """[summary]

        Args:
            ideal_positions ([type]): [description]
        """
        self.total_cash = 0

        for symbol in self.positions:
            self.total_cash += self.get_position_to_cash(symbol)

        for symbol in self.positions:
            symbol_diff = self.get_cash_to_position(symbol, amount=(ideal_positions[symbol] * self.total_cash)) - self.positions[symbol]
            cash_diff = self.get_position_to_cash(symbol, amount=symbol_diff)
            self.trade(symbol, cash_diff, symbol_diff)

    def run_backtest(self):
        """[summary]

        Args:
            data ([type], optional): [description]. Defaults to None.
        """
        while self.datetime < self.end_date:
            self.step()


        print("\n##########\n")
        print(self.positions_list[0]) #TODO is appending data frames
        print("\n##########\n")
        print(self.trades_list[0])




s = Strategy(1, 2)
b = Backtesting("1577836800000", "1577840400000", ["BTCUSDT"], s, 1000*60, 100)
b.run_backtest()