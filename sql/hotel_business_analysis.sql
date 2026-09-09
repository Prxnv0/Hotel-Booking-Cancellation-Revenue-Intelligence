-- =====================================================================
-- Hotel Booking Cancellation & Revenue Intelligence Analytics
-- File: hotel_business_analysis.sql
-- Purpose: Business analysis queries against the `bookings` table.
-- Engine: MySQL 8.0+ (uses CTEs, window functions - RANK, DENSE_RANK,
--         LAG, LEAD - and CASE WHEN throughout)
-- =====================================================================

USE hotel_booking_analytics;

-- ---------------------------------------------------------------------
-- 1. Overall Booking KPIs
-- ---------------------------------------------------------------------
SELECT
    COUNT(*)                                            AS total_bookings,
    SUM(is_canceled)                                     AS total_cancellations,
    ROUND(AVG(is_canceled) * 100, 2)                     AS cancellation_rate_pct,
    ROUND(AVG(lead_time), 1)                             AS avg_lead_time_days,
    ROUND(AVG(total_stay_nights), 1)                     AS avg_stay_nights,
    ROUND(AVG(adr), 2)                                   AS avg_daily_rate
FROM bookings;

-- ---------------------------------------------------------------------
-- 2. Overall Cancellation Rate (explicit numerator/denominator view)
-- ---------------------------------------------------------------------
SELECT
    SUM(CASE WHEN is_canceled = 1 THEN 1 ELSE 0 END)              AS canceled_bookings,
    SUM(CASE WHEN is_canceled = 0 THEN 1 ELSE 0 END)              AS completed_bookings,
    COUNT(*)                                                       AS total_bookings,
    ROUND(SUM(CASE WHEN is_canceled = 1 THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS cancellation_rate_pct
FROM bookings;

-- ---------------------------------------------------------------------
-- 3. Cancellation Rate by Hotel Type
-- ---------------------------------------------------------------------
SELECT
    hotel,
    COUNT(*)                                    AS total_bookings,
    SUM(is_canceled)                            AS canceled_bookings,
    ROUND(AVG(is_canceled) * 100, 2)            AS cancellation_rate_pct
FROM bookings
GROUP BY hotel
ORDER BY cancellation_rate_pct DESC;

-- ---------------------------------------------------------------------
-- 4. Cancellation Rate by Market Segment
-- ---------------------------------------------------------------------
SELECT
    market_segment,
    COUNT(*)                            AS total_bookings,
    ROUND(AVG(is_canceled) * 100, 2)    AS cancellation_rate_pct
FROM bookings
GROUP BY market_segment
HAVING COUNT(*) >= 100
ORDER BY cancellation_rate_pct DESC;

-- ---------------------------------------------------------------------
-- 5. Cancellation Rate by Distribution Channel
-- ---------------------------------------------------------------------
SELECT
    distribution_channel,
    COUNT(*)                            AS total_bookings,
    ROUND(AVG(is_canceled) * 100, 2)    AS cancellation_rate_pct
FROM bookings
GROUP BY distribution_channel
ORDER BY cancellation_rate_pct DESC;

-- ---------------------------------------------------------------------
-- 6. Booking Trends by Month (all years combined)
-- ---------------------------------------------------------------------
SELECT
    arrival_date_month,
    arrival_month_num,
    COUNT(*)  AS total_bookings
FROM bookings
GROUP BY arrival_date_month, arrival_month_num
ORDER BY arrival_month_num;

-- ---------------------------------------------------------------------
-- 7. Hotel Demand Comparison (bookings and share of total)
-- ---------------------------------------------------------------------
SELECT
    hotel,
    COUNT(*) AS total_bookings,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM bookings), 2) AS pct_of_total_bookings
FROM bookings
GROUP BY hotel;

-- ---------------------------------------------------------------------
-- 8. Average Lead Time by Hotel Type
-- ---------------------------------------------------------------------
SELECT
    hotel,
    ROUND(AVG(lead_time), 1)  AS avg_lead_time_days,
    ROUND(STDDEV(lead_time), 1) AS stddev_lead_time
FROM bookings
GROUP BY hotel;

-- ---------------------------------------------------------------------
-- 9. Longest Lead Time Booking Segments (top 10 by average lead time,
--    market segments with sufficient volume)
-- ---------------------------------------------------------------------
SELECT
    market_segment,
    COUNT(*)                   AS total_bookings,
    ROUND(AVG(lead_time), 1)   AS avg_lead_time_days
FROM bookings
GROUP BY market_segment
HAVING COUNT(*) >= 100
ORDER BY avg_lead_time_days DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- 10. Repeat Customer Analysis
-- ---------------------------------------------------------------------
SELECT
    is_returning_guest,
    COUNT(*)                            AS total_bookings,
    ROUND(AVG(is_canceled) * 100, 2)    AS cancellation_rate_pct,
    ROUND(AVG(adr), 2)                  AS avg_daily_rate
FROM bookings
GROUP BY is_returning_guest;

-- ---------------------------------------------------------------------
-- 11. Deposit Type and Cancellation Analysis
-- ---------------------------------------------------------------------
SELECT
    deposit_type,
    COUNT(*)                            AS total_bookings,
    ROUND(AVG(is_canceled) * 100, 2)    AS cancellation_rate_pct
FROM bookings
GROUP BY deposit_type
ORDER BY cancellation_rate_pct DESC;

-- ---------------------------------------------------------------------
-- 12. Country-Level Booking Analysis (top 15 countries by volume)
-- ---------------------------------------------------------------------
SELECT
    country,
    COUNT(*)                            AS total_bookings,
    ROUND(AVG(is_canceled) * 100, 2)    AS cancellation_rate_pct
FROM bookings
WHERE country <> 'Unknown'
GROUP BY country
ORDER BY total_bookings DESC
LIMIT 15;

-- ---------------------------------------------------------------------
-- 13. Market Segment Performance (volume, cancellation, ADR combined)
-- ---------------------------------------------------------------------
SELECT
    market_segment,
    COUNT(*)                                            AS total_bookings,
    ROUND(AVG(is_canceled) * 100, 2)                    AS cancellation_rate_pct,
    ROUND(AVG(adr), 2)                                  AS avg_daily_rate,
    ROUND(SUM(potential_booking_revenue), 0)            AS total_potential_revenue
FROM bookings
WHERE adr IS NOT NULL
GROUP BY market_segment
ORDER BY total_potential_revenue DESC;

-- ---------------------------------------------------------------------
-- 14. Average Daily Rate (ADR) Analysis by Hotel Type and Season
-- ---------------------------------------------------------------------
SELECT
    hotel,
    season,
    ROUND(AVG(adr), 2)  AS avg_daily_rate,
    COUNT(*)             AS total_bookings
FROM bookings
WHERE adr IS NOT NULL
GROUP BY hotel, season
ORDER BY hotel, avg_daily_rate DESC;

-- ---------------------------------------------------------------------
-- 15. Seasonal Demand Analysis
-- ---------------------------------------------------------------------
SELECT
    season,
    COUNT(*)                            AS total_bookings,
    ROUND(AVG(is_canceled) * 100, 2)    AS cancellation_rate_pct
FROM bookings
GROUP BY season
ORDER BY total_bookings DESC;

-- ---------------------------------------------------------------------
-- 16. High Cancellation Risk Segments (CASE WHEN classification)
-- ---------------------------------------------------------------------
SELECT
    market_segment,
    COUNT(*) AS total_bookings,
    ROUND(AVG(is_canceled) * 100, 2) AS cancellation_rate_pct,
    CASE
        WHEN AVG(is_canceled) >= 0.35 THEN 'Very High Risk'
        WHEN AVG(is_canceled) >= 0.25 THEN 'High Risk'
        WHEN AVG(is_canceled) >= 0.15 THEN 'Moderate Risk'
        ELSE 'Low Risk'
    END AS risk_category
FROM bookings
GROUP BY market_segment
HAVING COUNT(*) >= 100
ORDER BY cancellation_rate_pct DESC;

-- ---------------------------------------------------------------------
-- 17. Revenue at Risk Analysis (potential revenue lost to cancellations,
--     by market segment)
-- ---------------------------------------------------------------------
SELECT
    market_segment,
    ROUND(SUM(CASE WHEN is_canceled = 1 THEN potential_booking_revenue ELSE 0 END), 0) AS revenue_at_risk,
    ROUND(SUM(potential_booking_revenue), 0)                                            AS total_potential_revenue,
    ROUND(
        SUM(CASE WHEN is_canceled = 1 THEN potential_booking_revenue ELSE 0 END)
        / NULLIF(SUM(potential_booking_revenue), 0) * 100, 2
    ) AS pct_revenue_at_risk
FROM bookings
WHERE adr IS NOT NULL
GROUP BY market_segment
ORDER BY revenue_at_risk DESC;

-- ---------------------------------------------------------------------
-- 18. Hotel Performance Ranking (using RANK and DENSE_RANK window functions)
-- ---------------------------------------------------------------------
SELECT
    hotel,
    market_segment,
    COUNT(*)                          AS total_bookings,
    ROUND(AVG(is_canceled) * 100, 2)  AS cancellation_rate_pct,
    RANK()       OVER (PARTITION BY hotel ORDER BY COUNT(*) DESC) AS booking_volume_rank,
    DENSE_RANK() OVER (PARTITION BY hotel ORDER BY AVG(is_canceled) DESC) AS cancellation_risk_rank
FROM bookings
GROUP BY hotel, market_segment
ORDER BY hotel, booking_volume_rank;

-- ---------------------------------------------------------------------
-- 19. Month-over-Month Booking Trends (using LAG window function)
-- ---------------------------------------------------------------------
WITH monthly_bookings AS (
    SELECT
        arrival_date_year,
        arrival_month_num,
        arrival_date_month,
        COUNT(*) AS total_bookings
    FROM bookings
    GROUP BY arrival_date_year, arrival_month_num, arrival_date_month
)
SELECT
    arrival_date_year,
    arrival_date_month,
    total_bookings,
    LAG(total_bookings) OVER (ORDER BY arrival_date_year, arrival_month_num) AS prev_month_bookings,
    total_bookings - LAG(total_bookings) OVER (ORDER BY arrival_date_year, arrival_month_num) AS month_over_month_change
FROM monthly_bookings
ORDER BY arrival_date_year, arrival_month_num;

-- ---------------------------------------------------------------------
-- 20. Forward-Looking Comparison Using LEAD (next month's booking volume
--     relative to current month, to help spot upcoming demand shifts)
-- ---------------------------------------------------------------------
WITH monthly_bookings AS (
    SELECT
        arrival_date_year,
        arrival_month_num,
        arrival_date_month,
        COUNT(*) AS total_bookings
    FROM bookings
    GROUP BY arrival_date_year, arrival_month_num, arrival_date_month
)
SELECT
    arrival_date_year,
    arrival_date_month,
    total_bookings,
    LEAD(total_bookings) OVER (ORDER BY arrival_date_year, arrival_month_num) AS next_month_bookings
FROM monthly_bookings
ORDER BY arrival_date_year, arrival_month_num;

-- ---------------------------------------------------------------------
-- 21. Business Risk Summary (CTE combining volume, cancellation and
--     revenue-at-risk into a single segment-level risk view)
-- ---------------------------------------------------------------------
WITH segment_summary AS (
    SELECT
        market_segment,
        COUNT(*)                                                                AS total_bookings,
        AVG(is_canceled)                                                        AS cancellation_rate,
        SUM(potential_booking_revenue)                                          AS total_potential_revenue,
        SUM(CASE WHEN is_canceled = 1 THEN potential_booking_revenue ELSE 0 END) AS revenue_at_risk
    FROM bookings
    WHERE adr IS NOT NULL
    GROUP BY market_segment
    HAVING COUNT(*) >= 100
)
SELECT
    market_segment,
    total_bookings,
    ROUND(cancellation_rate * 100, 2) AS cancellation_rate_pct,
    ROUND(total_potential_revenue, 0) AS total_potential_revenue,
    ROUND(revenue_at_risk, 0)         AS revenue_at_risk,
    CASE
        WHEN total_potential_revenue >= (SELECT AVG(total_potential_revenue) FROM segment_summary)
             AND cancellation_rate >= (SELECT AVG(cancellation_rate) FROM segment_summary)
            THEN 'High Revenue Risk'
        WHEN total_potential_revenue >= (SELECT AVG(total_potential_revenue) FROM segment_summary)
             AND cancellation_rate < (SELECT AVG(cancellation_rate) FROM segment_summary)
            THEN 'Stable Revenue Segment'
        WHEN total_potential_revenue < (SELECT AVG(total_potential_revenue) FROM segment_summary)
             AND cancellation_rate >= (SELECT AVG(cancellation_rate) FROM segment_summary)
            THEN 'Growth Opportunity'
        ELSE 'Low Priority Segment'
    END AS risk_classification
FROM segment_summary
ORDER BY revenue_at_risk DESC;

-- ---------------------------------------------------------------------
-- 22. Special Requests and Booking Changes vs Cancellation (engagement
--     signal analysis)
-- ---------------------------------------------------------------------
SELECT
    total_of_special_requests,
    COUNT(*)                            AS total_bookings,
    ROUND(AVG(is_canceled) * 100, 2)    AS cancellation_rate_pct
FROM bookings
GROUP BY total_of_special_requests
ORDER BY total_of_special_requests;

-- ---------------------------------------------------------------------
-- 23. Lead Time Category Breakdown with Revenue Impact
-- ---------------------------------------------------------------------
SELECT
    lead_time_category,
    COUNT(*)                                        AS total_bookings,
    ROUND(AVG(is_canceled) * 100, 2)                AS cancellation_rate_pct,
    ROUND(SUM(CASE WHEN is_canceled = 1 THEN potential_booking_revenue ELSE 0 END), 0) AS revenue_at_risk
FROM bookings
WHERE adr IS NOT NULL
GROUP BY lead_time_category
ORDER BY cancellation_rate_pct DESC;
