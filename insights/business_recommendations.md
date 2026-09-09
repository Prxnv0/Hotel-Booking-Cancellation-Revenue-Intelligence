# Business Recommendations
### Hotel Booking Cancellation & Revenue Intelligence Analytics
**Author:** Pranav Singh

---

## Executive Summary

Across 119,210 cleaned hotel booking records (City Hotel and Resort Hotel, 2015-2017), the overall cancellation rate is **37.1%**, representing an estimated **€16.73M in potential revenue at risk** out of **€42.71M** in total potential booking revenue (39.2%). Cancellation risk is not evenly distributed — it concentrates heavily in a small number of identifiable segments: Online Travel Agency bookings, long-lead-time reservations, and guests with a prior cancellation history. These concentrations mean targeted interventions, rather than blanket policy changes, are likely to deliver the best return.

---

## Major Cancellation Insights

- **Overall cancellation rate: 37.08%** (44,199 of 119,210 bookings).
- **Hotel type matters**: City Hotel cancels at 41.79% vs. Resort Hotel at 27.77% — a statistically significant difference (chi-square p < 0.001).
- **Lead time is the strongest behavioral signal**: cancellation rate climbs from 9.60% (Last Minute, 0-7 days) to 32.80% (Short Lead), 42.73% (Medium Lead), and 55.41% (Long Lead, 162+ days).
- **Market segment concentration**: Online TA bookings (47.3% of all volume) cancel at 36.76%, far above Corporate (18.76%) and Direct (15.37%) bookings.
- **Deposit type paradox**: Non-Refundable bookings cancel at 99.36%, vastly higher than No-Deposit (28.40%). This is a genuinely counter-intuitive finding — the data does not support the common assumption that non-refundable deposits reliably discourage cancellation, and it warrants investigation into how this deposit type is actually used (e.g., speculative holds, third-party booking behavior) rather than being treated as a policy success.
- **Repeat cancellation behavior**: guests with previous cancellations cancel again at 91.68%, versus 33.94% for guests with no cancellation history.
- **Engagement signals reduce cancellation**: `total_of_special_requests` and `booking_changes` both show a negative correlation with cancellation, suggesting more "engaged" bookings are more likely to be honored.

## Demand Insights

- **Peak demand month: August** (13,861 historical bookings); **lowest demand month: January** (5,921 bookings).
- Bookings more than double from the January trough to the August peak, with July and August together accounting for the two highest-volume months.
- **City Hotel demand is more seasonally volatile** (coefficient of variation 0.277) than Resort Hotel (0.238), meaning City Hotel operations face sharper seasonal swings in staffing and inventory needs.
- **Summer is simultaneously the peak-demand and highest-cancellation season** (38.76%), which concentrates revenue risk exactly when occupancy planning matters most.

## Hotel Performance Insights

| Metric | City Hotel | Resort Hotel |
|---|---|---|
| Total Bookings | 79,163 | 40,047 |
| Cancellation Rate | 41.79% | 27.77% |
| Average Daily Rate | €105.50 | €94.99 |

City Hotel carries more volume and a higher ADR, but also a meaningfully higher cancellation rate — its higher revenue potential is offset by higher revenue-risk exposure.

## Revenue Risks

- **Total potential booking revenue: €42,714,213**; **revenue at risk from cancellations: €16,727,237 (39.2%)**.
- **Online TA segment alone accounts for ~€10.23M of revenue at risk** — roughly 61% of total revenue at risk sits in this one distribution channel.
- Revenue Risk Matrix classification (median-based thresholds on booking volume and cancellation rate):

| Market Segment | Classification |
|---|---|
| Online TA | High Revenue Risk |
| Offline TA/TO | High Revenue Risk |
| Groups | High Revenue Risk |
| Direct | Stable Revenue Segment |
| Corporate | Low Priority Segment |
| Aviation | Growth Opportunity (High Cancellation, Lower Volume) |
| Complementary | Low Priority Segment |

## High-Risk Booking Segments

1. Online TA bookings with long lead times (162+ days) — the single largest concentration of cancellation risk and revenue exposure.
2. Non-Refundable deposit bookings — unexpectedly the highest-cancellation deposit category.
3. Guests with any history of prior cancellations — nearly 2.7x the base cancellation rate.
4. Summer-season Online TA bookings — peak demand overlapping peak cancellation risk.

## Business Opportunities

- **Corporate and Complementary segments** show the lowest cancellation rates (18.76% and 12.23%) — strong candidates for relationship-based retention and account growth investment.
- **Last-minute bookings (0-7 day lead time)** convert reliably (90.4% completion) — there may be room to grow this segment through targeted late-availability promotions with low downside risk.
- **Aviation segment** is small in volume but shows a distinct risk profile (22.1% cancellation) worth monitoring as it scales.

## Recommended Actions

1. **Reassess the Non-Refundable deposit policy.** Investigate why this category shows the highest cancellation rate in the dataset before assuming it is functioning as a retention tool; consider a review of how and when it is offered.
2. **Apply differentiated confirmation/reminder workflows by lead time.** Bookings made 90+ days in advance could receive proactive re-confirmation touchpoints as the stay date approaches, since this is where cancellation risk concentrates.
3. **Prioritize Online TA channel management.** Given this single channel represents roughly 61% of revenue at risk, even a modest reduction in its cancellation rate would have an outsized impact on total realized revenue.
4. **Flag repeat-cancellation guests at booking time.** A simple internal flag (already engineered in this project as `has_prior_cancellation_history`) could trigger a different deposit or confirmation policy for guests with a cancellation history.
5. **Plan Summer staffing and overbooking buffers around both peak demand and peak cancellation risk simultaneously** — the same season that requires the most operational capacity also has the highest cancellation churn to plan around.
6. **Encourage booking engagement** (special requests, modifications) where possible, e.g., through early post-booking communication, since engaged bookings show a lower cancellation association.

---

*All figures above are estimates derived from `adr x nights stayed` for the cleaned analytical dataset and are labeled as "potential" revenue, not confirmed realized/invoiced hotel revenue. See `README.md` → Limitations for further detail.*
