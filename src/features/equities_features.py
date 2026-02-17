import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

from src.event_bus.event_dispatcher import EventDispatcher


class EquitiesFeatureFactory:
    def __init__(self, silver_path: Path):
        self.silver_path = silver_path

    def load(self) -> pd.DataFrame:
        df = pd.read_parquet(self.silver_path)
        df = df.sort_values("Date").reset_index(drop=True)
        return df

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        # ---- Returns ----
        df["return_1d"] = df["Adj Close"].pct_change()

        # ---- Volatility ----
        df["vol_20d"] = df["return_1d"].rolling(20).std()
        df["vol_60d"] = df["return_1d"].rolling(60).std()

        # ---- CAGR (rolling) ----
        df["cagr_60d"] = (
            (df["Adj Close"] / df["Adj Close"].shift(60)) ** (252 / 60) - 1
        )

        # ---- Sharpe (rolling, rf = 0) ----
        df["sharpe_60d"] = (
            df["return_1d"].rolling(60).mean()
            / df["return_1d"].rolling(60).std()
        ) * np.sqrt(252)

        # ---- Volatility Regime ----
        df["vol_regime"] = pd.qcut(
            df["vol_60d"],
            q=3,
            labels=["LOW", "MEDIUM", "HIGH"],
        )

        return df.dropna().reset_index(drop=True)

    def write(self, df: pd.DataFrame) -> Path:
        date_str = datetime.utcnow().date().isoformat()
        feature_path = Path("data") / "features" / "equities" / date_str
        feature_path.mkdir(parents=True, exist_ok=True)

        out_file = feature_path / "features.parquet"
        df.to_parquet(out_file, index=False)

        return out_file

    def run(self) -> Path:
        df = self.load()
        df_feat = self.build_features(df)
        feature_path = self.write(df_feat)

        EventDispatcher.emit(
            event_type="FEATURES_READY",
            payload={
                "domain": "equities",
                "feature_path": str(feature_path),
                "row_count": len(df_feat),
            },
        )

        return feature_path
