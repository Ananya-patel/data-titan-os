from pathlib import Path

from src.ingestion.equities_ingestor import EquitiesIngestor
from src.ingestion.macro_ingestor import MacroIngestor
from src.silver.equities_silver import EquitiesSilverProcessor
from src.silver.macro_silver import MacroSilverProcessor
from src.features.equities_features import EquitiesFeatureFactory
from src.signals.equities_signals import EquitiesSignalEngine
from src.backtest.equities_backtest import EquitiesBacktester


if __name__ == "__main__":

    # ---- Bronze: Equities ----
    try:
        equities = EquitiesIngestor("AAPL")
        equities.run()
    except Exception as e:
        print(f"[PIPELINE HALT] Equities ingestion failed: {e}")
        raise

    # ---- Bronze: Macro ----
    macro = MacroIngestor(indicator="DFF")
    macro.run()

    # ---- Silver: Equities ----
    bronze_equities_file = max(
        Path("data/bronze/equities").rglob("raw_data.csv"),
        key=lambda p: p.stat().st_mtime,
    )

    equities_silver = EquitiesSilverProcessor(bronze_equities_file)
    silver_equities_path = equities_silver.run()
    print(f"[SILVER] Equities validated → {silver_equities_path}")

    # ---- Silver: Macro ----
    bronze_macro_file = max(
        Path("data/bronze/macro").rglob("raw_data.csv"),
        key=lambda p: p.stat().st_mtime,
    )

    macro_silver = MacroSilverProcessor(bronze_macro_file)
    silver_macro_path = macro_silver.run()
    print(f"[SILVER] Macro validated → {silver_macro_path}")

    # ---- Features ----
    features = EquitiesFeatureFactory(silver_equities_path)
    features_path = features.run()
    print(f"[FEATURES] Written → {features_path}")

    # ---- Signals ----
    signals = EquitiesSignalEngine(features_path)
    signals_path = signals.run()
    print(f"[SIGNALS] Written → {signals_path}")

    # ---- Backtest (Gold) ----
    backtester = EquitiesBacktester(signals_path)
    gold_path = backtester.run()
    print(f"[GOLD] Backtest results → {gold_path}")
