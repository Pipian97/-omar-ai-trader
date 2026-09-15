import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import CONFIG
from market_data import fetch_bars
from indicators import add_indicators
from strategy import score_latest
from backtest import run_backtest
from risk import position_size
from broker import get_clients, submit_paper_bracket
from scanner import scan_market

st.set_page_config(
    page_title="OMAR AI TRADER".             
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- CUSTOM STYLE ----------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #0b0f17 0%, #0f1722 100%);
        color: #f8fafc;
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    h1, h2, h3 {
        color: #f8fafc;
    }

    [data-testid="stMetric"] {
        background: #121926; 
        border: 1px solid rgba(255,255,255,0.07);
        padding: 18px;
        border-radius: 18px;
    }

    [data-testid="stMetricLabel"] {
      color: #94a3b8;
    }

    .paper-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(34,197,94,0.12);
        color: #22c55e;
        border: 1px solid rgba(34,197,94,0.35);
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 0.7rem;
    }

    .hero-title {

        font-size: 2.2rem;

        font-weight: 800;

        margin: 0;

        line-height: 1.1;

    }

    .hero-subtitle {
        color: #94a3b8;
        margin-top: 6px;
        margin-bottom: 18px;
    }

    .trade-card {
        background: #121926;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 18px;
        margin-top: 14px;
        margin-bottom: 14px;
     }

    .section-label {
        color: #94a3b8;
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
     }

    .signal-buy {
        color: #22c55e;
        font-weight: 800;
    }

    .signal-none {
        color: #94a3b8;
        font-weight: 800;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        overflow: hidden;
    }

    .stButton > button {
        width: 100%;
        border-radius: 12p;
        min-height: 48px;
        font-weight: 700;
    }

    @media (max-width: 768px) {
        .block-container {
               padding-left: 1rem;
               padding-right: 1rem;
    }

        .hero-title {
            font-size: 1.8rem;
        }

    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- HEADER ----------
st.markdown('<div class="paper-badge">● PAPER MODE</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">📈 OMAR AI TRADER</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">AI-assisted paper-trading terminal</div>',
    unsafe_allow_html=True,
)

# ---------- ACCOUNT ----------

trading_client, _ = get_clients()
account = trading_client.get_account()
account_equity = float(account.equity)

with st.sidebar:
    st.header("Controls")
    symbol = st.selectbox("Symbol", CONFIG.watchlist)
    threshold = st.slider(

        "Signal threshold",

        0.50,

        0.95,

        CONFIG.confidence_threshold,

        0.01,

    )

    st.info("Live money is disabled. Paper trading only.")

# ---------- DATA ----------

try:

    df = fetch_bars(

        symbol,

        CONFIG.timeframe_minutes,

        CONFIG.lookback_days,

    )

except Exception as e:

    st.error(f"Data connection error: {e}")

    st.stop()

if df.empty:

    st.warning("No market data returned.")

    st.stop()

feat = add_indicators(df)

sig = score_latest(

    symbol,

    feat,

    threshold,

    CONFIG.reward_risk,

    CONFIG.atr_stop_multiple,

)

# ---------- TOP METRICS ----------

m1, m2, m3, m4 = st.columns(4)

m1.metric(

    "Paper Equity",

    f"${account_equity:,.2f}",

)

m2.metric(

    "Symbol",

    sig.symbol,

)

m3.metric(

    "Signal",

    sig.action,

)

m4.metric(

    "Confidence",

    f"{sig.confidence:.1%}",

)

# ---------- PRICE ACTION ----------

st.markdown("## Price Action")

tail = feat.tail(120).copy()

fig = make_subplots(

    rows=2,

    cols=1,

    shared_xaxes=True,

    vertical_spacing=0.03,

    row_heights=[0.78, 0.22],

)

fig.add_trace(

    go.Candlestick(

        x=tail.index,

        open=tail["open"],

        high=tail["high"],

        low=tail["low"],

        close=tail["close"],

        name="Price",

        increasing_line_color="#22c55e",

        decreasing_line_color="#ef4444",

        increasing_fillcolor="#22c55e",

        decreasing_fillcolor="#ef4444",

        showlegend=False,

    ),

    row=1,

    col=1,

)

fig.add_trace(

    go.Scatter(

        x=tail.index,

        y=tail["ema9"],

        mode="lines",

        name="EMA 9",

        line=dict(color="#60a5fa", width=2),

    ),

    row=1,

    col=1,

)

fig.add_trace(

    go.Scatter(

        x=tail.index,

        y=tail["ema20"],

        mode="lines",

        name="EMA 20",

        line=dict(color="#f59e0b", width=2),

    ),

    row=1,

    col=1,

)

fig.add_trace(

    go.Scatter(

        x=tail.index,

        y=tail["ema50"],

        mode="lines",

        name="EMA 50",

        line=dict(color="#f472b6", width=2),

    ),

    row=1,

    col=1,

)

volume_colors = [

    "#22c55e" if close >= open_ else "#ef4444"

    for open_, close in zip(tail["open"], tail["close"])

]

fig.add_trace(

    go.Bar(

        x=tail.index,

        y=tail["volume"],

        marker_color=volume_colors,

        opacity=0.45,

        showlegend=False,

        name="Volume",

    ),

    row=2,

    col=1,

)

last_price = float(tail["close"].iloc[-1])

fig.add_hline(

    y=last_price,

    line_dash="dot",

    line_color="#a78bfa",

    line_width=1,

    row=1,

    col=1,

)

fig.update_layout(

    template="plotly_dark",

    height=680,

    margin=dict(l=10, r=10, t=20, b=10),

    paper_bgcolor="#0f1722",

    plot_bgcolor="#0f1722",

    font=dict(color="#e2e8f0"),

    hovermode="x unified",

    legend=dict(

        orientation="h",

        yanchor="bottom",

        y=1.02,

        xanchor="left",

        x=0,

    ),

)

fig.update_xaxes(

    showgrid=False,

    rangeslider_visible=False,

    zeroline=False,

)

fig.update_yaxes(

    showgrid=True,

    gridcolor="rgba(255,255,255,0.06)",

    zeroline=False,

    side="right",

)

st.plotly_chart(fig, use_container_width=True)

# ---------- TRADE SETUP ----------

st.markdown("## Trade Setup")

if sig.stop:

    qty = position_size(

        account_equity,

        sig.price,

        sig.stop,

        CONFIG.risk_per_trade_pct,

    )

else:

    qty = 0

t1, t2, t3, t4 = st.columns(4)

t1.metric("Entry", f"${sig.price:,.2f}")

if sig.stop:

    t2.metric("Stop", f"${sig.stop:,.2f}")

else:

    t2.metric("Stop", "—")

if sig.target:

    t3.metric("Target", f"${sig.target:,.2f}")

else:

    t3.metric("Target", "—")

t4.metric("Qty", qty)

st.caption("Why: " + " • ".join(sig.reasons))

# ---------- MARKET SCANNER ----------

st.divider()

st.markdown("## 🔎 Market Scanner")

with st.spinner("Scanning market..."):

    scan_results = scan_market()

scanner_rows = []

for result in scan_results:

    if (

        hasattr(result, "symbol")

        and result.action in ("BUY", "SELL")

        and result.confidence >= threshold

    ):

        row = {

            "Symbol": result.symbol,

            "Signal": result.action,

            "Confidence": f"{result.confidence:.1%}",

            "Price": f"${result.price:,.2f}",

            "Entry": f"${result.price:,.2f}",

            "Stop": f"${result.stop:,.2f}" if result.stop else "—",

            "Target": f"${result.target:,.2f}" if result.target else "—",

            "Size": (

                position_size(

                    account_equity,

                    result.price,

                    result.stop,

                    CONFIG.risk_per_trade_pct,

                )

                if result.stop

                else 0

            ),

        }

        scanner_rows.append(row)

if scanner_rows:

    st.dataframe(

        pd.DataFrame(scanner_rows),

        use_container_width=True,

        hide_index=True,

    )

else:

    st.info("No qualifying scanner results right now.")

# ---------- MANUAL PAPER TRADE ----------

top_trade = next(

    (

        r

        for r in scan_results

        if hasattr(r, "symbol")

        and r.action == "BUY"

        and r.confidence >= threshold

        and r.stop

        and r.target

    ),

    None,

)

if top_trade:

    top_qty = position_size(

        account_equity,

        top_trade.price,

        top_trade.stop,

        CONFIG.risk_per_trade_pct,

    )

    st.divider()

    st.markdown("## 🧪 Manual Paper Trade")

    st.markdown(

        f"""

        <div class="trade-card">

            <div class="section-label">Top opportunity</div>

            <div style="font-size:1.25rem;font-weight:800;">

                {top_trade.symbol} · BUY · {top_trade.confidence:.1%}

            </div>

            <div style="margin-top:10px;color:#cbd5e1;">

                Entry ${top_trade.price:,.2f}

                &nbsp; · &nbsp;

                Stop ${top_trade.stop:,.2f}

                &nbsp; · &nbsp;

                Target ${top_trade.target:,.2f}

                &nbsp; · &nbsp;

                Qty {top_qty}

            </div>

        </div>

        """,

        unsafe_allow_html=True,

    )

    confirm_trade = st.checkbox(

        f"I confirm this PAPER trade for {top_trade.symbol}"

    )

    if confirm_trade and st.button(

        f"Send PAPER BUY for {top_trade.symbol}"

    ):

        try:

            order = submit_paper_bracket(

                top_trade.symbol,

                top_qty,

                top_trade.stop,

                top_trade.target,

            )

            if order:

                st.success("Paper order submitted.")

            else:

                st.warning("Paper order was not submitted.")

        except Exception as e:

            st.error(f"Paper order error: {e}")

# ---------- BACKTEST ----------

st.divider()

st.markdown("## Backtest")

bt = run_backtest(

    df,

    threshold,

    CONFIG.reward_risk,

    CONFIG.atr_stop_multiple,

)

b1, b2, b3, b4 = st.columns(4)

b1.metric("Trades", bt.trades)

b2.metric("Win rate", f"{bt.win_rate:.1%}")

b3.metric("Return", f"{bt.total_return:.1%}")

b4.metric("Max drawdown", f"{bt.max_drawdown:.1%}")

st.write(

    "Profit factor:",

    "∞" if bt.profit_factor == float("inf") else f"{bt.profit_factor:.2f}",

)

if len(bt.equity_curve):

    st.line_chart(bt.equity_curve)

st.warning(

    "Backtests can overstate results. They do not fully reproduce "

    "slippage, queue priority, latency, partial fills, changing market "

    "regimes, or future performance."

)
