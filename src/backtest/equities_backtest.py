import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

from src.event_bus.event_dispatcher import EventDispatcher


class EquitiesBacktester:
    def __init__(
        self,
        signal_path: Path,
        initial_capital: float = 1_000_000,
        txn_cost_bps: float = 10,  # 10 basis points
    ):
        self.signal_path = signal_path
        self.initial_capital = initial_capital
        self.txn_cost = txn_cost_bps / 10_000

    def load(self) -> pd.DataFrame:
        df = pd.read_parquet(self.signal_path)
        df = df.sort_values("Date").reset_index(drop=True)
        return df

    def simulate(self, df: pd.DataFrame):
        df = df.copy()

        # Position logic: long-only
        df["position"] = 0
        df.loc[df["signal"] == "BUY", "position"] = 1
        df.loc[df["signal"] == "SELL", "position"] = 0
        df["position"] = df["position"].ffill().fillna(0)

        # Trades occur when position changes
        df["trade"] = df["position"].diff().fillna(0).abs()

        # Daily returns from Adj Close
        df["market_return"] = df["Adj Close"].pct_change().fillna(0)

        # Strategy returns
        df["strategy_return"] = df["position"].shift(1).fillna(0) * df["market_return"]

        # Transaction costs
        df["txn_cost"] = df["trade"] * self.txn_cost

        # Net returns
        df["net_return"] = df["strategy_return"] - df["txn_cost"]

        # Equity curve
        df["equity"] = (
            self.initial_capital * (1 + df["net_return"]).cumprod()
        )

        return df

    def metrics(self, df: pd.DataFrame) -> dict:
        total_return = df["equity"].iloc[-1] / self.initial_capital - 1

        cagr = (1 + total_return) ** (252 / len(df)) - 1

        sharpe = (
            df["net_return"].mean() / df["net_return"].std()
        ) * np.sqrt(252)

        rolling_max = df["equity"].cummax()
        drawdown = (df["equity"] - rolling_max) / rolling_max
        max_dd = drawdown.min()

        return {
            "CAGR": cagr,
            "Sharpe": sharpe,
            "MaxDrawdown": max_dd,
        }

    def write(self, df: pd.DataFrame, metrics: dict) -> Path:
        date_str = datetime.utcnow().date().isoformat()
        gold_path = Path("data") / "gold" / "equities" / date_str
        gold_path.mkdir(parents=True, exist_ok=True)

        trades_file = gold_path / "trades.parquet"
        equity_file = gold_path / "equity_curve.parquet"

        df.to_parquet(trades_file, index=False)
        pd.DataFrame([metrics]).to_parquet(equity_file, index=False)

        return gold_path

    def run(self) -> Path:
        df = self.load()
        df_bt = self.simulate(df)
        metrics = self.metrics(df_bt)
        gold_path = self.write(df_bt, metrics)

        EventDispatcher.emit(
            event_type="BACKTEST_COMPLETE",
            payload={
                "domain": "equities",
                "gold_path": str(gold_path),
                "metrics": metrics,
            },
        )

        print("[BACKTEST] Metrics:", metrics)
        return gold_path
