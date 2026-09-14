import numpy as np
import pandas as pd

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x["ema9"] = x["close"].ewm(span=9, adjust=False).mean()
    x["ema20"] = x["close"].ewm(span=20, adjust=False).mean()
    x["ema50"] = x["close"].ewm(span=50, adjust=False).mean()

    delta = x["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    x["rsi14"] = 100 - (100 / (1 + rs))

    prev_close = x["close"].shift(1)
    tr = pd.concat([
        x["high"] - x["low"],
        (x["high"] - prev_close).abs(),
        (x["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    x["atr14"] = tr.ewm(alpha=1/14, adjust=False).mean()

    x["vol_sma20"] = x["volume"].rolling(20).mean()
    x["vol_ratio"] = x["volume"] / x["vol_sma20"].replace(0, np.nan)
    x["return_1"] = x["close"].pct_change()
    x["return_3"] = x["close"].pct_change(3)
    x["return_12"] = x["close"].pct_change(12)
    x["high20"] = x["high"].rolling(20).max().shift(1)
    x["low20"] = x["low"].rolling(20).min().shift(1)
    x["breakout_up"] = (x["close"] > x["high20"]).astype(int)
    x["breakout_down"] = (x["close"] < x["low20"]).astype(int)
    return x
