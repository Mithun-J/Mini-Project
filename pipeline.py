# pipeline.py
# Member 1: Mithun J (Project Lead & System Architect)
# Master ETL Orchestrator: Coordinates Extract, Clean, Features, and Load.

import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.etl.extract import extract
from src.etl.clean import clean_data
from src.etl.features import engineer_features
from src.etl.load import load


def run_etl_pipeline():
    """
    Executes the full 4-stage ETL Pipeline in sequential order:
      1. extract()           - Member 1: Mithun J (Project Lead)
      2. clean_data()        - Member 2: Azifali A
      3. engineer_features() - Member 3: Jayakrishnan KV
      4. load()              - Member 4: Sharon
    """
    print("\n" + "=" * 60)
    print("   CROP YIELD ETL PIPELINE")
    print("   Batch 7 Mini Project — DSA B13 Offline")
    print("=" * 60)

    total_start = time.perf_counter()

    try:
        # Step 1: Extract (Mithun J)
        t0 = time.perf_counter()
        raw_df = extract()
        t1 = time.perf_counter()
        extract_time = (t1 - t0) * 1000

        # Step 2: Clean (Azifali A)
        t0 = time.perf_counter()
        cleaned_df = clean_data(raw_df.copy())
        t1 = time.perf_counter()
        clean_time = (t1 - t0) * 1000

        # Step 3: Feature Engineering (Jayakrishnan KV)
        t0 = time.perf_counter()
        featured_df = engineer_features(cleaned_df)
        t1 = time.perf_counter()
        feature_time = (t1 - t0) * 1000

        # Step 4: Load & Reporting (Sharon)
        t0 = time.perf_counter()
        load(featured_df, raw_df)
        t1 = time.perf_counter()
        load_time = (t1 - t0) * 1000

        total_elapsed = (time.perf_counter() - total_start) * 1000

        # Benchmarking & Latency Summary
        print("\n" + "=" * 60)
        print("   PIPELINE BENCHMARKING & EXECUTION SUMMARY")
        print("=" * 60)
        print(f"  1. Extraction (Mithun J)          : {extract_time:>7.1f} ms")
        print(f"  2. Data Cleaning (Azifali A)      : {clean_time:>7.1f} ms")
        print(f"  3. Feature Eng. (Jayakrishnan KV) : {feature_time:>7.1f} ms")
        print(f"  4. Load & Reporting (Sharon)      : {load_time:>7.1f} ms")
        print("-" * 60)
        print(f"  Total Pipeline Latency            : {total_elapsed:>7.1f} ms")
        print("=" * 60)
        print("  ETL PIPELINE COMPLETED SUCCESSFULLY\n")

    except Exception as e:
        print(f"\n[ERROR] Pipeline execution terminated: {e}")
        raise


if __name__ == "__main__":
    run_etl_pipeline()
