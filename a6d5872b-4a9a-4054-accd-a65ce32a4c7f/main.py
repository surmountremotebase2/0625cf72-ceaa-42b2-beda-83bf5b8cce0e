from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "MSFT", "SMH", "QQQM", "PLTR", "NVDA"]
        self.short_window = 20
        self.long_window = 50

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1day"

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            short_ma = SMA(ticker, data["ohlcv"], self.short_window)
            long_ma = SMA(ticker, data["ohlcv"], self.long_window)
            
            # Ensure we have enough data points to calculate both MAs
            if short_ma is not None and long_ma is not None and len(short_ma) > 0 and len(long_ma) > 0:
                current_short_ma = short_ma[-1]
                current_long_ma = long_ma[-1]
                previous_short_ma = short_ma[-2] if len(short_ma) > 1 else current_short_ma
                previous_long_ma = long_ma[-2] if len(long_ma) > 1 else current_long_ma
                
                # Buy signal: SMA crosses above LMA
                if current_short_ma > current_long_ma and previous_short_ma <= previous_long_ma:
                    allocation_dict[ticker] = 1.0 / len(self.tickers)
                # Sell signal or avoid buying: SMA crosses below LMA or never crossed above
                else:
                    allocation_dict[ticker] = 0
            else:
                allocation_dict[ticker] = 0
        
        return TargetAllocation(allocation_dict)