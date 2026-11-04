# Crop Yield ETL Pipeline & Analytical Framework
**Batch 7 Mini Project — DSA B13 Offline**

---

## 1. Project Title
**Automated ETL Pipeline & Exploratory Analysis on Indian Agricultural Crop Yield Data**

---

## 2. Objective
The primary objective of this project is to build an automated, modular, and reproducible **Extract, Transform, Load (ETL)** pipeline and analytical framework following the **Data Science & Analytics (DSA) Life Cycle**. 

Specific goals include:
1. Extracting raw historical agricultural data and verifying structural integrity.
2. Cleaning, validating, and filtering anomalies, missing values, and zero/negative records.
3. Performing domain-specific feature engineering (chemical application intensities, rainfall categorization, quantile yield tiers).
4. Addressing significant crop-specific outlier anomalies (specifically Coconut yield unit variance).
5. Generating automated summary reports and producing a clean, analysis-ready dataset for downstream exploratory data analysis (EDA) and predictive modeling.

---

## 3. Team Members & Balanced 4-Way Workload Distribution

| Name | Project Role | Dedicated File(s) | Key Deliverables & Responsibilities |
|---|---|---|---|
| **Mithun J** | **Project Lead & System Architect** | `pipeline.py`<br>`eda.py`<br>`src/etl/extract.py`<br>`src/eda/outliers.py`<br>`.gitignore`<br>`README.md` | **ETL & Outlier Lead:**<br>• Master pipeline engine with stage execution timers (~540 ms).<br>• Ingestion health checks, schema contract verification.<br>• Master EDA orchestrator coordinating all 4 analytical phases.<br>• **DSA Phase 2 EDA:** IQR Outlier detection, Coconut anomaly analysis (nuts/ha vs tonnes/ha), skewness reduction ($12.79 \rightarrow 1.14$). |
| **Azifali A** | **Data Cleaning & Structure Analyst** | `src/etl/clean.py`<br>`src/eda/structure.py` | **Cleaning & Structure Lead:**<br>• 8 data validation & cleaning rules (T1–T8: whitespace trimming, duplicate check, missing values, boundary rules).<br>• Yield viability filtering (`yield > 0`, 112 invalid rows dropped).<br>• **DSA Phase 1 EDA:** Overall dataset structure (19,577 rows $\times$ 15 cols), cardinality, and Five-Number summary table. |
| **Jayakrishnan KV** | **Feature Engineer & Correlation Analyst** | `src/etl/features.py`<br>`src/eda/correlations.py` | **Features & Correlation Lead:**<br>• 7 feature engineering operations (T9–T15: fertilizer/pesticide ratios, rainfall bands, crop yield tertiles).<br>• Coconut 95th-percentile capping & log1p normalization.<br>• **DSA Phase 3 EDA:** Bivariate relationships, seasonal productivity, and Pearson correlation analysis with `log_yield`. |
| **Sharon** | **Persistence & Visualizations Engineer** | `src/etl/load.py`<br>`src/eda/visuals.py`<br>`requirements.txt` | **Persistence & Visual Reporting Lead:**<br>• Data persistence engine (`output/preprocessed_data.csv`).<br>• 3 summary CSV reports + pipeline text audit.<br>• **DSA Phase 4 EDA:** Major 5 visual representations in `reports/figures/` at 300 DPI (seasonal boxplot with outlier callouts, heatmap, bar charts). |

---

## 4. Data Source Description
As required by Step 2 of the project specification:
1. **Source:** Kaggle — *Crop Yield in Indian States* (`crop_yield.csv`).
2. **Reason for Choice:** India is predominantly an agrarian economy with substantial regional variance in soil, climate, rainfall, and crop yield. This dataset captures multifaceted real-world interactions across states, crop seasons, area, production, and chemical inputs (fertilizer and pesticide).
3. **Information Contained:** 19,689 records containing 10 raw attributes: `Crop`, `Crop_Year`, `Season`, `State`, `Area`, `Production`, `Annual_Rainfall`, `Fertilizer`, `Pesticide`, and `Yield`.
4. **Structure:** Structured tabular data.
5. **Format:** Comma-Separated Values (`.csv`).
6. **Update Frequency:** Static historical agricultural survey records spanning 1997 to 2020.

---

## 5. ETL Architecture Workflow

```
[raw_data/crop_yield.csv]
           │
           ▼
     1. EXTRACT & AUDIT (Member 1: Mithun J)
        • Read raw data & check column contract
        • Ingestion health diagnostics & skewness analysis
           │
           ▼
     2. DATA CLEANING & VALIDATION (Member 2: Azifali A)
        • T1: Snake_case column renaming
        • T2: Categorical whitespace stripping
        • T3: Duplicate row filtering
        • T4: Null value handling
        • T5: Strict numeric data typing
        • T6: Crop year window check (1990–2025)
        • T7: Area (>0) & Production (>=0) constraints
        • T8: Viable yield enforcement (>0)
           │
           ▼
     3. FEATURE ENGINEERING & SCALING (Member 3: Jayakrishnan KV)
        • T9:  fertilizer_per_hectare (kg/ha)
        • T10: pesticide_per_hectare (kg/ha)
        • T11: rainfall_category (5 precipitation bands)
        • T12: yield_category (crop-relative tertile rank: Low, Medium, High)
        • T13: Coconut 95th-percentile outlier capping
        • T14: log_yield mathematical log1p normalization
        • T15: Multi-key deterministic sorting (state -> crop -> crop_year)
           │
           ▼
     4. LOAD & GENERATE REPORTS (Member 4: Sharon)
        • Save primary dataset to output/preprocessed_data.csv
        • Generate 3 analytical CSV reports + 1 text report in reports/
```

---

## 6. List of Transformations & Necessity Justification

| ID | Transformation | Implementation Detail | Why It Was Necessary |
|---|---|---|---|
| **T1** | Column Renaming | Standardized all headers to lowercase `snake_case`. | Eliminates inconsistencies, spaces, and case sensitivity bugs in Python/Pandas. |
| **T2** | Whitespace Stripping | Trimmed leading/trailing spaces across all text columns. | Prevents duplicate categories caused by accidental whitespace (e.g., `'Kharif '` vs `'Kharif'`). |
| **T3** | Duplicate Removal | Checked for and dropped exact duplicate rows. | Ensures data uniqueness and avoids artificially inflated counts or biased models. |
| **T4** | Missing Value Handling | Verified and dropped null/NaN records. | Machine learning estimators fail when encountering missing values; guarantees complete records. |
| **T5** | Numeric Type Casting | Cast `crop_year` to `int64` and numerical metrics to `float64`. | Prevents numeric columns from being parsed as generic objects or strings during computation. |
| **T6** | Crop Year Validation | Kept only records within valid agricultural survey bounds (1990–2025). | Filters corrupt or impossible timestamps outside documented Indian crop survey periods. |
| **T7** | Area & Production Checks | Verified `area > 0` and `production >= 0`. | Crops cannot be cultivated on zero/negative hectares; production cannot be negative. |
| **T8** | Viable Yield Filter | Removed non-viable records with `yield <= 0` (112 records dropped). | A crop that yielded zero or negative output is either a total failure recording error or an artifact unsuited for yield prediction models. |
| **T9** | Fertilizer per Hectare | Computed `fertilizer / area` (kg/ha). | Raw fertilizer totals depend on farm size; normalizing per hectare allows fair comparison across farms. |
| **T10** | Pesticide per Hectare | Computed `pesticide / area` (kg/ha). | Normalizes chemical pesticide application intensity independent of total farm area. |
| **T11** | Rainfall Categorization | Binned rainfall into 5 bands: Very Low, Low, Medium, High, Very High. | Enables categorical environmental grouping and climatic segment analysis. |
| **T12** | Crop-Relative Yield Tiers | Assigned Low, Medium, High tiers per crop using balanced tertiles. | Yield varies wildly by crop type (e.g., Sugarcane vs Moong); per-crop tertiles prevent cross-crop bias. |
| **T13** | Coconut Outlier Capping | Capped Coconut yields at the 95th percentile (~13,809.77). | Coconut yields are reported in nuts/ha (mean ~8,652) instead of tonnes/ha, causing extreme distortion. |
| **T14** | Log Transformation | Created `log_yield` using `np.log1p(yield)`. | Compresses extreme skewness (skew drops from 12.79 to 1.14), stabilizing variance for statistical models. |
| **T15** | Multi-Key Deterministic Sorting | Sorted by `state`, then `crop`, then `crop_year`. | Creates a consistent, repeatable ordering essential for time-series splits and clear reporting. |

---

## 7. Reports Generated (Step 7 Compliance)

All analytical reports are saved inside the `reports/` folder:

1. **`reports/crop_yield_summary.csv` (Category-wise Report):**
   Summarizes performance across all unique crops, detailing record count, mean yield, min/max yield, average fertilizer and pesticide application per hectare, and unique cultivation states.
2. **`reports/state_production_summary.csv` (Region-wise Report):**
   Aggregates total agricultural output across Indian states, ranking states by total production, total cultivated area, average yield, and crop diversity.
3. **`reports/season_yield_analysis.csv` (Season-wise Report):**
   Evaluates crop productivity and rainfall patterns across agricultural seasons (Kharif, Rabi, Whole Year, Summer, Autumn, Winter).
4. **`reports/pipeline_summary_report.txt` (Master Execution Summary):**
   Text-based audit detailing initial data volume, retained record count (99.43%), column listings, yield statistics, top 5 crops/states, and data distribution counts.

---

## 8. Challenges Faced

1. **Unit Discrepancy & Extreme Skewness in Coconut Data:**
   - *Challenge:* The raw dataset had an extreme yield skewness of **12.79**. Diagnostic analysis revealed that Coconut yields reached up to 21,105, because coconuts are counted in *nuts per hectare*, whereas food grains (Wheat, Rice) are weighed in *tonnes per hectare*.
   - *Resolution:* Implemented a 95th-percentile crop-specific cap for Coconut followed by a logarithmic transform (`log_yield = np.log1p(yield)`), successfully bringing overall dataset skewness down to **1.14**.
2. **Quantile Boundary Collisions on Low-Variance Crops:**
   - *Challenge:* Using naive `pd.qcut` on crops with identical or repeated yield numbers resulted in `ValueError: Bin edges must be unique`.
   - *Resolution:* Built a custom `assign_crop_yield_tier` function with `include_lowest=True` and fallback boundary thresholds to reliably split records into balanced tiers (Low: 6,535, High: 6,522, Medium: 6,520).
3. **Cross-Platform Console Unicode Compatibility:**
   - *Challenge:* Unicode checkmarks and arrow symbols caused `UnicodeEncodeError` when running on Windows PowerShell / Command Prompt.
   - *Resolution:* Standardized all CLI logging output to universal ASCII symbols (`[OK]`, `->`, `<=`, `>=`).
4. **Multi-Developer Git Branching & Merge Isolation:**
   - *Challenge:* Four team members needed to submit independent contributions without conflicting commits or overwriting teammate files.
   - *Resolution:* Assigned strictly separated modular files (`extract.py`, `clean.py`, `features.py`, `load.py`) connected by an orchestrator (`pipeline.py`), with individual feature branches and PRs on GitHub.

---

## 9. Learning Outcomes

1. **Production ETL Design:** Practical experience designing modular Extract, Transform, Load pipelines with separation of concerns and step-by-stage latency monitoring.
2. **Data Cleaning & Defensive Validation:** Hands-on understanding of data validation rules, handling trailing whitespace, numeric coercion, and boundary filtering.
3. **Statistical Outlier Mitigation:** Learned when to cap domain-specific outliers versus when to log-transform skewed distributions to preserve agricultural signal without distorting models.
4. **Collaborative Git Workflow:** Experienced the full team development lifecycle: feature branch creation, clean atomic commits, peer pull request reviews, and remote branch tracking.

---

## 10. Future Improvements

1. **Automated Unit & Integration Testing:** Add a `pytest` suite to test edge cases, schema validation assertions, and non-null guarantees in CI/CD.
2. **Interactive EDA Dashboard:** Build a Streamlit or Plotly web dashboard to visualize state-level yield choropleth maps and seasonal yield distributions dynamically.
3. **Machine Learning Model Development:** Train baseline regression models (Random Forest, XGBoost, Ridge Regression) on `log_yield` and classification models on `yield_category`.
4. **Live Data Ingestion:** Connect the pipeline to live government agricultural APIs (such as Open Government Data India) to ingest future seasonal survey updates automatically.

---

## Project Structure

```text
mini project/
│
├── raw_data/                 <- Ingestion source data (crop_yield.csv)
├── output/                   <- Cleaned primary dataset (preprocessed_data.csv)
├── reports/                  <- Summary & analytical reports (.csv, .txt & figures)
│   ├── figures/              <- Major 5 high-resolution EDA visual plots (300 DPI)
│   │   ├── 01_yield_distribution_and_outliers.png
│   │   ├── 02_top_crop_yields.png
│   │   ├── 03_seasonal_yield_variation.png (with labeled outlier crops)
│   │   ├── 04_state_production_ranking.png
│   │   └── 05_correlation_heatmap.png
│   ├── crop_yield_summary.csv
│   ├── state_production_summary.csv
│   ├── season_yield_analysis.csv
│   ├── outlier_analysis_summary.csv
│   ├── eda_summary_report.txt
│   └── pipeline_summary_report.txt
│
├── src/                      <- Production Modular Source Package
│   ├── etl/                  <- ETL Pipeline Modules
│   │   ├── extract.py        <- Schema contract & ingestion diagnostics (Mithun J)
│   │   ├── clean.py          <- 8 Validation & cleaning operations (Azifali A)
│   │   ├── features.py       <- 7 Feature engineering & scaling steps (Jayakrishnan KV)
│   │   └── load.py           <- Persistence & multi-report generator (Sharon)
│   └── eda/                  <- Exploratory Data Analysis (DSA Life Cycle) Modules
│       ├── structure.py      <- DSA Phase 1: Structure & 5-Number summary (Azifali A)
│       ├── outliers.py       <- DSA Phase 2: Outlier & Coconut anomaly analysis (Mithun J)
│       ├── correlations.py   <- DSA Phase 3: Bivariate & Pearson correlation analysis (Jayakrishnan KV)
│       └── visuals.py        <- DSA Phase 4: 5 Major high-resolution plots (Sharon)
│
├── pipeline.py               <- Master Pipeline Orchestrator & Benchmarking (Mithun J)
├── eda.py                    <- Master EDA Orchestrator (Mithun J)
├── requirements.txt          <- Project dependencies (pandas, numpy, matplotlib, seaborn)
├── .gitignore                <- Repository hygiene rules
└── README.md                 <- Architecture & project documentation
```

---

## How to Execute

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the master ETL pipeline
python pipeline.py

# 3. Run the Exploratory Data Analysis (EDA) module
python eda.py
```
