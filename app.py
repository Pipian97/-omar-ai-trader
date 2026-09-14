import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from config import CONFIG
from market_data import fetch_bars
from indicators import add_indicators
from strategy import score_latest
from backtest import run_backtest
from risk import position_size  
from broker import get_clients, submit_paper_bracket
from scanner import scan_market

st.set_page_config(page_title="OMAR AI TRADER", layout="wide")
st.title("OMAR AI TRADER")
st.caption("Paper-trading research terminal — no profit guarantees")
trading_client, _ = get_clients()
account_equity = float(trading_client.get_account().equity)
st.metric("Paper account equity ($)", f"${account_equity:,.2f}")
with st.sidebar:
    symbol = st.selectbox("Symbol", CONFIG.watchlist)
    threshold = st.slider("Signal threshold", 0.50, 0.90, CONFIG.confidence_threshold, 0.01)
    st.info("LIVE MONEY IS DISABLED IN THIS STARTER VERSION.")
try:
    df = fetch_bars(symbol, CONFIG.timeframe_minutes, CONFIG.lookback_days)
except Exception as e:
    st.error(f"Data connection error: {e}")
    st.stop()

if df.empty:
    st.warning("No market data returned.")
    st.stop()

feat = add_indicators(df)
sig = score_latest(symbol, feat, threshold, CONFIG.reward_risk, CONFIG.atr_stop_multiple)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Symbol", sig.symbol)
c2.metric("Signal", sig.action)
c3.metric("Confidence", f"{sig.confidence:.1%}")
c4.metric("Last price", f"${sig.price:,.2f}")

if sig.stop:
    qty = position_size(account_equity, sig.price, sig.stop, CONFIG.risk_per_trade_pct)
    st.write(f"**Suggested paper size:** {qty} shares")
    st.write(f"**Stop:** ${sig.stop:,.2f}  |  **Target:** ${sig.target:,.2f}")

st.write("**Why:**", " • ".join(sig.reasons))

fig = go.Figure()
tail = feat.tail(150)
fig.add_trace(go.Candlestick(
    x=tail.index, open=tail["open"], high=tail["high"], low=tail["low"], close=tail["close"], name="Price"
))
fig.add_trace(go.Scatter(x=tail.index, y=tail["ema9"], name="EMA 9"))
fig.add_trace(go.Scatter(x=tail.index, y=tail["ema20"], name="EMA 20"))
fig.add_trace(go.Scatter(x=tail.index, y=tail["ema50"], name="EMA 50"))
fig.update_layout(height=550, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Backtest")
bt = run_backtest(df, threshold, CONFIG.reward_risk, CONFIG.atr_stop_multiple)
b1, b2, b3, b4 = st.columns(4)
b1.metric("Trades", bt.trades)
b2.metric("Win rate", f"{bt.win_rate:.1%}")
b3.metric("Return", f"{bt.total_return:.1%}")
b4.metric("Max drawdown", f"{bt.max_drawdown:.1%}")
st.write("Profit factor:", "∞" if bt.profit_factor == float("inf") else f"{bt.profit_factor:.2f}")
if len(bt.equity_curve):
    st.line_chart(bt.equity_curve)

st.warning(
    "Backtests can overstate results. They do not fully reproduce slippage, queue priority, "
    "latency, partial fills, changing market regimes, or future performance."
)
st.divider()
st.subheader("🔎 Market Scanner")

with st.spinner("Scanning market..."):
    scan_results = scan_market()

scanner_rows = []
for result in scan_results:          
    if (
        hasattr(result, "symbol")
        and result.action in ("BUY", "SELL")
        and result.confidence >= threshold
    ):
        scanner_rows.append({         
            "Symbol": result.symbol,
            "Signal": result.action,
            "Confidence": f"{result.confidence:.1%}",
            "Price": f"${result.price:,.2f}",
            "Entry": f"${result.price:,.2f}",
            "Stop": f"${result.stop:,.2f}" if result.stop else "—",
            "Target": f"${result.target:,.2f}" if result.target else "—",
            "Size": position_size(account_equity, result.price, result.stop, CONFIG.risk_per_trade_pct) if result.stop else 0,
        })
if scanner_rows:
    st.dataframe(pd.DataFrame(scanner_rows), hide_index=True)
else:
    st.info("No scanner results available.")

