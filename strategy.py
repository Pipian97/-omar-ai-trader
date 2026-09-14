from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass
class Signal:
    symbol: str
    action: str
    confidence: float
    price: float
    stop: float | None
    target: float | None
    reasons: list[str]

def score_latest(symbol: str, df: pd.DataFrame, threshold: float = 0.68,
                 reward_risk: float = 2.0, atr_stop_multiple: float = 1.5) -> Signal:
    if len(df) < 55:
        return Signal(symbol, "NO TRADE", 0.0, float(df["close"].iloc[-1]), None, None,
                      ["Insufficient history"])

    r = df.iloc[-1]
    score = 0.50
    reasons = []

    if r["ema9"] > r["ema20"] > r["ema50"]:
        score += 0.14
        reasons.append("EMA trend bullish")
    elif r["ema9"] < r["ema20"] < r["ema50"]:
        score -= 0.14
        reasons.append("EMA trend bearish")

    if 52 <= r["rsi14"] <= 68:
        score += 0.08
        reasons.append("RSI supports momentum")
    elif r["rsi14"] >= 78:
        score -= 0.08
        reasons.append("RSI overextended")

    if r["vol_ratio"] >= 1.35:
        score += 0.07
        reasons.append("Volume expansion")

    if r["return_3"] > 0 and r["return_12"] > 0:
        score += 0.07
        reasons.append("Multi-window momentum positive")
    elif r["return_3"] < 0 and r["return_12"] < 0:
        score -= 0.07
        reasons.append("Multi-window momentum negative")

    if r["breakout_up"] == 1:
        score += 0.10
        reasons.append("20-bar breakout")
    if r["breakout_down"] == 1:
        score -= 0.10
        reasons.append("20-bar breakdown")

    score = float(np.clip(score, 0.0, 1.0))
    price = float(r["close"])
    atr = float(r["atr14"]) if pd.notna(r["atr14"]) else price * 0.01

    if score >= threshold:
        stop = price - atr_stop_multiple * atr
        risk = price - stop
        target = price + reward_risk * risk
        return Signal(symbol, "BUY", score, price, stop, target, reasons)

    return Signal(symbol, "NO TRADE", score, price, None, None, reasons or ["No edge detected"])
