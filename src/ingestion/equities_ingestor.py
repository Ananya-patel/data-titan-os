import yfinance as yf
import pandas as pd
from datetime import datetime

from src.ingestion.base_ingestor import BaseIngestor





class EquitiesIngestor(BaseIngestor):
    def __init__(self, ticker: str):
        super().__init__(domain="equities", source="yfinance")
        self.ticker = ticker

    def fetch(self) -> pd.DataFrame:
        df = yf.download(self.ticker, period="1y", auto_adjust=False)
        df.reset_index(inplace=True)
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

            print(f"[SUCCESS] Ingested {len(df)} rows for {self.ticker}")

        except Exception as e:
            self.log_run(
                data_date=datetime.utcnow().date().isoformat(),
                storage_path="N/A",
                record_count=0,
                status="FAILED",
                error_message=str(e),
            )
            raise
