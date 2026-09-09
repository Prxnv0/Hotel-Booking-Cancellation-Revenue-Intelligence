# Interview Guide
### Hotel Booking Cancellation & Revenue Intelligence Analytics
**Author:** Pranav Singh

---

## Explain the Project in 30 Seconds

"I built an end-to-end analytics project on 119,000+ real hotel bookings to figure out why guests cancel, and what that costs the business. I cleaned the data, engineered features like lead-time categories and revenue estimates, and used Python, MySQL, Power BI, and Excel together to find that cancellation risk isn't evenly spread — it concentrates in specific segments like Online Travel Agency bookings and long-lead-time reservations — and I translated that into a data-driven Revenue Risk Matrix and concrete recommendations."

## Explain the Project in 1 Minute

"The business question was: what factors are associated with hotel booking cancellations, and how do they impact revenue and occupancy? I started with a raw dataset of 119,390 bookings across a City Hotel and Resort Hotel, ran a full data quality assessment, and cleaned it down to 119,210 analysis-ready records — documenting every decision, like converting the highly-missing `agent`/`company` columns into presence flags instead of guessing values, and deliberately *retaining* the 31,994 exact-duplicate rows because the dataset has no booking ID to confirm they're accidental. From there I engineered features like lead-time buckets, season, and an estimated potential-revenue figure. I then built five separate Python modules covering cancellation analysis, demand/seasonality, revenue analysis, and statistical testing. I mirrored the same business questions in 23 MySQL queries using CTEs and window functions, built an Excel KPI workbook, designed a 3-page Power BI dashboard, and packaged everything into a Jupyter notebook that tells the full analytical story end-to-end. The headline finding: 37.1% of bookings cancel, worth about €16.7M in at-risk revenue, and it's heavily concentrated in Online TA and long-lead-time bookings."

## Explain the Complete Data Pipeline

1. **Raw ingestion**: `hotel_bookings.csv` (119,390 x 32) loaded with pandas.
2. **Data quality assessment**: missingness, duplicates, invalid guest counts, invalid ADR values, all quantified before any changes are made.
3. **Cleaning**: each column's missing/invalid values handled according to what that specific column means (e.g., `children` NaN → 0, `country` NaN → "Unknown" rather than guessed, exact-duplicate rows counted and *retained* since there's no booking ID to confirm they're accidental, zero-guest rows removed, negative ADR set to NaN only for revenue math).
4. **Feature engineering**: `total_guests`, `total_stay_nights`, `lead_time_category` (quartile-based), `season`, `arrival_date` (reconstructed from year/month/day), `potential_booking_revenue` (adr × nights), and cancellation-history flags.
5. **Output**: `hotel_bookings_cleaned.csv` (119,210 x 44) — the single source of truth used by every downstream script, the notebook, MySQL import, and Excel.

## Explain the Cancellation Analysis

I calculated cancellation rate as a simple `mean(is_canceled)` grouped by each dimension — hotel type, market segment, distribution channel, lead-time category, customer type, deposit type, season, and repeat-cancellation history. I deliberately used *associative* language throughout ("bookings with X show a higher association with cancellation") rather than causal claims, since this is observational data, not an experiment. The standout findings were the strong lead-time gradient (9.6% → 55.4% cancellation as lead time grows) and the counter-intuitive deposit-type result (Non-Refundable deposits actually show the *highest* cancellation rate at 99.4%), which I flagged explicitly as worth investigating rather than smoothing over.

## Explain the Revenue Risk Matrix

I combined two metrics at the market-segment level: total potential revenue (`adr x nights`, summed) and cancellation rate. I used the **median** of each metric across segments (with at least 200 bookings, to avoid noise from tiny segments) as the classification threshold — not arbitrary hardcoded cutoffs. Segments above both medians are "High Revenue Risk," above-revenue/below-cancellation is "Stable Revenue Segment," below-revenue/above-cancellation is "Growth Opportunity," and below both is "Low Priority." This let me show, quantitatively, that Online TA, Offline TA/TO, and Groups together represent the highest-risk revenue concentration.

## Explain the Demand Analysis

I aggregated bookings by arrival month across all years to find the seasonal shape of demand (August peak, January trough), then compared that shape between hotel types using the coefficient of variation, since it's mean-normalized. City Hotel demand is more seasonally volatile than Resort Hotel demand. I also built a 3-month moving average over the full monthly time series purely as a **descriptive historical trend line** — I was explicit in the code and docs that this is not a validated forecasting model, since I didn't want to overstate what a simple moving average can predict.

## Explain Why Python, MySQL, Excel, and Power BI Were Used Together

Each tool plays to its strength rather than duplicating the others:
- **Python** does the heavy lifting — cleaning, feature engineering, statistical testing, and generating the analytical visuals that require custom logic (like the Revenue Risk Matrix).
- **MySQL** demonstrates the ability to answer the same business questions using set-based SQL, including window functions for ranking and month-over-month trend analysis — a skill dashboard tools alone don't showcase.
- **Excel** provides a lightweight, universally-accessible KPI summary that a non-technical stakeholder could open without any tooling.
- **Power BI** turns the static findings into an interactive, filterable dashboard stakeholders can explore themselves (by hotel, season, segment) rather than reading a static report.

Together they show the full realistic toolkit a business/data analyst is expected to move between on the job.

## Important SQL Concepts Used

- **CTEs (`WITH ... AS`)**: used to pre-aggregate monthly bookings before applying window functions (query 19, 20) and to build the segment-level Business Risk Summary (query 21) cleanly in two logical steps.
- **Window Functions**:
  - `RANK()` — ranks market segments within each hotel by booking volume (query 18); ties share the same rank and skip the next rank number.
  - `DENSE_RANK()` — ranks segments by cancellation risk within each hotel (query 18); ties share the same rank without skipping numbers, which matters when segments have identical cancellation rates.
  - `LAG()` — pulls the previous month's booking count to compute month-over-month change (query 19).
  - `LEAD()` — pulls the *next* month's booking count alongside the current row, useful for spotting upcoming demand shifts (query 20).
- **`CASE WHEN`**: used to bucket cancellation rate into risk tiers (query 16) and to build the Revenue Risk Matrix classification directly in SQL (query 21), mirroring the Python logic.

---

## 25+ Interview Questions and Answers

**Q1. Why did you choose this dataset?**
A: It's a real, publicly available operational dataset (Kaggle's Hotel Booking Demand) with genuine data quality issues — missing values, duplicates, invalid records — which let me demonstrate a realistic cleaning process rather than working with a pre-cleaned toy dataset.

**Q2. What was the overall cancellation rate you found?**
A: 37.08% across the 119,210 cleaned bookings (44,199 cancellations).

**Q3. How did you handle the ~32,000 duplicate-looking rows?**
A: I detected and reported them (31,994 exact full-row duplicates, ~26.8% of the raw data) but I did **not** delete them. This dataset has no booking ID / primary key, so there's no reliable way to prove an identical-looking row is an accidental duplicate rather than a second, legitimate booking that happens to share every attribute value. Blanket-dropping over a quarter of the data on an unverifiable assumption would risk silently distorting every downstream KPI, so I kept every row and documented the reasoning directly in `data_cleaning.py`.

**Q4. Doesn't keeping that many duplicate-looking rows concern you?**
A: It's a real limitation I call out explicitly (see README Limitations) — if some of those rows genuinely are accidental duplicates, KPIs like total bookings and total potential revenue would be modestly inflated. But the alternative — deleting 27% of the dataset based on a guess — is a bigger risk with a dataset that has no key to verify the guess. I'd rather be transparent about an unresolved ambiguity than silently "fix" it in a way I can't justify.

**Q5. How did you handle the missing `agent` and `company` columns?**
A: Rather than imputing IDs I don't have any basis for, I converted them into `has_agent` and `has_company` boolean flags. The missingness itself is meaningful — it likely means no agent/company was involved — so encoding presence/absence preserves that signal without fabricating IDs.

**Q6. What's the difference between your lead time categories?**
A: They're built from the dataset's own quartile distribution rather than arbitrary day cutoffs: Last Minute (0-7 days), Short Lead (8 to the median, ~49 days), Medium Lead (median to Q3, ~50-125 days), Long Lead (125+ days).

**Q7. Why does cancellation rate increase with lead time?**
A: The data shows a strong positive association (correlation 0.293, and a highly significant t-test between canceled/non-canceled groups), but I'm careful to describe it as an association. A plausible explanation is that bookings made far in advance have more time for plans to change, but I don't claim that mechanism is proven by this dataset alone.

**Q8. What surprised you most in the analysis?**
A: The deposit type result — Non-Refundable deposit bookings cancel at 99.4%, far higher than No-Deposit bookings (28.4%). That runs against the common assumption that a non-refundable deposit discourages cancellation, and I chose to flag it explicitly rather than explain it away, since I don't have enough information in this dataset to know the underlying cause.

**Q9. How did you calculate "potential revenue"?**
A: `adr` (Average Daily Rate) multiplied by `total_stay_nights` for each booking. I labeled every revenue figure "potential" throughout the project because this dataset has no separate "amount paid" or invoice field — it's a reasonable proxy, not confirmed realized revenue.

**Q10. How much revenue is at risk from cancellations?**
A: An estimated €16.73M out of €42.71M in total potential booking revenue — about 39.2%.

**Q11. Which market segment carries the most revenue risk?**
A: Online Travel Agency (Online TA) bookings — they're both the highest-volume segment (47.3% of bookings) and carry the largest single share of revenue at risk (about €10.23M), even though Groups has a higher cancellation rate (61.1%) at much lower volume.

**Q12. How did you build the Revenue Risk Matrix?**
A: I computed total potential revenue and cancellation rate per market segment (filtering to segments with at least 200 bookings for reliability), then used the median of each metric as the classification threshold, avoiding arbitrary hardcoded cutoffs. Segments were classified into High Revenue Risk, Stable Revenue Segment, Growth Opportunity, or Low Priority Segment based on which side of both medians they fell on.

**Q13. Why medians instead of means for the thresholds?**
A: Revenue and cancellation-rate distributions across only 7-8 segments can be skewed by one or two large segments; the median is more robust to that skew than the mean when there are so few groups.

**Q14. What statistical tests did you run, and why?**
A: A chi-square test of independence for hotel type vs. cancellation and for deposit type vs. cancellation (both categorical vs. categorical), and an independent-samples t-test comparing mean lead time between canceled and non-canceled bookings (numerical vs. categorical). All three came back statistically significant (p < 0.001).

**Q15. Does a significant p-value mean the effect is large or important?**
A: No — with a dataset this large (tens of thousands of rows), even small differences become statistically significant. I paired every p-value with the actual effect size (e.g., percentage-point gaps in cancellation rate) so the business magnitude is clear, not just statistical significance.

**Q16. How did you detect outliers in ADR?**
A: The IQR method — values beyond 1.5x the interquartile range above Q3 or below Q1. About 3.24% of bookings with valid ADR were flagged as outliers, visualized in a boxplot.

**Q17. Which hotel type has stronger seasonal demand swings?**
A: City Hotel, based on a higher coefficient of variation (0.277 vs. 0.238 for Resort Hotel) in monthly booking volume — CV normalizes for the fact the two hotels have different average volumes.

**Q18. Did you build a forecasting model?**
A: No predictive/trained forecasting model — the brief called for a "demonstration" only where genuinely supported. I built a 3-month moving average over historical monthly bookings as a descriptive trend line, and was explicit in the code comments and outputs that it's not a validated forecast.

**Q19. Why MySQL and not PostgreSQL?**
A: The project spec required MySQL specifically. I used MySQL 8.0-compatible syntax throughout, including window functions (`RANK`, `DENSE_RANK`, `LAG`, `LEAD`) which are supported from MySQL 8.0 onward.

**Q20. Walk me through one of your window function queries.**
A: Query 19 builds a CTE aggregating bookings by year and month, then applies `LAG()` ordered by year and month number to pull the prior month's booking count into the same row, letting me compute month-over-month change in a single pass without a self-join.

**Q21. Why does your project avoid an RFM (Recency-Frequency-Monetary) customer segmentation?**
A: The brief was explicit that this project needed to be clearly different from a generic retail/RFM analytics project. Instead, I focused on booking-behavior segmentation — market segment, distribution channel, customer type, repeat-guest status — which is more directly relevant to a hotel's actual booking funnel.

**Q22. What would you do differently with more time or better data?**
A: I'd want an actual "amount paid" or invoice-level revenue field instead of estimating from ADR x nights, and a booking ID to resolve the duplicate-row ambiguity with certainty — right now those 31,994 duplicate-looking rows are retained rather than dropped precisely because I can't confirm which side of that ambiguity they fall on. I'd also want to test an actual predictive cancellation model (e.g., logistic regression or gradient boosting) with proper train/test validation, which was out of scope for this descriptive/BI-focused project.

**Q23. How would a hotel operationally use your Non-Refundable deposit finding?**
A: Rather than assuming the policy is working as intended, I'd recommend the hotel investigate who is actually making Non-Refundable bookings and why they still cancel at such a high rate — it could reveal a process issue (e.g., ease of "no-show" cancellation despite deposit terms) worth fixing before rolling the policy out further.

**Q24. How confident are you in the "Unknown" country label instead of imputing a value?**
A: Very — guessing a guest's country based on other columns would fabricate data the dataset doesn't support, and 0.4% of rows carrying an explicit "Unknown" label doesn't meaningfully distort country-level analysis, which I limited to countries with real values.

**Q25. What's the single most actionable recommendation from this project?**
A: Focus retention effort on Online TA bookings with long lead times specifically — it's the single largest, most identifiable concentration of both booking volume and revenue-at-risk, so even a modest improvement there has the largest expected payoff of any segment-level intervention I found.

**Q26. How did you validate that your cleaned dataset didn't introduce errors?**
A: I compared row counts and key aggregate stats (cancellation rate, ADR distribution) before and after cleaning to confirm the cleaning steps didn't distort the underlying business patterns, and re-ran the full pipeline end-to-end (including executing the Jupyter notebook) to confirm every script runs without errors on the final cleaned file.

**Q27. Why build both a Jupyter notebook AND separate Python scripts?**
A: The scripts (`src/*.py`) are modular, reusable, and independently runnable — suited for a production-style pipeline or automation. The notebook tells the same story as a single narrative document, which is better for walking a reviewer or interviewer through the reasoning step by step.
