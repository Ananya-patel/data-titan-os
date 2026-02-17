from pathlib import Path

from src.ingestion.equities_ingestor import EquitiesIngestor
from src.ingestion.macro_ingestor import MacroIngestor
from src.silver.equities_silver import EquitiesSilverProcessor
from src.silver.macro_silver import MacroSilverProcessor


if __name__ == "__main__":
    equities = EquitiesIngestor(ticker="AAPL")
    equities.run()

    macro = MacroIngestor(indicator="DFF")
    macro.run()

    # ---- Silver Layer (Equities) ----
    bronze_file = max(
        Path("data/bronze/equities").rglob("raw_data.csv"),
        key=lambda p: p.stat().st_mtime,
    )

    silver = EquitiesSilverProcessor(bronze_file)
    silver_path = silver.run()

    print(f"[SILVER] Validated data written to {silver_path}")
    # ---- Silver Layer (Macro) ----
    macro_bronze_file = max(
    Path("data/bronze/macro").rglob("raw_data.csv"),
    key=lambda p: p.stat().st_mtime,
)

    macro_silver = MacroSilverProcessor(macro_bronze_file)
    macro_silver_path = macro_silver.run()

    print(f"[SILVER] Macro validated data written to {macro_silver_path}")
    from src.features.equities_features import EquitiesFeatureFactory

# ---- Feature Factory (Equities) ----
silver_equities_file = max(
    Path("data/silver/equities").rglob("validated.parquet"),
    key=lambda p: p.stat().st_mtime,
)

features = EquitiesFeatureFactory(silver_equities_file)
feature_path = features.run()

print(f"[FEATURES] Equities features written to {feature_path}")
from src.signals.equities_signals import EquitiesSignalEngine

# ---- Signal Engine (Equities) ----
feature_file = max(
    Path("data/features/equities").rglob("features.parquet"),
    key=lambda p: p.stat().st_mtime,
)

signals = EquitiesSignalEngine(feature_file)
signal_path = signals.run()

print(f"[SIGNALS] Equities signals written to {signal_path}")
from src.backtest.equities_backtest import EquitiesBacktester

# ---- Backtesting Engine (Equities) ----
signal_file = max(
    Path("data/signals/equities").rglob("signals.parquet"),
    key=lambda p: p.stat().st_mtime,
)

backtester = EquitiesBacktester(signal_file)
gold_path = backtester.run()

print(f"[GOLD] Backtest results written to {gold_path}")



