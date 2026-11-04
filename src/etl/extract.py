# src/etl/extract.py
# Member 1: Mithun J (Project Lead & System Architect)
# Loads raw dataset, verifies schema contract, and executes pre-flight health checks.

from pathlib import Path
import pandas as pd

# Resolve project root directory (two levels up from src/etl/)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Expected columns in the raw dataset
EXPECTED_COLUMNS = [
    "Crop", "Crop_Year", "Season", "State", "Area",
    "Production", "Annual_Rainfall", "Fertilizer", "Pesticide", "Yield"
]


def check_dataset_health(df: pd.DataFrame) -> dict:
    """
    Checks basic data quality metrics on the raw dataset
    prior to executing validation and cleaning operations.
    """
    stats = {
        "total_records": len(df),
        "total_columns": len(df.columns),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "zero_yield_rows": int((df["Yield"] <= 0).sum()),
        "invalid_area_rows": int((df["Area"] <= 0).sum()),
        "negative_prod_rows": int((df["Production"] < 0).sum()),
        "year_min": int(df["Crop_Year"].min()),
        "year_max": int(df["Crop_Year"].max()),
        "yield_skewness": round(float(df["Yield"].skew()), 2),
    }

    # Investigate Coconut average compared to other crops
    coconut_mask = df["Crop"].astype(str).str.strip().str.lower() == "coconut"
    if coconut_mask.any():
        stats["coconut_mean"] = round(float(df.loc[coconut_mask, "Yield"].mean()), 2)
        stats["others_mean"] = round(float(df.loc[~coconut_mask, "Yield"].mean()), 2)

    return stats


def extract() -> pd.DataFrame:
    """
    Reads crop_yield.csv from raw_data/, verifies schema contract,
    prints ingestion diagnostics, and returns the DataFrame.
    """
    print("\n" + "=" * 60)
    print("  PHASE 1: DATA EXTRACTION (Member 1: Mithun J)")
    print("=" * 60)

    dataset_path = PROJECT_ROOT / "raw_data" / "crop_yield.csv"

    if not dataset_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at: {dataset_path}")

    print("Reading file: raw_data/crop_yield.csv")
    df = pd.read_csv(dataset_path)

    # Validate schema column contract
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Schema violation! Missing required columns: {missing_cols}")
    print("All 10 required schema columns verified.")

    # Ingestion health diagnostics
    stats = check_dataset_health(df)

    print("\n--- Ingestion Health Diagnostics ---")
    print(f"  * Total records          : {stats['total_records']:,}")
    print(f"  * Missing values         : {stats['missing_values']}")
    print(f"  * Duplicate rows         : {stats['duplicate_rows']}")
    print(f"  * Year range             : {stats['year_min']} to {stats['year_max']}")
    print(f"  * Zero or negative yield : {stats['zero_yield_rows']} rows (to be cleaned)")
    print(f"  * Yield skewness         : {stats['yield_skewness']} (high due to coconut unit variance)")

    if "coconut_mean" in stats:
        print(f"  * Anomaly Alert          : Coconut avg yield ({stats['coconut_mean']:,}) "
              f"is drastically higher than other crops ({stats['others_mean']}).")

    print("\nExtraction phase completed successfully.")
    return df


if __name__ == "__main__":
    extract()

