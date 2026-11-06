# src/etl/clean.py
# Member 2: Azifali A (Data Cleaning & Structure Analyst)
# Executes T1 to T8 validation and data cleaning rules.

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs 8 data validation & cleaning transformations (T1 to T8).
    Removes invalid observations and normalizes column formats.
    """
    print("\n" + "=" * 60)
    print("  PHASE 2: DATA CLEANING & VALIDATION (Member 2: Azifali A)")
    print("=" * 60)
    start_count = len(df)

    # T1: Convert column names to lowercase snake_case
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    print("[T1] Column headers standardized to lowercase snake_case")

    # T2: Strip leading/trailing whitespaces from text columns
    for col in ["crop", "season", "state"]:
        df[col] = df[col].astype(str).str.strip()
    print("[T2] Trailing and leading whitespaces trimmed across string columns")

    # T3: Remove duplicate rows
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"[T3] Exact duplicate records removed: {before - len(df)}")

    # T4: Handle missing values
    before = len(df)
    df = df.dropna().reset_index(drop=True)
    print(f"[T4] Records with null/missing values dropped: {before - len(df)}")

    # T5: Strict numeric type casting
    df["crop_year"] = pd.to_numeric(df["crop_year"], errors="coerce").astype(int)
    numeric_cols = ["area", "production", "annual_rainfall", "fertilizer", "pesticide", "yield"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna().reset_index(drop=True)
    print("[T5] Numeric attributes coerced to float64 / int64")

    # T6: Validate crop year window (1990 to 2025)
    before = len(df)
    df = df[(df["crop_year"] >= 1990) & (df["crop_year"] <= 2025)].reset_index(drop=True)
    print(f"[T6] Records outside agricultural survey window (1990-2025) dropped: {before - len(df)}")

    # T7: Enforce domain boundaries (Area > 0, Production >= 0)
    before = len(df)
    df = df[(df["area"] > 0) & (df["production"] >= 0)].reset_index(drop=True)
    print(f"[T7] Records violating area (>0) and production (>=0) constraints dropped: {before - len(df)}")

    # T8: Enforce viable yield constraint (Yield > 0)
    before = len(df)
    df = df[df["yield"] > 0].reset_index(drop=True)
    print(f"[T8] Non-viable zero/negative yield records dropped: {before - len(df)}")

    total_removed = start_count - len(df)
    pct_retained = (len(df) / start_count) * 100
    print(f"\nCleaning complete: {len(df):,} valid rows retained ({pct_retained:.2f}%), {total_removed} removed.")
    return df


if __name__ == "__main__":
    from src.etl.extract import extract
    raw_df = extract()
    cleaned_df = clean_data(raw_df)

