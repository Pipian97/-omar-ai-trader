"""
One-shot paper trading script.
It scans configured symbols and submits at most one BUY bracket order, only in Alpaca paper mode.
Run manually until you have validated the strategy.
"""
from config import CONFIG
from broker import get_clients, submit_paper_bracket
from market_data import fetch_bars
from indicators import add_indicators
from strategy import score_latest
from risk import position_size, daily_loss_guard

def main():
    trading, _ = get_clients()
    account = trading.get_account()
    equity = float(account.equity)
    last_equity = float(account.last_equity)

    if not daily_loss_guard(last_equity, equity, CONFIG.max_daily_loss_pct):
        print("KILL SWITCH: daily loss limit reached.")
        return

    if len(trading.get_all_positions()) >= CONFIG.max_positions:
        print("Max positions reached.")
        return

    candidates = []
    for symbol in CONFIG.watchlist:
        df = fetch_bars(symbol, CONFIG.timeframe_minutes, CONFIG.lookback_days)
        if df.empty:
            continue
        sig = score_latest(symbol, add_indicators(df), CONFIG.confidence_threshold,
                           CONFIG.reward_risk, CONFIG.atr_stop_multiple)
        if sig.action == "BUY":
            candidates.append(sig)

    if not candidates:
        print("No valid trade.")
        return

    best = max(candidates, key=lambda s: s.confidence)
    qty = position_size(equity, best.price, best.stop, CONFIG.risk_per_trade_pct)
    if qty <= 0:
        print("Risk manager rejected position size.")
        return

    order = submit_paper_bracket(best.symbol, qty, best.stop, best.target)
    print("PAPER ORDER SUBMITTED:", order)

if __name__ == "__main__":
    main()
