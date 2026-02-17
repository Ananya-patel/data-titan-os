import pandas as pd
from pathlib import Path
from datetime import datetime

from src.validation.macro_schema import MacroSchema
from src.event_bus.event_dispatcher import EventDispatcher


class MacroSilverProcessor:
    def __init__(self, bronze_path: Path):
        self.bronze_path = bronze_path

    def load(self) -> pd.DataFrame:
        """
        Load macro data from the Bronze layer and perform
        explicit cleanup required for schema validation.
        """
        df = pd.read_csv(self.bronze_path, parse_dates=["date"])

        # Drop invalid timestamps explicitly
        initial_rows = len(df)
        df = df.dropna(subset=["date"])
        dropped = initial_rows - len(df)

        if dropped > 0:
            print(f"[SILVER] Dropped {dropped} rows with invalid date")

        # Explicit numeric coercion
        df["DFF"] = pd.to_numeric(df["DFF"], errors="coerce")

        before_numeric = len(df)
        df = df.dropna(subset=["DFF"])
        dropped_numeric = before_numeric - len(df)

        if dropped_numeric > 0:
            print(f"[SILVER] Dropped {dropped_numeric} rows with invalid DFF values")

        return df

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enforce the macro schema. Any violation raises a hard failure.
        """
        return MacroSchema.validate(df)

    def write(self, df: pd.DataFrame) -> Path:
        """
        Write validated macro data to the Silver layer in Parquet format.
        """
        date_str = datetime.utcnow().date().isoformat()
        silver_path = Path("data") / "silver" / "macro" / date_str
        silver_path.mkdir(parents=True, exist_ok=True)

        out_file = silver_path / "validated.parquet"
        df.to_parquet(out_file, index=False)

        return out_file

    def run(self) -> Path:
        """
        Execute the full Bronze → Silver pipeline for macro data
        and emit a DATA_VALIDATED event on success.
        """
        df = self.load()
        df_valid = self.validate(df)
        silver_path = self.write(df_valid)

        EventDispatcher.emit(
            event_type="DATA_VALIDATED",
            payload={
                "domain": "macro",
                "silver_path": str(silver_path),
                "row_count": len(df_valid),
            },
        )

        return silver_path
