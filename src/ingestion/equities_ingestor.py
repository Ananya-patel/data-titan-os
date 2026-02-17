import yfinance as yf
import pandas as pd
from datetime import datetime

from src.ingestion.base_ingestor import BaseIngestor


class EquitiesIngestor(BaseIngestor):
    def __init__(self, ticker: str):
        super().__init__(domain="equities", source="yfinance")
        self.ticker = ticker

    def fetch(self) -> pd.DataFrame:
        """
        Fetch equities data with a resilient fallback strategy.
        Primary: Yahoo Finance
        Fallback: Stooq
        """

        try:
            df = yf.download(
                self.ticker,
                period="1y",
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=False,
            )

            if df is None or df.empty:
                raise ValueError("Yahoo returned empty dataframe")

            df = df.reset_index()

        except Exception as yahoo_error:
            print(f"[WARN] Yahoo failed for {self.ticker}: {yahoo_error}")
            print("[FALLBACK] Using Stooq data source")

            import pandas_datareader.data as web

            df = web.DataReader(
                self.ticker,
                data_source="stooq",
                start="2023-01-01",
            ).reset_index()

        # ---- Hard contract checks ----
        if "Date" not in df.columns:
            raise RuntimeError(
                f"[INGESTION FAILED] Missing Date column for {self.ticker}"
            )

        df["Ticker"] = self.ticker
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
