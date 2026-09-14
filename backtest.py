from dataclasses import dataclass
import pandas as pd
import numpy as np
from indicators import add_indicators

@dataclass
class BacktestResult:
    trades: int
    win_rate: float
    total_return: float
    profit_factor: float
    max_drawdown: float
    equity_curve: pd.Series

def run_backtest(df: pd.DataFrame, threshold: float = 0.68,
                 reward_risk: float = 2.0, atr_stop_multiple: float = 1.5) -> BacktestResult:
    x = add_indicators(df).dropna().copy()
    if len(x) < 60:
        return BacktestResult(0, 0, 0, 0, 0, pd.Series(dtype=float))

    equity = 1.0
    curve = []
    wins = 0
    pnl_list = []
    in_trade = False
    entry = stop = target = None

    for i in range(50, len(x)):
        r = x.iloc[i]
        if in_trade:
            # Conservative ordering: assume stop hits first if both occur in same bar.
            if r["low"] <= stop:
                pnl = (stop - entry) / entry
                equity *= (1 + pnl)
                pnl_list.append(pnl)
                in_trade = False
            elif r["high"] >= target:
                pnl = (target - entry) / entry
                equity *= (1 + pnl)
                pnl_list.append(pnl)
                wins += 1
                in_trade = False
        else:
            score = 0.50
            if r["ema9"] > r["ema20"] > r["ema50"]: score += 0.14
            if 52 <= r["rsi14"] <= 68: score += 0.08
            if r["vol_ratio"] >= 1.35: score += 0.07
            if r["return_3"] > 0 and r["return_12"] > 0: score += 0.07
            if r["breakout_up"] == 1: score += 0.10

            if score >= threshold:
                entry = float(r["close"])
                stop = entry - atr_stop_multiple * float(r["atr14"])
                target = entry + reward_risk * (entry - stop)
                in_trade = True

        curve.append(equity)

    s = pd.Series(curve)
    if len(s):
        dd = ((s / s.cummax()) - 1).min()
    else:
        dd = 0.0

    gross_profit = sum(p for p in pnl_list if p > 0)
    gross_loss = abs(sum(p for p in pnl_list if p < 0))
    pf = gross_profit / gross_loss if gross_loss > 0 else (float("inf") if gross_profit > 0 else 0)

    return BacktestResult(
        trades=len(pnl_list),
        win_rate=(wins / len(pnl_list)) if pnl_list else 0,
        total_return=equity - 1,
        profit_factor=pf,
        max_drawdown=float(dd),
        equity_curve=s
    )
