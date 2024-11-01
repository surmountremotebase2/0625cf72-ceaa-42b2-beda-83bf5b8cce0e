from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # List of tickers we are interested in (could be any cryptocurrency pairs)
        self.tickers = ["BTCUSD", "ETHUSD"]
        
        # Initialization of variables needed for the strategy
        self.data_list = []
    
    @property
    def assets(self):
        # Here, we define the assets that our strategy will involve
        return self.tickers

    @property
    def interval(self):
        # Set the interval for data collection suitable for looking for "flips" 
        # Daily intervals could be a starting point
        return "1day"

    def run(self, data):
        # This method evaluates the trading signals and decides allocation
        allocation_dict = {}
        
        for ticker in self.tickers:
            rsi_values = RSI(ticker, data["ohlcv"], 14) # 14 periods RSI
            macd_signal = MACD(ticker, data["ohlcv"], 12, 26) # Default MACD signal
            
            if rsi_values is None or macd_signal is None or len(rsi_values) < 1 or len(macd_signal["signal"]) < 1:
                continue  # Skip if there's no sufficient data
            
            # Check for buy signal - RSI below 30 is considered oversold, might indicate a good buying opportunity
            # and MACD crosses above the signal line indicating potential upward momentum
            current_rsi = rsi_values[-1]
            macd_current = macd_signal["MACD"][-1] - macd_signal["signal"][-1] # Should be positive for buy signal
            if current_rsi < 30 and macd_current > 0:
                log(f"Buying signal detected on {ticker}")
                allocation_dict[ticker] = 0.5  # Allocate 50% of portfolio weight to this asset
            
            # Check for sell signal - RSI above 70 is considered overbought, might indicate a good selling opportunity
            # and MACD crosses below the signal line indicating potential downward momentum
            elif current_rsi > 70 and macd_current < 0:
                log(f"Selling signal detected on {ticker}")
                allocation_dict[ticker] = 0  # Reduce allocation to zero to sell off this asset
        
        # Ensure our allocation does not exceed 100% in total (simple normalization)
        total_allocation = sum(allocation_dict.values())
        if total_allocation > 1:
            allocation_dict = {k: v/total_allocation for k, v in allocation_dict.items()}
        
        return TargetAllocation(allocation_dict)