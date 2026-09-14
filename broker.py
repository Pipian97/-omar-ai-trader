import os
from dotenv import load_dotenv

load_dotenv()

def _get_secret(name: str):
    # Local .env first.
    value = os.getenv(name)
    if value:
        return value

    # Streamlit Community Cloud secrets fallback.
    try:
        import streamlit as st
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return None

def credentials_configured() -> bool:
    return bool(_get_secret("ALPACA_API_KEY") and _get_secret("ALPACA_SECRET_KEY"))

def get_clients():
    from alpaca.trading.client import TradingClient
    from alpaca.data.historical import StockHistoricalDataClient

    key = _get_secret("ALPACA_API_KEY")
    secret = _get_secret("ALPACA_SECRET_KEY")
    paper_flag = str(_get_secret("ALPACA_PAPER") or "true").lower()

    if not key or not secret:
        raise RuntimeError(
            "Alpaca paper API keys are not configured. "
            "Add ALPACA_API_KEY and ALPACA_SECRET_KEY to Streamlit Secrets."
        )

    if paper_flag != "true":
        raise RuntimeError("OMAR AI TRADER Web is locked to PAPER trading.")

    trading = TradingClient(key, secret, paper=True)
    data = StockHistoricalDataClient(key, secret)
    return trading, data

def submit_paper_bracket(symbol: str, qty: int, stop: float, target: float):
    if qty <= 0:
        return None

    from alpaca.trading.requests import (
        MarketOrderRequest, TakeProfitRequest, StopLossRequest
    )
    from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass

    trading, _ = get_clients()
    order = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
        order_class=OrderClass.BRACKET,
        take_profit=TakeProfitRequest(limit_price=round(target, 2)),
        stop_loss=StopLossRequest(stop_price=round(stop, 2)),
    )
    return trading.submit_order(order_data=order)
