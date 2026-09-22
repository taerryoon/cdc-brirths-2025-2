# U.S. Provisional Natality Analytics Dashboard (2025)

An interactive, educational Streamlit dashboard designed for undergraduate business analytics students to explore geographic, monthly, and sex-based patterns in CDC provisional birth data for 2025.

---

## 🏛️ Project Overview

This dashboard analyzes provisional natality data published by the **Centers for Disease Control and Prevention (CDC) National Center for Health Statistics (NCHS)**. It provides business analytics students with a hands-on platform to practice core visual analytics principles:
- **Absolute Counts vs. Per-Capita Rates**: Understand why raw counts reflect state population size rather than fertility rates.
- **Seasonality & Calendar Effects**: Analyze monthly fluctuations, including the 28-day February artifact and late summer birth peaks.
- **Demographic Benchmarks**: Observe the secondary sex ratio at birth (~105 male births per 100 female births).
- **Zero-Baseline Visual Ethics**: Ensure charts avoid truncated axes that exaggerate minor variations.

---

## 📁 Repository Structure

```
CDC - birth - 2025/
├── Data/
│   └── Provisional_Natality_2025_CDC.xlsx       # Raw CDC Excel dataset
├── src/
│   ├── __init__.py                              # Package marker
│   ├── config.py                                # Constants, 51-state mapping, colors, metadata
│   ├── data_loader.py                           # Cached ingestion, path resolution, validation schema
│   ├── metrics.py                               # Filtered KPI computation and summary aggregations
│   ├── visualizations.py                        # Plotly visual generators (choropleth, trends, heatmaps)
│   └── components.py                            # Header banners, KPI cards, filter badges, CSS styles
├── app.py                                       # Main Streamlit dashboard application
├── requirements.txt                             # Production dependencies
└── README.md                                    # Project documentation
```

---

## 🚀 Running the Dashboard Locally

### Prerequisites
- Python 3.9+ installed.

### Setup Instructions
1. **Clone or Navigate to the Workspace Directory**:
   ```bash
   cd "CDC - birth - 2025"
   ```

2. **Create and Activate a Virtual Environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or: venv\Scripts\activate on Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Streamlit Dashboard**:
   ```bash
   streamlit run app.py
   ```
   The dashboard will automatically open in your default web browser at `http://localhost:8501`.

---

## ☁️ Deploying to Streamlit Community Cloud

This project is pre-configured for one-click deployment to Streamlit Community Cloud:
1. Push this repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Select your repository, branch (`main`), and set **Main file path** to `app.py`.
4. Click **Deploy**. Streamlit Cloud will automatically detect `requirements.txt` and load `Data/Provisional_Natality_2025_CDC.xlsx` seamlessly using relative paths.

---

## 📊 Dashboard Features

1. **Header & Context Banners**:
   - CDC attribution and provisional notice.
   - Prominent analytical caveat distinguishing raw birth counts from birth rates.
2. **Interactive Sidebar Filters**:
   - Multi-select for 51 U.S. geographies (50 states + DC) with "Select All" and "Clear" controls.
   - Chronological month selector with "Select All" and "Clear" controls.
   - Infant sex selector (`All`, `Female`, `Male`).
   - "Reset All Filters" one-click action.
3. **Responsive KPI Row**:
   - Total Births in selection (with thousands separator).
   - Count of selected geographies.
   - Average births per selected month.
   - Geography with highest birth volume.
   - Peak calendar month.
4. **Five Analytical Tabs**:
   - **📊 Overview**: Executive summary with monthly trend, male/female comparison, and core analytics takeaways.
   - **🗺️ Geographic Analysis**: US state choropleth map, ranked bar chart with customizable top N, and Top 5 vs Bottom 5 volume contrast.
   - **📈 Monthly & Sex Analysis**: Seasonality line chart with benchmark average line, infant sex distribution, and State $\times$ Month heatmap matrix.
   - **📋 Data Table & Download**: Searchable filtered table, descriptive statistics, state summaries, and one-click CSV export.
   - **📖 About the Data**: Methodological guide on counts vs rates, crude birth rate formula, seasonality factors, secondary sex ratio benchmark, and automated schema validation results.

---

## 🔬 Data Integrity & Validation

The application performs automated schema checks on startup:
- Checks for presence of all required columns.
- Validates 0 null / NaN values across all 1,224 rows.
- Confirms non-negative integer birth counts.
- Verifies exact 1-to-1 match for all 51 states and District of Columbia in the postal code mapping.
- Ensures month codes span 1 through 12 in calendar sequence.
