# 🌍 Plastic Waste Around the World — Executive Dashboard

An executive-grade, Klipfolio-inspired environmental analytics dashboard built with **Python**, **Streamlit**, **Pandas**, and **Plotly**. This application analyzes authentic country-level plastic waste footprints, recycling performance, per-capita generation, and coastal leakage vulnerability using the official dataset **`Plastic Waste Around the World.csv`**.

---

## 📌 Project Architecture

```text
DASHBOARD/
├── app.py                             # Main Streamlit dashboard application
├── requirements.txt                   # Core dependencies (pandas, plotly, streamlit)
├── Plastic Waste Around the World.csv # Authentic country dataset (165 country records)
└── README.md                          # Project documentation and run guide
```

---

## 🚀 Quickstart: How to Run Locally in Antigravity

### 1. Open Terminal in Workspace
In Antigravity (or VS Code / PowerShell), ensure your working directory is the project directory:
```powershell
cd c:\Users\Jnansi\Downloads\DASHBOARD
```

### 2. Activate the Virtual Environment
Activate the existing virtual environment:
```powershell
.\.venv\Scripts\Activate.ps1
```

*(Alternatively, run directly using the `.venv` Python executable without manual activation).*

### 3. Install Dependencies
Verify and install required packages:
```powershell
pip install -r requirements.txt
```

### 4. Launch the Dashboard
Run the Streamlit application:
```powershell
streamlit run app.py
```
Or directly via the Python module:
```powershell
python -m streamlit run app.py
```

Streamlit will print the local URL in the terminal (usually `http://localhost:8501`). Open this URL in your web browser.

---

## 📊 Dataset Schema

The dashboard automatically loads and validates **`Plastic Waste Around the World.csv`** located directly beside `app.py` using `pathlib.Path(__file__).resolve().parent`. All calculations are derived strictly from reported values without synthetic estimation.

| Column Name | Type | Description | Unit |
| :--- | :--- | :--- | :--- |
| **`Country`** | `string` | Unique country name (165 records) | N/A |
| **`Total_Plastic_Waste_MT`** | `float` | National annual plastic waste | Metric Tons (MT) |
| **`Main_Sources`** | `string` | Dominant packaging / waste sector | Categorical |
| **`Recycling_Rate`** | `float` | Reported national recycling efficiency | Percentage (%) |
| **`Per_Capita_Waste_KG`** | `float` | Annual plastic waste per person | Kilograms (kg) |
| **`Coastal_Waste_Risk`** | `string` | Leakage risk classification | `Low`, `Medium`, `High`, `Very_High` |

---

## 🎯 Dashboard Features & Visualizations

### 1. Executive Klipfolio Design System
- **Dark Navy Header**: Professional gradient hero card (`#091224` to `#1a2d4d`) with live record counts and status badges.
- **Clean White Cards**: Rounded corners (`border-radius: 14px`), subtle border outlines (`#e2e8f0`), and soft drop shadows (`0 4px 14px rgba(15,23,42,0.04)`).
- **Responsive Layout**: Fluid design optimized for desktop and mobile screens.

### 2. Five Dynamic KPI Cards
1. **Total Plastic Waste (MT)** — Sum of reported country totals.
2. **Average Recycling Rate (%)** — Unweighted mean across countries.
3. **Average Per-Capita Waste (kg)** — Mean generation per person.
4. **High / Very High Coastal Risk** — Count and percentage of vulnerable coastal nations.
5. **Countries Analyzed** — Active country count vs global total.

### 3. Seven Interactive Plotly Charts
1. **Top 10 Countries by Total Plastic Waste** — Horizontal bar chart with data labels, MT formatting, and deep hover tooltips.
2. **Recycling Rates by Country** — Sorted bar chart with toggle for sorting direction (Highest First / Lowest First) and display scope (Top 15, 25, 50, or All).
3. **Top 10 Per-Capita Plastic Waste Countries** — Horizontal bar chart displaying peak per-person plastic footprints.
4. **Coastal Waste Risk Distribution** — Donut chart (`hole=0.58`) illustrating country counts, percentage shares, and sample countries per risk category.
5. **Main Plastic Waste Sources** — Bar chart counting country records per source sector (`Consumer Packaging`, `Industrial Packaging`, etc.).
6. **Total Plastic Waste vs Recycling Rate** — Multi-dimensional scatter plot colored by coastal risk, with bubble sizes proportional to per-capita waste and an optional logarithmic scale toggle.
7. **Head-to-Head Country Comparison** — 3 independent side-by-side subplots comparing selected countries across Total Waste (MT), Recycling Rate (%), and Per-Capita Waste (kg) with dedicated scales. Includes a benchmark comparison table and CSV export.

### 4. Interactive Filters (Sidebar)
- 🔍 **Country Name Search** (live text search)
- 🌐 **Country Multiselect** (focus on specific nations)
- 🌊 **Coastal Risk Selector** (`Low`, `Medium`, `High`, `Very_High`)
- 🏭 **Main Waste Sources Selector** (packaging sectors)
- ♻️ **Recycling Rate Slider** (0.1% to 84.8%)
- 📦 **Total Plastic Waste Slider** (0.01 MT to 59.08 MT)
- ↺ **Reset All Filters** button

### 5. In-Depth Country Profile Panel
Select any nation to review an executive scorecard comparing its metrics against dataset averages (e.g. `+245% vs global mean`) alongside sector and coastal risk badges.

### 6. Dynamic Analytical Takeaways
Auto-computed analytical highlights identifying the top waste generator, recycling leader, peak per-capita generator, and dominant waste stream.

### 7. Searchable Data Table & CSV Export
- Search within country table
- Multi-column sorting (ascending/descending)
- **Download Filtered Dataset as CSV**
- **Download Country Comparison Data as CSV**

---

## 🛡️ Code Quality & Data Integrity
- **No Synthetic Records**: 100% of figures are calculated directly from `Plastic Waste Around the World.csv`.
- **Safe Type Conversion**: Numeric columns are coerced safely with tracking of any parsing anomalies.
- **Missing File Error Handling**: If the CSV is moved or missing, the dashboard presents a clear diagnostic banner indicating the exact file path expected.
- **Graceful Filter Handling**: If a filter combination results in zero matches, a friendly prompt suggests adjusting filter criteria or resetting.

---

## 📄 Footer Note
**Plastic Waste Analytics** | Data-driven environmental awareness.  
*Built for educational and analytical research.*
