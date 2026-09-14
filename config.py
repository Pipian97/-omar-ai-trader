from dataclasses import dataclass, field

@dataclass
class TradingConfig:
    watchlist: list[str] = field(default_factory=lambda: [
        "SPY","QQQ","AAPL","MSFT","NVDA","AMD","META","AMZN","GOOGL","TSLA"
    ])
    timeframe_minutes: int = 5
    lookback_days: int = 30
    risk_per_trade_pct: float = 0.005
    max_daily_loss_pct: float = 0.015
    max_positions: int = 3
    confidence_threshold: float = 0.68
    reward_risk: float = 2.0
    atr_stop_multiple: float = 1.5
    allow_shorting: bool = False
    paper_only: bool = True

CONFIG = TradingConfig()
