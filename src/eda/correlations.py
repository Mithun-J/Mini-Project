# src/eda/correlations.py
# Member 3: Jayakrishnan KV (Feature Engineer & Correlation Analyst)
# DSA Life Cycle — Phase 3: Bivariate Distributions & Feature Correlation Analysis

from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEAN_PATH = PROJECT_ROOT / "output" / "preprocessed_data.csv"


def load_dataset() -> pd.DataFrame:
    """Loads the preprocessed dataset for correlation analysis."""
    if not CLEAN_PATH.exists():
        raise FileNotFoundError(
            f"Preprocessed file not found at {CLEAN_PATH}. Please run pipeline.py first."
        )
    return pd.read_csv(CLEAN_PATH)


def analyze_correlations(df: pd.DataFrame) -> pd.Series:
    """
    Examines key domain relationships and distributions across segments:
      - Seasonal productivity breakdown
      - Rainfall category variance
      - Highest and lowest yielding crops
      - Pearson correlation coefficients with log_yield
    """
    print("\n" + "=" * 65)
    print("  DSA LIFE CYCLE — PHASE 3: BIVARIATE & CORRELATION ANALYSIS")
    print("  Engineer: Jayakrishnan KV (Feature Engineer & Correlation Analyst)")
    print("=" * 65)

    print("\n--- Yield by Agricultural Season ---")
    season_stats = (
        df.groupby("season")["yield"]
        .agg(Records="count", Mean="mean", Median="median", Std="std")
        .round(2)
        .sort_values(by="Mean", ascending=False)
    )
    print(season_stats.to_string())

    print("\n--- Yield by Rainfall Category ---")
    rain_stats = (
        df.groupby("rainfall_category", observed=False)["yield"]
        .agg(Records="count", Mean="mean", Median="median", Std="std")
        .round(2)
    )
    print(rain_stats.to_string())

    print("\n--- Top 5 vs Bottom 5 Crops by Mean Yield ---")
    crop_means = df.groupby("crop")["yield"].mean().sort_values(ascending=False)
    print("  * Top 5 (Capped):")
    for c, val in crop_means.head(5).items():
        print(f"      {c:<22} : {val:>10.2f}")
    print("  * Bottom 5:")
    for c, val in crop_means.tail(5).items():
        print(f"      {c:<22} : {val:>10.2f}")

    print("\n--- Pearson Correlation with log_yield ---")
    corr_cols = [
        "fertilizer_per_hectare",
        "pesticide_per_hectare",
        "annual_rainfall",
        "area",
        "production",
        "log_yield",
    ]
    corr_matrix = df[corr_cols].corr()
    log_yield_corrs = corr_matrix["log_yield"].drop("log_yield").sort_values(ascending=False).round(3)
    for col_name, val in log_yield_corrs.items():
        print(f"  * {col_name:<24} : {val:+0.3f}")

    return log_yield_corrs


if __name__ == "__main__":
    df = load_dataset()
    analyze_correlations(df)

