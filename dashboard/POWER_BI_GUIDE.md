# Power BI Dashboard Guide
### Hotel Booking Cancellation & Revenue Intelligence Analytics

This guide describes a professional 3-page Power BI dashboard built on top of `data/processed/hotel_bookings_cleaned.csv` (or the `bookings` table in the `hotel_booking_analytics` MySQL database via the MySQL connector). All measures below are written to match the **actual column names** in the cleaned dataset.

---

## Data Import

1. In Power BI Desktop: **Get Data → Text/CSV** → select `data/processed/hotel_bookings_cleaned.csv`
   (or **Get Data → MySQL database** → server/database `hotel_booking_analytics`, table `bookings`).
2. In Power Query, confirm data types: `is_canceled`, `is_repeated_guest`, `has_agent`, `has_company`, `is_returning_guest`, `has_prior_cancellation_history` as **Whole Number** (0/1) or **True/False**; `arrival_date`, `reservation_status_date` as **Date**; `adr`, `potential_booking_revenue` as **Decimal Number**.
3. Create a **Date table** (Calendar) keyed off `arrival_date` for time-intelligence visuals, and mark it as a Date table.

---

## PAGE 1 — Executive Overview

**KPI Cards** (top row):
- Total Bookings → `[Total Bookings]`
- Cancellation Rate → `[Cancellation Rate]`
- Average Lead Time → `[Avg Lead Time]`
- Average Stay Duration → `[Avg Stay Nights]`
- Average Daily Rate → `[Avg ADR]`
- Repeat Guest Percentage → `[Repeat Guest %]`

**Visualizations:**
- **Line chart**: Monthly Booking Trend — axis `arrival_date_month` (sorted by `arrival_month_num`), value `[Total Bookings]`
- **Bar chart**: Bookings by Hotel Type — axis `hotel`, value `[Total Bookings]`
- **Bar chart**: Cancellation Rate by Hotel Type — axis `hotel`, value `[Cancellation Rate]`
- **Bar/Treemap**: Market Segment Performance — axis `market_segment`, values `[Total Bookings]` and `[Cancellation Rate]`
- **Card matrix**: Key Business KPIs summarized above

**Slicers:** `hotel`, `arrival_date_year`, `season`

---

## PAGE 2 — Cancellation Intelligence

**Main business question:** *What booking characteristics are associated with the highest cancellation risk?*

**Visualizations:**
- **Bar chart**: Cancellation Rate by Market Segment — axis `market_segment`, value `[Cancellation Rate]`
- **Bar chart**: Cancellation Rate by Distribution Channel — axis `distribution_channel`, value `[Cancellation Rate]`
- **Bar chart**: Cancellation Rate by Deposit Type — axis `deposit_type`, value `[Cancellation Rate]`
- **Bar chart**: Cancellation Rate by Lead Time Category — axis `lead_time_category` (sort by average lead time), value `[Cancellation Rate]`
- **Table**: High-Risk Booking Segments — `market_segment`, `[Total Bookings]`, `[Cancellation Rate]`, conditional formatting (red = high risk) on segments with `[Total Bookings] >= 100`
- **Line chart**: Cancellation Trends — axis `arrival_date` (by month), value `[Cancellation Rate]`, split by `hotel`

**Slicers:** `deposit_type`, `market_segment`, `has_prior_cancellation_history`

---

## PAGE 3 — Demand and Revenue Intelligence

**Main business question:** *Where are the strongest demand opportunities and the biggest revenue risks?*

**Visualizations:**
- **Line chart**: Seasonal Demand Trends — axis `arrival_date_month`, value `[Total Bookings]`, split by `hotel`
- **Bar chart**: Hotel Type Performance — `hotel` vs `[Total Bookings]`, `[Cancellation Rate]`, `[Avg ADR]` (use a multi-row card or small multiples)
- **Bar chart**: ADR Analysis — axis `hotel` or `season`, value `[Avg ADR]`
- **Scatter chart**: Revenue Risk Matrix — X = `[Cancellation Rate]` by `market_segment`, Y = `[Total Potential Revenue]` by `market_segment`, size = `[Total Bookings]` (recreates the Python-generated risk matrix interactively)
- **Table**: High-Value Booking Segments — `market_segment`, `[Total Potential Revenue]`, `[Revenue at Risk]`, `[Cancellation Rate]`
- **Map or bar chart**: Market Performance — `country` vs `[Total Bookings]` (top 15)

**Slicers:** `season`, `arrival_date_year`, `hotel`

---

## DAX Measures

```dax
Total Bookings = COUNTROWS(bookings)

Cancelled Bookings = SUM(bookings[is_canceled])

Cancellation Rate = DIVIDE([Cancelled Bookings], [Total Bookings])

Avg Lead Time = AVERAGE(bookings[lead_time])

Avg Stay Nights = AVERAGE(bookings[total_stay_nights])

Avg ADR = AVERAGE(bookings[adr])

Repeat Guest % = DIVIDE(
    CALCULATE([Total Bookings], bookings[is_returning_guest] = TRUE()),
    [Total Bookings]
)

Total Potential Revenue = SUM(bookings[potential_booking_revenue])

Revenue at Risk =
CALCULATE(
    [Total Potential Revenue],
    bookings[is_canceled] = 1
)

Pct Revenue at Risk = DIVIDE([Revenue at Risk], [Total Potential Revenue])

Completed Bookings = CALCULATE([Total Bookings], bookings[is_canceled] = 0)
```

All measures reference only columns that exist in `hotel_bookings_cleaned.csv` — no fabricated fields.

---

## Design Notes
- Use a consistent color pair for hotel type across all three pages (e.g., blue = City Hotel, gold = Resort Hotel) for visual continuity.
- Use a red-to-green conditional color scale on cancellation-rate visuals so risk is immediately legible.
- Keep Page 1 as the "5-second glance" summary; Pages 2 and 3 are the drill-down analytical pages recruiters/stakeholders would explore next.
