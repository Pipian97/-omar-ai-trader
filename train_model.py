"""
Optional ML experiment.
This does NOT magically predict markets; it estimates next-bar directional probability
from engineered features. Use only out-of-sample / walk-forward evaluation.
"""
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from indicators import add_indicators

FEATURES = ["rsi14","atr14","vol_ratio","return_1","return_3","return_12","breakout_up","breakout_down"]

def train_walk_forward(df: pd.DataFrame):
    x = add_indicators(df).dropna().copy()
    x["target"] = (x["close"].shift(-3) > x["close"]).astype(int)
    x = x.iloc[:-3]

    split = int(len(x) * 0.75)
    train, test = x.iloc[:split], x.iloc[split:]
    model = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=150)
    model.fit(train[FEATURES], train["target"])
    p = model.predict_proba(test[FEATURES])[:, 1]
    auc = roc_auc_score(test["target"], p) if test["target"].nunique() > 1 else float("nan")
    return model, auc, test.assign(prob_up=p)
