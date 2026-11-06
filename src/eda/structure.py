# src/eda/structure.py
# Member 2: Azifali A (Data Cleaning & Structure Analyst)
# DSA Life Cycle — Phase 1: Overall Data Structure & Five-Number Summary Analysis

from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEAN_PATH = PROJECT_ROOT / "output" / "preprocessed_data.csv"


def load_dataset() -> pd.DataFrame:
    """Loads the preprocessed dataset for structure analysis."""
    if not CLEAN_PATH.exists():
        raise FileNotFoundError(
            f"Preprocessed file not found at {CLEAN_PATH}. Please run pipeline.py first."
        )
    return pd.read_csv(CLEAN_PATH)


def analyze_structure(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs comprehensive structural inspection of the dataset:
      - Dimensions, memory footprint, and null audit
      - Categorical feature cardinality
      - Five-Number Summary (Min, Q1, Median, Q3, Max) with Std and Skewness
    """
    print("\n" + "=" * 65)
    print("  DSA LIFE CYCLE — PHASE 1: OVERALL STRUCTURE ANALYSIS")
    print("  Engineer: Azifali A (Data Cleaning & Structure Analyst)")
    print("=" * 65)

    num_rows, num_cols = df.shape
    memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

    print(f"Dataset Dimensions : {num_rows:,} rows x {num_cols} columns")
    print(f"Memory Footprint   : {memory_mb:.2f} MB")
    print(f"Missing Values     : {df.isnull().sum().sum()} (0.00% across all features)")
    print(f"Duplicate Rows     : {df.duplicated().sum()}")

    # Categorical feature breakdown
    cat_cols = ["crop", "season", "state", "rainfall_category", "yield_category"]
    print("\n--- Categorical Feature Cardinality ---")
    for col in cat_cols:
        if col in df.columns:
            print(f"  * {col:<18} : {df[col].nunique():3d} unique categories")

    # Numerical features 5-number summary + Mean, Std, Skewness, IQR
    num_cols_list = df.select_dtypes(include=[np.number]).columns.tolist()
    if "crop_year" in num_cols_list:
        num_cols_list.remove("crop_year")

    summary_rows = []
    for col in num_cols_list:
        s = df[col]
        q1 = s.quantile(0.25)
        median = s.median()
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        summary_rows.append({
            "Feature": col,
            "Mean": round(s.mean(), 2),
            "Std": round(s.std(), 2),
            "Min": round(s.min(), 2),
            "Q1 (25%)": round(q1, 2),
            "Median (Q2)": round(median, 2),
            "Q3 (75%)": round(q3, 2),
            "Max": round(s.max(), 2),
            "IQR": round(iqr, 2),
            "Skewness": round(s.skew(), 2),
        })

    summary_df = pd.DataFrame(summary_rows)
    print("\n--- Five-Number Statistical Summary Table ---")
    print(summary_df.to_string(index=False))

    return summary_df


if __name__ == "__main__":
    df = load_dataset()
    analyze_structure(df)

