# OMAR AI TRADER — v0.1

A paper-trading research system for U.S. equities.

## What it does
- Downloads 5-minute bars from Alpaca
- Calculates EMA, RSI, ATR, volume expansion, momentum and breakout features
- Generates BUY / NO TRADE signals with a confidence score
- Calculates position size from account risk
- Includes a daily-loss kill switch
- Includes a conservative bracket-order paper trading script
- Includes a basic historical backtest
- Includes an optional ML experiment with a gradient-boosting classifier
- Includes a Streamlit dashboard

## Important
This version is intentionally locked to **PAPER trading**. It does not guarantee profits.
Do not remove the paper-trading lock until you have evaluated out-of-sample results,
paper-trading results, slippage, and failure modes.

## Setup

### 1. Install Python 3.11+
Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

Windows:
```bash
.venv\Scripts\activate
```

macOS:
```bash
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create a free Alpaca paper account
Create paper API keys in your Alpaca account.

### 4. Add keys
Copy:
```bash
cp .env.example .env
```

Then edit `.env`:

```text
ALPACA_API_KEY=...
ALPACA_SECRET_KEY=...
ALPACA_PAPER=true
```

### 5. Run the dashboard
```bash
streamlit run app.py
```

### 6. Run scanner
```bash
python scanner.py
```

### 7. Optional one-shot PAPER order
```bash
python paper_trade_once.py
```

## Risk defaults
- 0.5% account risk per trade
- 1.5% maximum daily loss before kill switch
- Maximum 3 concurrent positions
- Minimum signal confidence: 68%
- Target: 2R
- Stop: 1.5 ATR

Change these in `config.py`.

## Before real money
Minimum recommended validation sequence:
1. Historical backtest
2. Separate out-of-sample period
3. Walk-forward testing
4. At least several weeks of paper trading
5. Review every losing trade and every software failure
6. Only then consider very small real capital

## Known limitations
- The signal score is a rules-based ensemble, not a magical AI predictor.
- The included ML model is experimental and intentionally not wired directly to orders.
- Backtesting is simplified.
- No news/sentiment filter yet.
- No portfolio-correlation engine yet.
- No option trading yet.
- No production scheduler, database, monitoring, cloud deployment or redundancy yet.
