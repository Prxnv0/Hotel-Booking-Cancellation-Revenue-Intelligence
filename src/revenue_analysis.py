"""
Hotel Booking Cancellation & Revenue Intelligence Analytics
------------------------------------------------------------
Script: revenue_analysis.py
Purpose: Analyze revenue-related metrics using the ADR (Average Daily
Rate) column and engineered `potential_booking_revenue`. Calculates
revenue at risk from cancellations, revenue by hotel type/segment/
season, and builds the data-driven Revenue Risk Matrix.

IMPORTANT ASSUMPTION: `potential_booking_revenue` = adr * total_stay_nights.
This is an ESTIMATE of booking value, not confirmed realized hotel
revenue (no separate "amount paid" or invoicing field exists in this
dataset). All figures in this script should be read as "potential" or
"at-risk" revenue, not audited financial revenue.

Run independently with (after running data_cleaning.py first):
    python src/revenue_analysis.py
"""

import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

DATA_PATH = os.path.join("data", "processed", "hotel_bookings_cleaned.csv")
OUT_DIR = os.path.join("images", "generated_visualizations")

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110


def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def run_analysis():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = load_data()

    print("=" * 70)
    print("REVENUE AND OCCUPANCY ANALYSIS")
    print("(all revenue figures are ESTIMATES: adr x nights stayed)")
    print("=" * 70)

    valid = df.dropna(subset=["adr"])  # exclude the rows with cleaned-out negative ADR

    total_potential_revenue = valid["potential_booking_revenue"].sum()
    realized_revenue = valid.loc[valid["is_canceled"] == 0, "potential_booking_revenue"].sum()
    at_risk_revenue = valid.loc[valid["is_canceled"] == 1, "potential_booking_revenue"].sum()

    print(f"\nTotal potential booking revenue (all bookings): €{total_potential_revenue:,.0f}")
    print(f"Potential revenue from completed (non-canceled) bookings: €{realized_revenue:,.0f}")
    print(f"Potential revenue at risk from canceled bookings: €{at_risk_revenue:,.0f}")
    print(f"Share of potential revenue at risk: {at_risk_revenue/total_potential_revenue:.1%}")

    # --- ADR by hotel type ---
    adr_hotel = valid.groupby("hotel")["adr"].mean().round(2)
    print("\n--- Average Daily Rate (ADR) by Hotel Type ---")
    print(adr_hotel.to_string())

    plt.figure(figsize=(7, 5))
    ax = sns.barplot(x=adr_hotel.index, y=adr_hotel.values, hue=adr_hotel.index, palette="flare", legend=False)
    ax.set_title("Average Daily Rate (ADR) by Hotel Type", fontsize=13, fontweight="bold")
    ax.set_ylabel("Average Daily Rate (€)")
    ax.set_xlabel("")
    for p in ax.patches:
        ax.annotate(f"€{p.get_height():.0f}", (p.get_x() + p.get_width()/2, p.get_height()),
                    ha="center", va="bottom", fontsize=10)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "adr_by_hotel_type.png")
    plt.savefig(path)
    plt.close()
    print(f"Saved chart: {path}")

    # --- Revenue at risk by market segment ---
    risk_by_segment = valid[valid["is_canceled"] == 1].groupby("market_segment")["potential_booking_revenue"].sum().sort_values(ascending=False)
    print("\n--- Potential revenue at risk (canceled bookings) by Market Segment ---")
    print(risk_by_segment.round(0).to_string())

    plt.figure(figsize=(9, 5))
    ax = sns.barplot(x=risk_by_segment.index, y=risk_by_segment.values, hue=risk_by_segment.index, palette="rocket", legend=False)
    ax.set_title("Potential Revenue at Risk from Cancellations, by Market Segment", fontsize=12, fontweight="bold")
    ax.set_ylabel("Revenue at Risk (€)")
    ax.set_xlabel("")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "revenue_at_risk_by_segment.png")
    plt.savefig(path)
    plt.close()
    print(f"Saved chart: {path}")

    # --- Revenue by season ---
    rev_season = valid.groupby("season")["potential_booking_revenue"].sum().sort_values(ascending=False)
    print("\n--- Potential booking revenue by Season ---")
    print(rev_season.round(0).to_string())

    # --- ADR by market segment ---
    adr_segment = valid.groupby("market_segment")["adr"].mean().sort_values(ascending=False).round(2)
    print("\n--- Average Daily Rate by Market Segment ---")
    print(adr_segment.to_string())

    # --- Occupancy proxy: total room-nights booked (non-canceled) by month ---
    room_nights = valid.loc[valid["is_canceled"] == 0].groupby("arrival_date_month")["total_stay_nights"].sum()
    print("\n--- Total occupied room-nights by arrival month (non-canceled bookings) ---")
    print(room_nights.sort_values(ascending=False).head(5).to_string())
    print("(Top 5 months shown; full monthly detail available in the processed dataset.)")

    print("\nRevenue and occupancy analysis complete.")
    return {
        "total_potential_revenue": total_potential_revenue,
        "at_risk_revenue": at_risk_revenue,
        "adr_by_hotel": adr_hotel,
        "risk_by_segment": risk_by_segment,
    }


if __name__ == "__main__":
    run_analysis()
