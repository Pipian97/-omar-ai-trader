from datetime import datetime, timedelta, timezone
import pandas as pd

def fetch_bars(symbol: str, timeframe_minutes: int = 5, lookback_days: int = 30) -> pd.DataFrame:
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.enums import DataFeed
    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
    from broker import get_clients

    _, client = get_clients()
    tf = TimeFrame(timeframe_minutes, TimeFrameUnit.Minute)
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback_days)

    req = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=tf,
        start=start,
        end=end,
        limit=10000,
        feed=DataFeed.IEX,
    )
    result = client.get_stock_bars(req).df
    if result.empty:
        return pd.DataFrame()

    if isinstance(result.index, pd.MultiIndex):
        try:
            result = result.xs(symbol)
        except Exception:
            result = result.reset_index()
            result = result[result["symbol"] == symbol].set_index("timestamp")

    return result[["open","high","low","close","volume"]].copy()
