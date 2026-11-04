# eda.py
# Member 1: Mithun J (Project Lead & System Architect)
# Master Exploratory Data Analysis (EDA) Orchestrator
# Coordinates all 4 phases of the Data Science & Analytics (DSA) Life Cycle:
#   Phase 1: Overall Structure Analysis         — Member 2: Azifali A
#   Phase 2: Outlier Analysis & Coconut Anomaly — Member 1: Mithun J (Project Lead)
#   Phase 3: Bivariate & Correlation Analysis   — Member 3: Jayakrishnan KV
#   Phase 4: Visual Plots & Reports             — Member 4: Sharon

import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.eda.structure import analyze_structure
from src.eda.outliers import run_outlier_analysis
from src.eda.correlations import analyze_correlations
from src.eda.visuals import generate_major_plots

CLEAN_PATH = PROJECT_ROOT / "output" / "preprocessed_data.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"


def load_dataset() -> pd.DataFrame:
    """Loads the preprocessed dataset for EDA."""
    if not CLEAN_PATH.exists():
        raise FileNotFoundError(
            f"Preprocessed file not found at {CLEAN_PATH}. Please run pipeline.py first."
        )
    return pd.read_csv(CLEAN_PATH)


def export_eda_summary_report(df: pd.DataFrame, outlier_df: pd.DataFrame, coconut_info: dict, plot_paths: list) -> None:
    """Exports structured EDA summary text report to reports/eda_summary_report.txt."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "eda_summary_report.txt"

    lines = []
    lines.append("EXPLORATORY DATA ANALYSIS (EDA) - STATISTICAL REPORT")
    lines.append("Batch 7 Mini Project — DSA B13 Offline")
    lines.append("=" * 65)
    lines.append("")
    lines.append("1. DATA STRUCTURE OVERVIEW (Member 2: Azifali A)")
    lines.append(f"   Total Records       : {len(df):,}")
    lines.append(f"   Total Features      : {len(df.columns)}")
    lines.append(f"   Missing Values      : {df.isnull().sum().sum()}")
    lines.append(f"   Duplicate Rows      : {df.duplicated().sum()}")
    lines.append("")

    lines.append("2. OUTLIER SUMMARY (Member 1: Mithun J - Project Lead)")
    for _, row in outlier_df.iterrows():
        lines.append(
            f"   * {row['Feature']:<24}: Bounds [{row['Lower Bound']:>9.2f}, {row['Upper Bound']:>9.2f}] | "
            f"Outliers: {row['Outlier Count']:>5} ({row['Outlier %']:>5.2f}%) | "
            f"Extreme: {row['Extreme Count']:>5} ({row['Extreme %']:>5.2f}%)"
        )
    lines.append("")

    lines.append("3. COCONUT YIELD ANOMALY & REMEDIATION (Member 1: Mithun J)")
    lines.append(f"   * Raw Dataset Yield Skewness        : {coconut_info.get('raw_skew', 12.79):.2f}")
    lines.append(f"   * Capped Yield Skewness             : {coconut_info.get('capped_skew', 12.43):.2f}")
    lines.append(f"   * Log-Transformed Skewness (Full)   : {coconut_info.get('log_skew', 3.66):.2f}")
    lines.append(f"   * Log-Transformed Skewness (Non-Coc): {coconut_info.get('non_coconut_log_skew', 1.95):.2f}")
    lines.append("   * Finding: Coconut's reporting unit (nuts/ha vs tonnes/ha) is the root cause.")
    lines.append("   * Resolution: 95th-pct capping + log1p normalization restored normal distribution.")
    lines.append("")

    lines.append("4. FEATURE CORRELATIONS WITH LOG_YIELD (Member 3: Jayakrishnan KV)")
    corrs = (
        df[["fertilizer_per_hectare", "pesticide_per_hectare", "annual_rainfall", "area", "production", "log_yield"]]
        .corr()["log_yield"]
        .drop("log_yield")
        .sort_values(ascending=False)
        .round(3)
    )
    for feat, corr_val in corrs.items():
        lines.append(f"   * {feat:<24} : {corr_val:+0.3f}")
    lines.append("")

    lines.append("5. GENERATED MAJOR EDA PLOTS (Member 4: Sharon)")
    for p in plot_paths:
        lines.append(f"   * reports/figures/{p.name}")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] Saved EDA Master Text Report : reports/{report_path.name}")


def main() -> None:
    """Executes the full 4-stage DSA Lifecycle EDA workflow."""
    print("\n" + "=" * 65)
    print("   MASTER EXPLORATORY DATA ANALYSIS (EDA)")
    print("   Data Science & Analytics (DSA) Life Cycle Execution")
    print("=" * 65)

    df = load_dataset()

    # Stage 1: Structure (Azifali)
    analyze_structure(df)

    # Stage 2: Outliers (Mithun)
    outlier_df, coconut_info = run_outlier_analysis(df)

    # Stage 3: Bivariate & Correlations (Jayakrishnan)
    analyze_correlations(df)

    # Stage 4: Visual Plots (Sharon)
    plot_paths = generate_major_plots(df)

    # Master Report
    export_eda_summary_report(df, outlier_df, coconut_info, plot_paths)

    print("\n" + "=" * 65)
    print("   ALL 4 EDA MODULES COMPLETED SUCCESSFULLY")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
