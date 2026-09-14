from config import CONFIG
from market_data import fetch_bars
from indicators import add_indicators
from strategy import score_latest

def scan_market(symbols=None):
    symbols = symbols or CONFIG.watchlist
    out = []
    for symbol in symbols:
        try:
            df = fetch_bars(symbol, CONFIG.timeframe_minutes, CONFIG.lookback_days)
            if df.empty:
                continue
            feat = add_indicators(df)
            sig = score_latest(
                symbol, feat, CONFIG.confidence_threshold,
                CONFIG.reward_risk, CONFIG.atr_stop_multiple
            )
            out.append(sig)
        except Exception as e:
            out.append({"symbol": symbol, "error": str(e)})
    return out

if __name__ == "__main__":
    for x in scan_market():
        print(x)
