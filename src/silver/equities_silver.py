import pandas as pd
from pathlib import Path
from datetime import datetime

from src.validation.equities_schema import EquitiesSchema
from src.event_bus.event_dispatcher import EventDispatcher


class EquitiesSilverProcessor:
    def __init__(self, bronze_path: Path):
        self.bronze_path = bronze_path

    def load(self) -> pd.DataFrame:
        """
        Load raw equities data from the Bronze layer and perform
        explicit, minimal cleanup required for schema validation.
        """
        df = pd.read_csv(self.bronze_path, parse_dates=["Date"])

        # ---- Timestamp cleanup ----
        initial_rows = len(df)
        df = df.dropna(subset=["Date"])
        dropped_dates = initial_rows - len(df)

        if dropped_dates > 0:
            print(f"[SILVER] Dropped {dropped_dates} rows with invalid Date")

        # ---- Explicit numeric coercion ----
        numeric_cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Drop rows with invalid numeric values
        rows_before_numeric = len(df)
        df = df.dropna(subset=numeric_cols)
        dropped_numeric = rows_before_numeric - len(df)

        if dropped_numeric > 0:
            print(f"[SILVER] Dropped {dropped_numeric} rows with invalid numeric values")

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
        silver_path = Path("data") / "silver" / "equities" / date_str
        silver_path.mkdir(parents=True, exist_ok=True)

        out_file = silver_path / "validated.parquet"
        df.to_parquet(out_file, index=False)

        return out_file

    def run(self) -> Path:
        """
        Execute the full Bronze → Silver pipeline for equities data
        and emit a DATA_VALIDATED event on success.
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
