# ⚡ Carbon-Aware AI Scheduling: Evidence from U.S. Electricity Data

> **How much can you reduce the carbon footprint of AI training just by changing *when* and *where* you run it?**  
> This project answers that question with a full year of hourly U.S. grid data.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Data: EIA Form 930](https://img.shields.io/badge/Data-EIA%20Form%20930-orange)](https://www.eia.gov/electricity/gridmonitor/)
[![Context: TCD MSc Business Analytics](https://img.shields.io/badge/TCD-MSc%20Business%20Analytics-blue)](https://www.tcd.ie)

---

## 📌 Project Overview

As AI training workloads scale, their electricity consumption — and the resulting carbon emissions — have become a board-level ESG concern. But carbon intensity is not fixed: it varies by **region**, **hour of day**, **day of week**, and **season**, because the grid's generation mix changes constantly.

This project investigates whether operational scheduling decisions alone — no new hardware, no renewable energy certificates — can meaningfully reduce Scope 2 carbon exposure for AI data centre workloads.

**Spoiler: yes, by up to 45% — but only if you know which levers to pull and where.**

---

## 🔬 Research Questions

| # | Question | Type |
|---|----------|------|
| RQ1 | How large are cross-regional differences in hourly carbon exposure across U.S. grid areas? | Descriptive |
| RQ2 | Within the same region, how strongly does carbon exposure vary by hour and day of week? | Descriptive |
| RQ3 | For a fixed AI training workload, how much can exposure be reduced through time-shifting, location-shifting, and joint optimisation? | Prescriptive |
| RQ4 | Under realistic operational constraints, which scheduling margin is most effective? | Operational |

---

## 📊 Key Findings

### Finding 1 — Location is the dominant lever (61 pp gap)

| Region | Mean Fossil Share | Interpretation |
|--------|-------------------|----------------|
| 🔴 Florida (FLA) | **87.6%** | Highest — fossil-intensive year-round |
| 🔴 Midwest (MIDW) | **83.2%** | 2nd highest — near-flat daily profile |
| 🟡 California (CAL) | **50.7%** | Solar-driven midday dips |
| 🟢 Northwest (NW) | **31.8%** | Hydro-dominated |
| 🟢 Central (CENT) | **26.7%** | Lowest — wind-rich, high scheduling potential |

> The same AI training job run in Florida emits **3× more** fossil-weighted electricity than in Central.

---

### Finding 2 — Time-shifting works, but only in the right regions

| Region | Hourly Spread (pp) | Scheduling Value |
|--------|-------------------|-----------------|
| Southeast | 32.2 | ✅ High — strong solar/fossil swing |
| Texas | 21.6 | ✅ High — afternoon fossil peak |
| Southwest | 19.4 | ✅ High — solar midday dip |
| Midwest | 4.1 | ❌ Negligible — flat fossil baseline |
| New York | 4.2 | ❌ Negligible — diverse clean mix |

---

### Finding 3 — "Avoid peak demand" is the wrong rule in 5 of 13 regions

Demand and carbon exposure are **negatively correlated** in Midwest (r = −0.75), Florida (−0.50), and Carolinas (−0.47). In these regions, peak demand coincides with *peak renewable output* — so scheduling away from peak demand **raises** emissions. Direct carbon-proxy inputs are required.

---

### Finding 4 — Combined optimisation cuts exposure by up to 45%

| Lever | Empirical Range | Feasibility | Horizon |
|-------|----------------|-------------|---------|
| Location (region) | ~61 pp | High capex, slow | Long-term |
| Seasonal allocation | ~5–10% relative | Medium, contractual | Medium-term |
| Time-of-day shift | 4–32 pp (region-specific) | Low — scheduler config | Short-term |
| Weekend preference | 1–4 pp (region-specific) | Low — scheduler config | Short-term |
| Demand-based proxy | Unreliable (r = −0.75 to +0.93) | **Avoid** as standalone | Replace now |

---

## 🛠️ Methodology

```
EIA Form 930 (2025)
493,283 BA-hour observations
59 Balancing Authorities × 13 EIA Regions
Hourly resolution, Jan–Dec 2025
         │
         ▼
Carbon Exposure Proxy
  = (Coal + Gas + Petroleum) / Net Generation
  (Scope 2 operational emissions proxy)
         │
    ┌────┴────────────────┐
    ▼                     ▼
Descriptive Analysis    Predictive Analysis
  - Cross-regional         - Linear Regression
  - Temporal variation     - Random Forest ✓ (selected)
  - Seasonal patterns      - XGBoost
  - Demand coupling        - Persistence baseline
         │
         ▼
Scenario Simulation
  - Baseline vs. time-shift vs. location-shift vs. joint optimisation
  - Realistic operational constraints applied
```

**Carbon proxy formula:**

$$\text{Carbon Proxy}_{r,t} = \frac{\text{Coal}_{r,t} + \text{Gas}_{r,t} + \text{Petroleum}_{r,t}}{\text{Net Generation}_{r,t}}$$

---

## 🤖 Predictive Modelling Results

| Model | MAE | RMSE | vs. Naive Baseline |
|-------|-----|------|--------------------|
| Naive (lag-1h) | 0.0200 | 0.0407 | — |
| Linear Regression | 0.0215 | 0.0381 | −7.3% ❌ |
| **Random Forest** | **0.0191** | **0.0351** | **+4.7% ✅** |
| XGBoost | 0.0196 | 0.0351 | +2.3% |
| Day-ahead RF (no lag-1h) | 0.0517 | — | −2.1% vs lag-24h ❌ |

**Key insight:** The 1-hour lag (`carbon_proxy_lag1h`) accounts for 98.9% of Random Forest feature importance — because thermal plants ramp slowly. This means short-term scheduling is highly predictable, but day-ahead forecasting remains hard. Scheduling tools should use rolling short-term forecasts, not day-ahead ML predictions.

---

## 📁 Repository Structure

```
carbon-aware-ai-scheduling/
│
├── data/
│   ├── raw/                    # EIA Form 930 raw downloads (not tracked — see setup)
│   └── processed/              # Cleaned BA-hour dataset with carbon proxy
│
├── notebooks/
│   ├── 01_data_prep.ipynb      # EIA data ingestion, cleaning, proxy construction
│   ├── 02_descriptive.ipynb    # Cross-regional, temporal, seasonal analysis (Figs 1–7)
│   ├── 03_predictive.ipynb     # LR, RF, XGBoost models + feature importance
│   └── 04_simulation.ipynb     # Scenario simulations for RQ3 & RQ4
│
├── src/
│   ├── carbon_proxy.py         # Proxy calculation utilities
│   ├── eia_loader.py           # EIA API / CSV ingestion
│   ├── models.py               # Model training + evaluation pipeline
│   └── scheduler_sim.py        # Workload scheduling simulation logic
│
├── outputs/
│   └── figures/                # All paper figures (PNG/SVG)
│
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/carbon-aware-ai-scheduling.git
cd carbon-aware-ai-scheduling
pip install -r requirements.txt
```

### 2. Download EIA data

Data source: [EIA Form 930 Hourly Electric Grid Monitor](https://www.eia.gov/electricity/gridmonitor/)

```bash
# Download 2025 BA-hour balance data
python src/eia_loader.py --year 2025 --output data/raw/
```

Or manually download `EIA930_BALANCE_2025_Jan_Jun.csv` and `EIA930_BALANCE_2025_Jul_Dec.csv` from the EIA website and place them in `data/raw/`.

### 3. Run the pipeline

```bash
# Step 1: Process raw data and construct carbon proxy
jupyter nbconvert --to notebook --execute notebooks/01_data_prep.ipynb

# Step 2–4: Run analysis notebooks in sequence
jupyter lab  # then open notebooks/ in order
```

---

## 💡 Business Implications

This project reframes AI sustainability from a **procurement problem** (buying RECs) to an **operational intelligence problem** (scheduling against live grid data).

Three practical takeaways for data centre operators and AI cloud providers:

1. **Short-term (now):** Replace demand-based scheduling heuristics with direct carbon-proxy inputs. Enable region-tiered time-shifting (prioritise Southeast, Texas, Southwest, California).

2. **Medium-term (≤12 months):** Deploy a rolling RF forecast in production. Shift flexible batch training seasonally toward Central, California, and Northwest. Build a joint Infrastructure–MLOps–Sustainability governance model.

3. **Long-term (next capex):** Treat regional fossil share as a first-class site-selection criterion. Avoid greenfield commitments in Midwest or Florida given the 15–20 year regulatory trajectory.

> **Greenwashing risk note:** Annual-average REC matching can mask high-carbon operational footprints. As 24/7 CFE frameworks and CSRD double-materiality requirements tighten, firms relying on demand-based proxies in the wrong regions face audit and reputational exposure.

---

## 🗂️ Data Source

- **EIA Form 930 BALANCE** — U.S. Energy Information Administration  
  Hourly generation by fuel type and electricity demand, by Balancing Authority  
  URL: https://www.eia.gov/electricity/gridmonitor/  
  Period: January–December 2025 (493,283 BA-hour observations)

---

## 📚 References

- International Energy Agency. (2025). *Energy and AI*. https://www.iea.org/reports/energy-and-ai
- Khan, I., Jack, M. W., & Stephenson, J. (2018). Analysis of greenhouse gas emissions in electricity systems using time-varying carbon intensity. *Journal of Cleaner Production*, 184, 1091–1101.
- de Vries, A. (2023). The growing energy footprint of artificial intelligence. *Joule*, 7(10), 2191–2194.

---

## 👤 Author

**Lin Htet Aung**  
MSc Business Analytics — Trinity College Dublin  
*Responsible for: descriptive analysis, statistical testing, workload scheduling simulation, persistence baseline & day-ahead forecast evaluation*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/YOUR_PROFILE)
[![GitHub](https://img.shields.io/badge/GitHub-Portfolio-181717?style=flat&logo=github)](https://github.com/YOUR_USERNAME)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

*This project was completed as part of the ESG Analytics module at Trinity Business School, Trinity College Dublin (April 2026).*
