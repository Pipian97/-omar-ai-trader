import math

def position_size(equity: float, entry: float, stop: float,
                  risk_per_trade_pct: float, max_notional_pct: float = 0.25) -> int:
    if equity <= 0 or entry <= 0 or stop >= entry:
        return 0
    risk_dollars = equity * risk_per_trade_pct
    risk_per_share = entry - stop
    qty_by_risk = math.floor(risk_dollars / risk_per_share)
    qty_by_notional = math.floor((equity * max_notional_pct) / entry)
    return max(0, min(qty_by_risk, qty_by_notional))

def daily_loss_guard(starting_equity: float, current_equity: float, max_daily_loss_pct: float) -> bool:
    if starting_equity <= 0:
        return False
    loss_pct = (starting_equity - current_equity) / starting_equity
    return loss_pct < max_daily_loss_pct
