from datetime import datetime
import pandas as pd
from fredapi import Fred

from src.ingestion.base_ingestor import BaseIngestor


class MacroIngestor(BaseIngestor):
    def __init__(self, indicator: str):
        super().__init__(domain="macro", source="FRED")
        self.indicator = indicator
        self.fred = Fred()  # no API key required for public series

    def fetch(self) -> pd.DataFrame:
        series = self.fred.get_series(self.indicator)
        df = series.reset_index()
        df.columns = ["date", self.indicator]
        return df

    def run(self):
        try:
            df = self.fetch()
            storage_path = self.write_raw(df, file_ext="csv")

            self.log_run(
                data_date=datetime.utcnow().date().isoformat(),
                storage_path=storage_path,
                record_count=len(df),
                status="SUCCESS",
            )

            print(f"[SUCCESS] Ingested macro indicator {self.indicator}")

        except Exception as e:
            self.log_run(
                data_date=datetime.utcnow().date().isoformat(),
                storage_path="N/A",
                record_count=0,
                status="FAILED",
                error_message=str(e),
            )
            raise
