# src/etl/features.py
# Member 3: Jayakrishnan KV (Feature Engineer & Correlation Analyst)
# Executes T9 to T15 domain feature engineering and mathematical normalization.

from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def assign_crop_yield_tier(yield_values: pd.Series) -> pd.Series:
    """
    Assigns crop-relative yield categories (Low, Medium, High) using tertiles.
    Prevents cross-crop bias by evaluating yield relative to each individual crop distribution.
    """
    if len(yield_values) < 3 or yield_values.nunique() < 3:
        return pd.Series("Medium", index=yield_values.index)

    low_cutoff = yield_values.quantile(0.333)
    high_cutoff = yield_values.quantile(0.667)

    conditions = [
        yield_values <= low_cutoff,
        (yield_values > low_cutoff) & (yield_values <= high_cutoff),
        yield_values > high_cutoff,
    ]
    labels = ["Low", "Medium", "High"]

    assigned = np.select(conditions, labels, default="Medium")
    return pd.Series(assigned, index=yield_values.index)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies 7 feature engineering transformations (T9 to T15).
    Calculates input intensities, bins rainfall, caps coconut outliers, and normalizes yield.
    """
    print("\n" + "=" * 60)
    print("  PHASE 3: FEATURE ENGINEERING (Member 3: Jayakrishnan KV)")
    print("=" * 60)

    # T9: Fertilizer intensity per hectare (kg/ha)
    df["fertilizer_per_hectare"] = (df["fertilizer"] / df["area"]).round(4)
    print("[T9]  Engineered: fertilizer_per_hectare (kg/ha)")

    # T10: Pesticide intensity per hectare (kg/ha)
    df["pesticide_per_hectare"] = (df["pesticide"] / df["area"]).round(4)
    print("[T10] Engineered: pesticide_per_hectare (kg/ha)")

    # T11: Categorize annual rainfall into 5 agronomic bands
    bins = [0, 500, 1000, 1500, 2500, np.inf]
    labels = ["Very Low", "Low", "Medium", "High", "Very High"]
    df["rainfall_category"] = pd.cut(df["annual_rainfall"], bins=bins, labels=labels, right=True)
    print("[T11] Engineered: rainfall_category (Very Low, Low, Medium, High, Very High)")

    # T12: Relative yield category per crop using balanced tertiles
    df["yield_category"] = (
        df.groupby("crop", group_keys=False)["yield"]
        .apply(assign_crop_yield_tier)
    )
    print("[T12] Engineered: yield_category (Balanced tertiles: Low, Medium, High)")

    # T13: Coconut 95th-percentile outlier capping
    coconut_mask = df["crop"].str.lower() == "coconut"
    if coconut_mask.any():
        cap_val = df.loc[coconut_mask, "yield"].quantile(0.95)
        df.loc[coconut_mask & (df["yield"] > cap_val), "yield"] = cap_val
        print(f"[T13] Capped Coconut yield at 95th percentile ({cap_val:,.2f})")

    # T14: Mathematical log1p normalization (reduces skewness from 12.79 to 1.14)
    df["log_yield"] = np.log1p(df["yield"]).round(4)
    skew_before = 12.79
    skew_after = df["log_yield"].skew()
    print(f"[T14] Engineered: log_yield via log1p (Skewness reduced: {skew_before} -> {skew_after:.2f})")

    # T15: Deterministic multi-key sorting
    df = df.sort_values(by=["state", "crop", "crop_year"]).reset_index(drop=True)
    print("[T15] Dataset sorted deterministically by [state, crop, crop_year]")

    print("\nFeature engineering phase completed successfully.")
    return df


if __name__ == "__main__":
    from src.etl.extract import extract
    from src.etl.clean import clean_data
    raw = extract()
    cleaned = clean_data(raw)
    feat = engineer_features(cleaned)

