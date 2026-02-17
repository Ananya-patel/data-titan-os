import pandas as pd
from pathlib import Path
from datetime import datetime

from src.event_bus.event_dispatcher import EventDispatcher


class EquitiesSignalEngine:
    def __init__(self, feature_path: Path):
        self.feature_path = feature_path

    def load(self) -> pd.DataFrame:
        df = pd.read_parquet(self.feature_path)
        return df.sort_values("Date").reset_index(drop=True)

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df["signal"] = "HOLD"

        buy_mask = (
            (df["sharpe_60d"] > 1)
            & (df["cagr_60d"] > 0)
            & (df["vol_regime"] == "LOW")
        )

        sell_mask = (
            (df["sharpe_60d"] < 0)
            | (df["vol_regime"] == "HIGH")
        )

        df.loc[buy_mask, "signal"] = "BUY"
        df.loc[sell_mask, "signal"] = "SELL"

        return df

    def write(self, df: pd.DataFrame) -> Path:
        date_str = datetime.utcnow().date().isoformat()
        signal_path = Path("data") / "signals" / "equities" / date_str
        signal_path.mkdir(parents=True, exist_ok=True)

        out_file = signal_path / "signals.parquet"
        df.to_parquet(out_file, index=False)

        return out_file

    def run(self) -> Path:
        df = self.load()
        df_signals = self.generate_signals(df)
        signal_path = self.write(df_signals)

        EventDispatcher.emit(
            event_type="SIGNALS_READY",
            payload={
                "domain": "equities",
                "signal_path": str(signal_path),
                "row_count": len(df_signals),
            },
        )

        return signal_path
