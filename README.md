# 🏨 Hotel Booking Cancellation & Revenue Intelligence Analytics

**Author:** Pranav Singh

A complete, end-to-end data analytics project investigating why hotel guests cancel bookings, how those cancellations translate into revenue and occupancy risk, and what actions a hotel business could take to improve booking conversion and operational planning.

---

## Project Overview

This project analyzes 119,390 raw hotel booking records from a City Hotel and a Resort Hotel (2015–2017) to answer one central business question:

> **What factors are associated with hotel booking cancellations, how do cancellations impact potential revenue and occupancy, and what actions can hotels take to improve booking conversion and operational planning?**

The project spans the full analytics stack — Python for cleaning/EDA/statistics, MySQL for business-query analysis, Power BI for interactive dashboards, Excel for supporting KPI summaries, and a documented Jupyter notebook narrating the entire analytical workflow.

---

## Business Problem

Hotels lose a meaningful share of potential revenue to booking cancellations, but not all cancellations carry equal risk. Without segment-level visibility into *which* bookings are most likely to cancel and *how much revenue* that represents, hotels are left reacting to cancellations rather than planning around them. This project builds that visibility from the ground up, directly from the raw booking data — no assumptions, no synthetic figures.

## Project Objectives

- Quantify the overall and segment-level cancellation rate
- Identify booking characteristics associated with higher cancellation risk (lead time, market segment, deposit type, distribution channel, customer type, season)
- Estimate potential revenue at risk from cancellations
- Analyze demand and seasonality patterns across hotel types
- Build a data-driven Revenue Risk Matrix to classify market segments
- Translate findings into concrete, data-backed business recommendations

---

## Dataset Description

- **Source:** [Hotel Booking Demand](https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand) (Kaggle, Jesse Mostipak), originally published by Antonio, Almeida & Nunes, *Data in Brief*, Vol. 22, 2019.
- **Raw size:** 119,390 rows × 32 columns
- **Grain:** one row per hotel booking
- **Key columns:** `hotel`, `is_canceled`, `lead_time`, `arrival_date_year/month/week_number/day_of_month`, `stays_in_weekend_nights`, `stays_in_week_nights`, `adults`, `children`, `babies`, `meal`, `country`, `market_segment`, `distribution_channel`, `is_repeated_guest`, `previous_cancellations`, `deposit_type`, `agent`, `company`, `customer_type`, `adr` (Average Daily Rate), `reservation_status`, `reservation_status_date`.
- **After cleaning:** 119,210 rows × 44 columns (32 original + 12 engineered features).

---

## Technology Stack

| Tool | Purpose |
|---|---|
| 🐍 Python (pandas, numpy, matplotlib, seaborn, scipy) | Data cleaning, EDA, feature engineering, statistical analysis, visualization |
| 🗄️ MySQL | Database storage and 23 business-analysis SQL queries (CTEs, window functions) |
| 📊 Power BI | 3-page interactive executive dashboard |
| 📈 Excel (openpyxl) | Supporting KPI summary workbook |
| 📓 Jupyter Notebook | End-to-end documented analytical narrative |

---

## Analytics Workflow

1. **Data Quality Assessment** — inspect missingness, duplicates, invalid values
2. **Data Cleaning** — documented, non-destructive handling of missing/invalid data
3. **Feature Engineering** — lead time categories, season, total guests/nights, revenue estimates, risk flags
4. **Cancellation Analysis** — rates across hotel type, market segment, channel, lead time, deposit type, season
5. **Demand & Seasonality Analysis** — monthly trends, peak/low periods, historical trend line
6. **Revenue & Occupancy Analysis** — potential revenue, revenue at risk, ADR analysis
7. **Statistical Analysis** — correlation, chi-square tests, t-tests, outlier detection
8. **Revenue Risk Matrix** — data-driven (median-threshold) segment classification
9. **Business Recommendations** — insights translated into concrete actions

---

## Project Structure

```
Hotel-Booking-Cancellation-Revenue-Intelligence/
│
├── README.md
├── INTERVIEW_GUIDE.md
├── requirements.txt
│
├── data/
│   ├── raw/                          hotel_bookings.csv (119,390 x 32)
│   └── processed/                    hotel_bookings_cleaned.csv (119,210 x 44)
│
├── src/
│   ├── data_cleaning.py
│   ├── cancellation_analysis.py
│   ├── demand_analysis.py
│   ├── revenue_analysis.py
│   └── statistical_analysis.py
│
├── notebooks/
│   └── Hotel_Booking_Cancellation_Revenue_Analysis.ipynb
│
├── sql/
│   ├── database_setup.sql
│   └── hotel_business_analysis.sql   (23 business queries)
│
├── dashboard/
│   └── POWER_BI_GUIDE.md
│
├── excel/
│   └── hotel_booking_business_analysis.xlsx
│
├── insights/
│   └── business_recommendations.md
│
└── images/
    └── generated_visualizations/     (16 charts)
```

---

## Data Cleaning Process

| Issue | Decision | Rationale |
|---|---|---|
| `children` missing (4 rows) | Filled with 0 | Adults recorded; missing count most plausibly means 0 |
| `country` missing (488 rows) | Labeled "Unknown" | Avoids fabricating nationality data |
| `agent` / `company` missing (13.7% / 94.3%) | Converted to `has_agent` / `has_company` flags | Missingness reflects "no agent/company used", not a data gap to impute |
| Exact duplicate rows (31,994, 26.8%) | **Retained** | No unique Booking ID exists in the dataset, so duplicate-looking rows cannot be reliably confirmed as accidental vs. legitimate separate bookings; count is reported for transparency, not dropped |
| Zero-guest bookings (180 rows) | Removed | Logically invalid — a booking cannot have zero occupants |
| Negative ADR (1 row) | Set to NaN, excluded from revenue calcs only | Row retained for booking/cancellation analysis; only revenue math excludes it |

Full documentation is in `src/data_cleaning.py`.

---

## Key KPIs (from the cleaned dataset)

| KPI | Value |
|---|---|
| Total Bookings (cleaned) | 119,210 |
| Overall Cancellation Rate | 37.08% |
| Average Lead Time | ~104 days |
| Average Stay Duration | ~3.4 nights |
| Average Daily Rate (ADR) | ~€102 |
| Total Potential Booking Revenue | €42,714,213 |
| Potential Revenue at Risk (Canceled) | €16,727,237 (39.2%) |

---

## Cancellation Analysis Highlights

- **By Hotel Type:** City Hotel 41.79% vs. Resort Hotel 27.77%
- **By Lead Time:** 9.60% (Last Minute) → 55.41% (Long Lead, 162+ days)
- **By Market Segment:** Groups 61.11% (highest reliable-volume segment) vs. Corporate 18.76% (lowest, excluding the 2-booking Undefined segment)
- **By Deposit Type:** Non-Refundable 99.36% vs. No Deposit 28.40% — a counter-intuitive finding flagged for investigation, not smoothed over
- **Prior Cancellation History:** 91.68% cancellation rate for repeat-cancelers vs. 33.94% baseline

## Demand and Seasonality Insights

- Peak demand month: **August** (13,861 bookings); lowest: **January** (5,921 bookings)
- City Hotel demand is more seasonally volatile (CV 0.277) than Resort Hotel (CV 0.238)
- Summer is both the peak-demand and the highest-cancellation season (38.76%)

## Hotel Performance Analysis

| | City Hotel | Resort Hotel |
|---|---|---|
| Bookings | 79,163 | 40,047 |
| Cancellation Rate | 41.79% | 27.77% |
| Avg Daily Rate | €105.50 | €94.99 |

## Revenue Risk Analysis

Median-threshold Revenue Risk Matrix (by market segment): Online TA, Offline TA/TO and Groups classified as **High Revenue Risk**; Direct as **Stable Revenue Segment**; Corporate and Complementary as **Low Priority Segments**; Aviation as a **Growth Opportunity**. Full detail in `insights/business_recommendations.md`.

## Business Recommendations

See [`insights/business_recommendations.md`](insights/business_recommendations.md) for the complete, data-backed recommendation set covering deposit policy review, lead-time-based confirmation workflows, Online TA channel management, repeat-canceler flagging, and seasonal operational planning.

---

## How to Run the Project

```bash
# 1. Clone and install dependencies
pip install -r requirements.txt

# 2. Run the Python analysis pipeline (in order)
python src/data_cleaning.py
python src/cancellation_analysis.py
python src/demand_analysis.py
python src/revenue_analysis.py
python src/statistical_analysis.py

# 3. Explore the full analytical narrative
jupyter notebook notebooks/Hotel_Booking_Cancellation_Revenue_Analysis.ipynb

# 4. Set up the MySQL database
mysql -u <user> -p < sql/database_setup.sql
# then import data/processed/hotel_bookings_cleaned.csv (see instructions inside the file)
mysql -u <user> -p < sql/hotel_business_analysis.sql

# 5. Open the Excel workbook
excel/hotel_booking_business_analysis.xlsx

# 6. Build the Power BI dashboard
# Follow dashboard/POWER_BI_GUIDE.md
```

---

## Limitations

- **Revenue figures are estimates**, calculated as `adr x total_stay_nights`. The dataset has no separate "amount actually invoiced/paid" field, so all revenue figures are labeled "potential" throughout this project, not audited financial revenue.
- **No booking ID / primary key** exists in the raw data, so 31,994 exact-duplicate rows (26.8% of raw records) could not be reliably confirmed as accidental vs. legitimate separate bookings. They are **retained** in the cleaned dataset rather than dropped; this means duplicate-looking bookings may inflate volume-based KPIs slightly if any of them were in fact data-entry duplicates.
- **Associations, not causation.** All cancellation "drivers" described (lead time, deposit type, etc.) are statistical associations found in this dataset. No causal experiment was run, and language throughout the project reflects that.
- **2015 and 2017 are partial calendar years** in this dataset, which affects direct year-over-year volume comparisons.
- Both hotels are located in Portugal; findings may not generalize to hotels in other markets.

---

## Author

**Pranav Singh**
