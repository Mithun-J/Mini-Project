# src/etl/load.py
# Member 4: Sharon (Persistence & Visual Reporting Lead)
# Saves cleaned dataset and produces analytical summary reports.

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def generate_crop_summary(df: pd.DataFrame, reports_dir: Path) -> Path:
    """Generates crop-wise summary report (Report 1)."""
    summary = (
        df.groupby("crop")
        .agg(
            record_count=("crop", "count"),
            mean_yield=("yield", "mean"),
            min_yield=("yield", "min"),
            max_yield=("yield", "max"),
            mean_fertilizer_per_ha=("fertilizer_per_hectare", "mean"),
            mean_pesticide_per_ha=("pesticide_per_hectare", "mean"),
            mean_rainfall=("annual_rainfall", "mean"),
            states_count=("state", "nunique"),
        )
        .round(2)
        .sort_values(by="mean_yield", ascending=False)
        .reset_index()
    )
    file_path = reports_dir / "crop_yield_summary.csv"
    summary.to_csv(file_path, index=False)
    return file_path


def generate_state_summary(df: pd.DataFrame, reports_dir: Path) -> Path:
    """Generates state-wise production and yield summary report (Report 2)."""
    summary = (
        df.groupby("state")
        .agg(
            record_count=("state", "count"),
            total_production=("production", "sum"),
            total_area=("area", "sum"),
            mean_yield=("yield", "mean"),
            unique_crops=("crop", "nunique"),
        )
        .round(2)
        .sort_values(by="total_production", ascending=False)
        .reset_index()
    )
    file_path = reports_dir / "state_production_summary.csv"
    summary.to_csv(file_path, index=False)
    return file_path


def generate_season_summary(df: pd.DataFrame, reports_dir: Path) -> Path:
    """Generates season-wise yield and rainfall analysis report (Report 3)."""
    summary = (
        df.groupby("season")
        .agg(
            record_count=("season", "count"),
            mean_yield=("yield", "mean"),
            mean_rainfall=("annual_rainfall", "mean"),
            mean_fertilizer_per_ha=("fertilizer_per_hectare", "mean"),
            mean_pesticide_per_ha=("pesticide_per_hectare", "mean"),
        )
        .round(2)
        .sort_values(by="mean_yield", ascending=False)
        .reset_index()
    )
    file_path = reports_dir / "season_yield_analysis.csv"
    summary.to_csv(file_path, index=False)
    return file_path


def generate_text_summary(cleaned_df: pd.DataFrame, raw_df: pd.DataFrame, reports_dir: Path) -> Path:
    """Generates master pipeline summary text report (Report 4)."""
    report_path = reports_dir / "pipeline_summary_report.txt"

    lines = []
    lines.append("CROP YIELD ETL PIPELINE — AUDIT & SUMMARY REPORT")
    lines.append("Batch 7 Mini Project — DSA B13 Offline")
    lines.append("=" * 60)
    lines.append("")

    lines.append("1. EXECUTION OVERVIEW")
    lines.append(f"   Raw Records Ingested   : {len(raw_df):,}")
    lines.append(f"   Clean Records Saved    : {len(cleaned_df):,}")
    dropped = len(raw_df) - len(cleaned_df)
    pct = (len(cleaned_df) / len(raw_df)) * 100
    lines.append(f"   Records Filtered Out   : {dropped:,} ({100 - pct:.2f}%)")
    lines.append(f"   Data Retention Rate    : {pct:.2f}%")
    lines.append("")

    lines.append("2. FINAL SCHEMA CONTRACT")
    lines.append(f"   Total Columns: {len(cleaned_df.columns)}")
    for col, dtype in cleaned_df.dtypes.items():
        lines.append(f"   - {col:<26} : {dtype}")
    lines.append("")

    lines.append("3. DATA INTEGRITY & AUDIT")
    lines.append(f"   Missing Values in Output : {cleaned_df.isna().sum().sum()}")
    lines.append(f"   Duplicate Rows in Output : {cleaned_df.duplicated().sum()}")
    lines.append(f"   Survey Year Coverage     : {cleaned_df['crop_year'].min()} to {cleaned_df['crop_year'].max()}")
    lines.append(f"   Number of States         : {cleaned_df['state'].nunique()}")
    lines.append(f"   Number of Crops          : {cleaned_df['crop'].nunique()}")
    lines.append("")

    lines.append("4. YIELD METRICS (DISTRIBUTION SUMMARY)")
    y = cleaned_df["yield"]
    lines.append(f"   Min Yield                : {y.min():.2f}")
    lines.append(f"   Q1 (25th percentile)     : {y.quantile(0.25):.2f}")
    lines.append(f"   Median (50th percentile) : {y.median():.2f}")
    lines.append(f"   Mean Yield               : {y.mean():.2f}")
    lines.append(f"   Q3 (75th percentile)     : {y.quantile(0.75):.2f}")
    lines.append(f"   Max Yield (Capped)       : {y.max():.2f}")
    lines.append(f"   Standard Deviation       : {y.std():.2f}")
    lines.append(f"   Log Yield Skewness       : {cleaned_df['log_yield'].skew():.2f}")
    lines.append("")

    lines.append("5. TOP 5 CROPS BY MEAN YIELD")
    top_crops = (
        cleaned_df.groupby("crop")["yield"]
        .mean()
        .sort_values(ascending=False)
        .head(5)
    )
    for crop, mean_val in top_crops.items():
        lines.append(f"   {crop:<22} : {mean_val:>10.2f}")
    lines.append("")

    lines.append("6. TOP 5 AGRICULTURAL STATES BY TOTAL PRODUCTION")
    top_states = (
        cleaned_df.groupby("state")["production"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )
    for state, total_prod in top_states.items():
        lines.append(f"   {state:<22} : {total_prod:>15,.2f}")
    lines.append("")

    lines.append("7. RAINFALL CATEGORY COUNTS")
    rain = cleaned_df["rainfall_category"].value_counts()
    for cat, count in rain.items():
        lines.append(f"   {cat:<22} : {count:,}")
    lines.append("")

    lines.append("8. GENERATED SUMMARY REPORTS")
    lines.append("   - reports/crop_yield_summary.csv       (Crop-wise metrics)")
    lines.append("   - reports/state_production_summary.csv (State-wise totals)")
    lines.append("   - reports/season_yield_analysis.csv    (Season-wise breakdown)")
    lines.append("   - reports/pipeline_summary_report.txt  (This summary text)")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def load(cleaned_df: pd.DataFrame, raw_df: pd.DataFrame) -> None:
    """
    Saves the preprocessed dataset to output/preprocessed_data.csv
    and writes multiple analytical reports to the reports/ directory.
    """
    print("\n" + "=" * 60)
    print("  PHASE 4: SAVE OUTPUT & REPORTS (Member 4: Sharon)")
    print("=" * 60)

    output_dir = PROJECT_ROOT / "output"
    reports_dir = PROJECT_ROOT / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Save preprocessed dataset
    clean_path = output_dir / "preprocessed_data.csv"
    cleaned_df.to_csv(clean_path, index=False)
    print("Saved cleaned data to: output/preprocessed_data.csv")
    print(f"Shape: {cleaned_df.shape[0]:,} rows x {cleaned_df.shape[1]} columns")

    # 2. Generate required analytical reports (Step 7 compliance)
    rep1 = generate_crop_summary(cleaned_df, reports_dir)
    rep2 = generate_state_summary(cleaned_df, reports_dir)
    rep3 = generate_season_summary(cleaned_df, reports_dir)
    rep4 = generate_text_summary(cleaned_df, raw_df, reports_dir)

    print(f"Generated Report 1: reports/{rep1.name}")
    print(f"Generated Report 2: reports/{rep2.name}")
    print(f"Generated Report 3: reports/{rep3.name}")
    print(f"Generated Report 4: reports/{rep4.name}")


if __name__ == "__main__":
    from src.etl.extract import extract
    from src.etl.clean import clean_data
    from src.etl.features import engineer_features
    raw = extract()
    cleaned = clean_data(raw)
    feat = engineer_features(cleaned)
    load(feat, raw)

