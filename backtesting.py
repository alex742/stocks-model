import pandas as pd
import numpy as np
import database_data as dd
from get_data import milliseconds_to_UTC
import argparse
from decimal import *
import matplotlib.pyplot as plt

VERBOSE = True

def my_floor(number, precision=0):
    return np.round(number - 0.5 * 10**(-precision), precision)
def my_ceil(number, precision=0):
    return np.round(number + 0.5 * 10**(-precision), precision)

class Strategy:
    def __init__(self, buy_threshold, sell_threshold):
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def get_metrics(self, symbol):
        return

    def make_buy_sell_decision(self, symbol_data, symbols):
        # Dict of the form (cash, symbol[i])
        if symbol_data["Date"].iloc[-1].item() < end:
            return {"Cash": 0, symbols[0]: 1, symbols[1]: 0}
        else:
            return {"Cash": 1, symbols[0]: 0, symbols[1]: 0}

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
        for symbol in self.symbols:
            data = dd.get_database_data(symbol, self.start_date, self.end_date)
            if self.symbols[0] == symbol:
                df = pd.DataFrame(data, columns=["Date", symbol])
            else:
                df2 = pd.DataFrame(data, columns=["Date", symbol])
                df = pd.merge(df, df2, on='Date')
                
        df["Cash"] = [1]*len(df.index)
        return df

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
        self.positions_list.append({ **{"date":self.datetime}, **self.positions}) 
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
        # print(symbol)
        # print(amount * self.data[symbol][self.data["Date"] == int(date)].values[0])
        # # print(Decimal(amount * self.data[symbol][self.data["Date"] == int(date)].values[0]))
        # print(my_floor(amount * self.data[symbol][self.data["Date"] == int(date)].values[0], 2))
        return amount * self.data[symbol][self.data["Date"] == int(date)].values[0] # Floating point errors arise here # TODO fix this 

    def get_cash_to_position(self, symbol, date=None, amount=None):
        
        if date is None:
            date = self.datetime
            
        if amount is None:
            amount = self.total_cash
        return amount / self.data[symbol][self.data["Date"] == date].values[0]  # Floating point errors arise here # TODO fix this 

    def trade(self, symbol, cash_diff, symbol_diff):
        """Purchases

        Args:
            symbol ([type]): [description]
            cash_diff ([type]): [description]
            symbol_diff ([type]): [description]
        """
        
        self.positions["Cash"] -= cash_diff
        self.positions[symbol] += symbol_diff

        self.trades_list.append({
            "date":self.datetime, 
            "symbol":symbol, 
            "amount":symbol_diff, 
            "cost":(cash_diff * -1), 
            "total_amount":self.positions[symbol]
            }) 

    def update_positions(self, ideal_positions):
        """[summary]

        Args:
            ideal_positions ([type]): [description]
        """
        self.total_cash = 0

        for symbol in self.positions:
            self.total_cash += self.get_position_to_cash(symbol)

        for symbol in self.positions:
            if my_floor(self.get_cash_to_position(symbol, amount=(ideal_positions[symbol] * self.total_cash)) - self.positions[symbol],8) > 0:
                symbol_diff = my_floor(self.get_cash_to_position(symbol, amount=(ideal_positions[symbol] * self.total_cash)) - self.positions[symbol],8)
            else:
                symbol_diff = my_ceil(self.get_cash_to_position(symbol, amount=(ideal_positions[symbol] * self.total_cash)) - self.positions[symbol],8)    
            cash_diff = self.get_position_to_cash(symbol, amount=symbol_diff)
            self.trade(symbol, cash_diff, symbol_diff)

    def run_backtest(self):
        """[summary]

        Args:
            data ([type], optional): [description]. Defaults to None.
        """
        error_list = []
        value_list = []
        while self.datetime <= self.end_date:
            self.step()
            if VERBOSE and (self.datetime % (1000*60*60*24)) == 0:
                print(f'{milliseconds_to_UTC(self.datetime)}\t{self.positions}\r', end="")

                value = 0
                for symbol in self.positions:
                    value += self.get_position_to_cash(symbol)
                
                move = self.get_symbol_data()[self.get_symbol_data()["Date"] == self.datetime]["BTCUSDT"].values/self.get_symbol_data()[self.get_symbol_data()["Date"] == start]["BTCUSDT"].values
                error_list.append(- move * 100 + value)
                value_list.append(self.get_symbol_data()[self.get_symbol_data()["Date"] == self.datetime]["BTCUSDT"].values)
        print(error_list, value_list)
        return [error_list, value_list]

        # print("\n##### POSITIONS #####\n")
        # for i in range(len(self.positions_list)):
        #     print(i, ": ", self.positions_list[i])

        # print("\n##### TRADES #####\n")
        # for i in range(len(self.trades_list)):
        #     print(i, ":  ", self.trades_list[i])

        # print("\n##### CHECK #####\n")
        if VERBOSE:
            print(self.positions_list[-1])
            # print("START PRICE", self.get_symbol_data()[self.get_symbol_data()["Date"] == start]["BTCUSDT"].values)
            # print("END PRICE", self.get_symbol_data()[self.get_symbol_data()["Date"] == end]["BTCUSDT"].values)
            # print("% MOVE", move)
            # print("FP ERROR", move * 100 - self.positions_list[-1]['Cash'])
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", help="increase output verbosity", action="store_true")
    args = parser.parse_args()
    if args.verbosity:
        VERBOSE = True

    s = Strategy(1, 2)
    start = 1577836800000
    error_list = []
    end = start + (1000*60*60*24)*10
    b = Backtesting(str(start), str(end), ["BTCUSDT", "ETHUSDT"], s, 1000*60, 100)
    error_list, value_list = b.run_backtest()

    fig, axs = plt.subplots(2)
    fig.suptitle('Vertically stacked subplots')
    axs[0].plot(error_list)
    axs[1].plot(value_list)
    plt.show()