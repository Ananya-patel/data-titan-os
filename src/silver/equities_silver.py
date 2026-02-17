import pandas as pd
from pathlib import Path
from datetime import datetime

from src.validation.equities_schema import EquitiesSchema
from src.event_bus.event_dispatcher import EventDispatcher


class EquitiesSilverProcessor:
    def __init__(self, bronze_path: Path):
        self.bronze_path = bronze_path

    def load(self) -> pd.DataFrame:
        df = pd.read_csv(self.bronze_path)

        # ---- Date coercion ----
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        invalid_dates = df["Date"].isna().sum()

        if invalid_dates > 0:
            print(f"[SILVER] Dropped {invalid_dates} rows with invalid Date")
            df = df.dropna(subset=["Date"])

        # ---- Schema normalization ----
        if "Adj Close" not in df.columns:
            print("[SILVER] 'Adj Close' missing — defaulting to Close")
            df["Adj Close"] = df["Close"]

        # ---- Numeric coercion ----
        numeric_cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        before = len(df)
        df = df.dropna(subset=numeric_cols)
        dropped = before - len(df)

        if dropped > 0:
            print(f"[SILVER] Dropped {dropped} rows with invalid numeric values")

        return df

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enforce the equities schema. Any violation raises a hard failure.
        """
        return EquitiesSchema.validate(df)

    def write(self, df: pd.DataFrame) -> Path:
        """
        Write validated equities data to the Silver layer in Parquet format.
        """
        date_str = datetime.utcnow().date().isoformat()
        out_dir = Path("data") / "silver" / "equities" / date_str
        out_dir.mkdir(parents=True, exist_ok=True)

        out_file = out_dir / "validated.parquet"
        df.to_parquet(out_file, index=False)

        return out_file

    def run(self) -> Path:
        """
        Execute the full Bronze → Silver pipeline and emit DATA_VALIDATED.
        """
        df = self.load()
        df_valid = self.validate(df)
        silver_path = self.write(df_valid)

        EventDispatcher.emit(
            event_type="DATA_VALIDATED",
            payload={
                "domain": "equities",
                "silver_path": str(silver_path),
                "row_count": len(df_valid),
            },
        )

        return silver_path
