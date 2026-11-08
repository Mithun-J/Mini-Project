# src/eda/visuals.py
# Member 4: Sharon (Persistence & Visualizations Engineer)
# DSA Life Cycle — Phase 4: High-Resolution Publication-Quality EDA Visual Plots

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEAN_PATH = PROJECT_ROOT / "output" / "preprocessed_data.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


def load_dataset() -> pd.DataFrame:
    """Loads the preprocessed dataset for visualization plotting."""
    if not CLEAN_PATH.exists():
        raise FileNotFoundError(
            f"Preprocessed file not found at {CLEAN_PATH}. Please run pipeline.py first."
        )
    return pd.read_csv(CLEAN_PATH)


def generate_major_plots(df: pd.DataFrame) -> list:
    """
    Generates 5 major visual representations for EDA:
      1. Yield Distribution & Outlier Remediation (Raw vs Log-Transformed)
      2. Top 10 Highest Yielding Crops
      3. Seasonal Agricultural Yield Productivity with Outlier Crop Callouts
      4. Top 10 Agricultural States by Production
      5. Input & Yield Correlation Heatmap
    """
    print("\n" + "=" * 65)
    print("  DSA LIFE CYCLE — PHASE 4: MAJOR 5 EDA VISUAL PLOTS")
    print("  Engineer: Sharon (Persistence & Visualizations Engineer)")
    print("=" * 65)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", font_scale=1.0)
    saved_plots = []

    # -------------------------------------------------------------
    # Plot 1: Yield Distribution & Outlier Remediation
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    sns.histplot(
        df["yield"],
        bins=50,
        kde=True,
        color="#d95f02",
        ax=axes[0],
        line_kws={"linewidth": 2},
    )
    axes[0].set_title(
        f"Capped Raw Yield Distribution\n(Skewness = {df['yield'].skew():.2f})",
        fontsize=12,
        fontweight="bold",
    )
    axes[0].set_xlabel("Yield (Tonnes/Ha or Nuts/Ha)", fontsize=11)
    axes[0].set_ylabel("Frequency", fontsize=11)

    sns.histplot(
        df["log_yield"],
        bins=50,
        kde=True,
        color="#1b9e77",
        ax=axes[1],
        line_kws={"linewidth": 2},
    )
    axes[1].set_title(
        f"Log-Transformed Yield (log_yield)\n(Normalized Skewness = {df['log_yield'].skew():.2f})",
        fontsize=12,
        fontweight="bold",
    )
    axes[1].set_xlabel("log_yield = log(1 + yield)", fontsize=11)
    axes[1].set_ylabel("Frequency", fontsize=11)

    plt.suptitle("Figure 1: Yield Distribution & Outlier Remediation", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    p1 = FIGURES_DIR / "01_yield_distribution_and_outliers.png"
    plt.savefig(p1, dpi=300, bbox_inches="tight")
    plt.close()
    saved_plots.append(p1)
    print(f"[OK] Generated Figure 1: reports/figures/{p1.name}")

    # -------------------------------------------------------------
    # Plot 2: Top 10 Highest Yielding Crops
    # -------------------------------------------------------------
    top10_crops = (
        df.groupby("crop")["yield"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    plt.figure(figsize=(12, 6))
    palette = sns.color_palette("viridis", len(top10_crops))
    ax = sns.barplot(
        data=top10_crops,
        x="yield",
        y="crop",
        palette=palette,
        hue="crop",
        legend=False,
    )
    plt.title("Figure 2: Top 10 Highest Mean Yield Crops in India", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Mean Yield (Tonnes/Ha; Coconut in Nuts/Ha)", fontsize=11)
    plt.ylabel("Crop Type", fontsize=11)

    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.annotate(
                f"{width:,.1f}",
                (width, p.get_y() + p.get_height() / 2.0),
                xytext=(6, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                fontsize=9,
                fontweight="semibold",
            )

    plt.tight_layout()
    p2 = FIGURES_DIR / "02_top_crop_yields.png"
    plt.savefig(p2, dpi=300, bbox_inches="tight")
    plt.close()
    saved_plots.append(p2)
    print(f"[OK] Generated Figure 2: reports/figures/{p2.name}")

    # -------------------------------------------------------------
    # Plot 3: Seasonal Agricultural Yield Productivity
    # -------------------------------------------------------------
    season_order = ["Kharif", "Rabi", "Whole Year", "Summer", "Autumn", "Winter"]
    available_seasons = [s for s in season_order if s in df["season"].unique()]

    plt.figure(figsize=(12, 6))
    ax = sns.boxplot(
        data=df,
        x="season",
        y="log_yield",
        order=available_seasons,
        palette="Set2",
        hue="season",
        legend=False,
        fliersize=3,
        flierprops={"marker": "o", "color": "red", "alpha": 0.4},
    )
    plt.title(
        "Figure 3: Seasonal Crop Yield Variation (log_yield)\nwith Outlier Crop Identification",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Agricultural Season", fontsize=11)
    plt.ylabel("log_yield = log(1 + yield)", fontsize=11)

    for idx, season in enumerate(available_seasons):
        season_data = df[df["season"] == season]
        q1 = season_data["log_yield"].quantile(0.25)
        q3 = season_data["log_yield"].quantile(0.75)
        iqr = q3 - q1
        upper_whisker = q3 + 1.5 * iqr

        outliers = season_data[season_data["log_yield"] > upper_whisker]
        if not outliers.empty:
            max_outlier_crop = outliers.loc[outliers["log_yield"].idxmax(), "crop"]
            max_val = outliers["log_yield"].max()
            ax.annotate(
                f"Outlier: {max_outlier_crop}",
                xy=(idx, max_val),
                xytext=(idx + 0.15, max_val - 0.2),
                arrowprops=dict(facecolor="black", arrowstyle="->", lw=1),
                fontsize=8.5,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="yellow", alpha=0.5),
            )

    plt.tight_layout()
    p3 = FIGURES_DIR / "03_seasonal_yield_variation.png"
    plt.savefig(p3, dpi=300, bbox_inches="tight")
    plt.close()
    saved_plots.append(p3)
    print(f"[OK] Generated Figure 3: reports/figures/{p3.name}")

    # -------------------------------------------------------------
    # Plot 4: Top 10 Agricultural States by Production
    # -------------------------------------------------------------
    top10_states = (
        df.groupby("state")["production"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    top10_states["production_million_tonnes"] = top10_states["production"] / 1e6

    plt.figure(figsize=(12, 6))
    ax = sns.barplot(
        data=top10_states,
        x="production_million_tonnes",
        y="state",
        palette="mako",
        hue="state",
        legend=False,
    )
    plt.title("Figure 4: Top 10 Agricultural States in India by Total Production", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Cumulative Production (Million Tonnes)", fontsize=11)
    plt.ylabel("State", fontsize=11)

    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.annotate(
                f"{width:,.2f} M",
                (width, p.get_y() + p.get_height() / 2.0),
                xytext=(6, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                fontsize=9,
                fontweight="semibold",
            )

    plt.tight_layout()
    p4 = FIGURES_DIR / "04_state_production_ranking.png"
    plt.savefig(p4, dpi=300, bbox_inches="tight")
    plt.close()
    saved_plots.append(p4)
    print(f"[OK] Generated Figure 4: reports/figures/{p4.name}")

    # -------------------------------------------------------------
    # Plot 5: Input & Yield Correlation Heatmap
    # -------------------------------------------------------------
    numeric_features = [
        "fertilizer_per_hectare",
        "pesticide_per_hectare",
        "annual_rainfall",
        "area",
        "production",
        "yield",
        "log_yield",
    ]
    labels_clean = [
        "Fertilizer (kg/ha)",
        "Pesticide (kg/ha)",
        "Annual Rainfall (mm)",
        "Area (ha)",
        "Production (tonnes)",
        "Yield (raw/capped)",
        "Log Yield (log1p)",
    ]

    corr = df[numeric_features].corr()

    plt.figure(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    cmap = sns.diverging_palette(220, 20, as_cmap=True)

    sns.heatmap(
        corr,
        mask=mask,
        cmap=cmap,
        vmax=1.0,
        vmin=-0.5,
        center=0,
        annot=True,
        fmt=".2f",
        square=True,
        linewidths=0.8,
        cbar_kws={"shrink": 0.8, "label": "Pearson Correlation Coefficient"},
        xticklabels=labels_clean,
        yticklabels=labels_clean,
    )
    plt.title("Figure 5: Correlation Matrix — Agricultural Inputs vs Output Yield", fontsize=14, fontweight="bold", pad=20)
    plt.xticks(rotation=45, ha="right", fontsize=9.5)
    plt.yticks(rotation=0, fontsize=9.5)

    plt.tight_layout()
    p5 = FIGURES_DIR / "05_correlation_heatmap.png"
    plt.savefig(p5, dpi=300, bbox_inches="tight")
    plt.close()
    saved_plots.append(p5)
    print(f"[OK] Generated Figure 5: reports/figures/{p5.name}")

    print(f"\nAll 5 publication-ready figures saved successfully to reports/figures/.")
    return saved_plots


if __name__ == "__main__":
    df = load_dataset()
    generate_major_plots(df)

