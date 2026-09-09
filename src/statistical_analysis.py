"""
Hotel Booking Cancellation & Revenue Intelligence Analytics
------------------------------------------------------------
Script: statistical_analysis.py
Purpose: Statistical analysis supporting the business narrative -
correlation analysis, group comparisons (chi-square), distribution /
outlier analysis, and the data-driven Revenue Risk Matrix (segment
classification using quartile thresholds).

Run independently with (after running data_cleaning.py first):
    python src/statistical_analysis.py
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

DATA_PATH = os.path.join("data", "processed", "hotel_bookings_cleaned.csv")
OUT_DIR = os.path.join("images", "generated_visualizations")

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110


def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def correlation_analysis(df: pd.DataFrame):
    print("\n--- Correlation Analysis (numerical variables vs is_canceled) ---")
    num_cols = ["lead_time", "adr", "total_stay_nights", "total_guests",
                "previous_cancellations", "booking_changes", "total_of_special_requests",
                "days_in_waiting_list", "is_canceled"]
    corr_matrix = df[num_cols].corr()
    print(corr_matrix["is_canceled"].drop("is_canceled").sort_values(ascending=False).round(3).to_string())

    plt.figure(figsize=(9, 7))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", center=0, square=True)
    plt.title("Correlation Matrix: Numerical Booking Variables", fontsize=12, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "correlation_matrix.png")
    plt.savefig(path)
    plt.close()
    print(f"Saved chart: {path}")
    print("\nInterpretation: total_of_special_requests and booking_changes show")
    print("a negative association with cancellation (more engaged bookings cancel")
    print("less often); lead_time shows a positive association. Correlation does")
    print("not establish causation.")
    return corr_matrix


def group_comparison_tests(df: pd.DataFrame):
    print("\n--- Chi-Square Test of Independence: Hotel Type vs Cancellation ---")
    ct = pd.crosstab(df["hotel"], df["is_canceled"])
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    print(f"Chi2 = {chi2:.2f}, p-value = {p:.6f}, dof = {dof}")
    print("Interpretation: " + (
        "The relationship between hotel type and cancellation is statistically "
        "significant (p < 0.05); cancellation behavior differs meaningfully "
        "between City and Resort hotels." if p < 0.05 else
        "No statistically significant relationship detected."))

    print("\n--- Chi-Square Test: Deposit Type vs Cancellation ---")
    ct2 = pd.crosstab(df["deposit_type"], df["is_canceled"])
    chi2b, pb, dofb, _ = stats.chi2_contingency(ct2)
    print(f"Chi2 = {chi2b:.2f}, p-value = {pb:.6f}, dof = {dofb}")
    print("Interpretation: " + (
        "Deposit type is statistically significantly associated with cancellation "
        "(p < 0.05). Notably, Non-Refundable deposits show a much HIGHER cancellation "
        "rate in this dataset than No-Deposit bookings - a counter-intuitive finding "
        "worth flagging rather than smoothing over, since it runs against the common "
        "assumption that deposits discourage cancellation." if pb < 0.05 else
        "No statistically significant relationship detected."))

    print("\n--- Independent samples t-test: Lead Time, Canceled vs Not Canceled ---")
    canceled_lead = df.loc[df["is_canceled"] == 1, "lead_time"]
    not_canceled_lead = df.loc[df["is_canceled"] == 0, "lead_time"]
    t_stat, p_val = stats.ttest_ind(canceled_lead, not_canceled_lead, equal_var=False)
    print(f"Mean lead time (canceled): {canceled_lead.mean():.1f} days")
    print(f"Mean lead time (not canceled): {not_canceled_lead.mean():.1f} days")
    print(f"t = {t_stat:.2f}, p-value = {p_val:.6f}")


def outlier_analysis(df: pd.DataFrame):
    print("\n--- Outlier Analysis: ADR (IQR method) ---")
    valid_adr = df["adr"].dropna()
    q1, q3 = valid_adr.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = valid_adr[(valid_adr < lower) | (valid_adr > upper)]
    print(f"IQR bounds: [{lower:.2f}, {upper:.2f}]")
    print(f"Outlier count: {len(outliers):,} ({len(outliers)/len(valid_adr):.2%} of bookings with valid ADR)")

    plt.figure(figsize=(7, 5))
    sns.boxplot(y=valid_adr, color="#4C72B0")
    plt.title("ADR Distribution with Outliers (IQR Method)", fontsize=12, fontweight="bold")
    plt.ylabel("Average Daily Rate (€)")
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "adr_outlier_boxplot.png")
    plt.savefig(path)
    plt.close()
    print(f"Saved chart: {path}")


def revenue_risk_matrix(df: pd.DataFrame):
    print("\n--- REVENUE RISK MATRIX (Market Segment level) ---")
    valid = df.dropna(subset=["adr"])
    seg = valid.groupby("market_segment").agg(
        booking_count=("is_canceled", "count"),
        cancellation_rate=("is_canceled", "mean"),
        total_potential_revenue=("potential_booking_revenue", "sum"),
    ).reset_index()
    seg = seg[seg["booking_count"] >= 200]  # exclude segments too small to classify reliably

    vol_median = seg["total_potential_revenue"].median()
    cxl_median = seg["cancellation_rate"].median()

    def classify(row):
        high_value = row["total_potential_revenue"] >= vol_median
        high_risk = row["cancellation_rate"] >= cxl_median
        if high_value and high_risk:
            return "High Revenue Risk"
        elif high_value and not high_risk:
            return "Stable Revenue Segment"
        elif not high_value and high_risk:
            return "Growth Opportunity (High Cancellation, Lower Volume)"
        else:
            return "Low Priority Segment"

    seg["risk_classification"] = seg.apply(classify, axis=1)
    seg = seg.sort_values("total_potential_revenue", ascending=False)
    seg["total_potential_revenue"] = seg["total_potential_revenue"].round(0)
    seg["cancellation_rate_pct"] = (seg["cancellation_rate"] * 100).round(1)
    print(seg[["market_segment", "booking_count", "cancellation_rate_pct",
               "total_potential_revenue", "risk_classification"]].to_string(index=False))
    print(f"\nThresholds used - Revenue median: €{vol_median:,.0f} | Cancellation rate median: {cxl_median:.1%}")

    # Scatter plot: revenue vs cancellation rate, sized by booking count
    plt.figure(figsize=(9, 6))
    scatter = plt.scatter(seg["cancellation_rate_pct"], seg["total_potential_revenue"],
                           s=seg["booking_count"] / 20, alpha=0.6, c=seg["cancellation_rate_pct"], cmap="RdYlGn_r")
    for _, row in seg.iterrows():
        plt.annotate(row["market_segment"], (row["cancellation_rate_pct"], row["total_potential_revenue"]),
                     fontsize=9, xytext=(5, 5), textcoords="offset points")
    plt.axvline(cxl_median * 100, linestyle="--", color="gray", linewidth=1)
    plt.axhline(vol_median, linestyle="--", color="gray", linewidth=1)
    plt.xlabel("Cancellation Rate (%)")
    plt.ylabel("Total Potential Revenue (€)")
    plt.title("Revenue Risk Matrix: Market Segments\n(bubble size = booking volume)", fontsize=12, fontweight="bold")
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "revenue_risk_matrix.png")
    plt.savefig(path)
    plt.close()
    print(f"Saved chart: {path}")

    return seg


def run_analysis():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = load_data()
    print("=" * 70)
    print("STATISTICAL ANALYSIS")
    print("=" * 70)
    correlation_analysis(df)
    group_comparison_tests(df)
    outlier_analysis(df)
    risk_matrix = revenue_risk_matrix(df)
    print("\nStatistical analysis complete.")
    return risk_matrix


if __name__ == "__main__":
    run_analysis()
