"""
Hotel Booking Cancellation & Revenue Intelligence Analytics
------------------------------------------------------------
Script: demand_analysis.py
Purpose: Analyze hotel demand patterns and seasonality - when demand
peaks, which hotel type experiences stronger seasonal swings, and a
simple historical-trend forecasting demonstration.

Run independently with (after running data_cleaning.py first):
    python src/demand_analysis.py
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

DATA_PATH = os.path.join("data", "processed", "hotel_bookings_cleaned.csv")
OUT_DIR = os.path.join("images", "generated_visualizations")

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110

MONTH_ORDER = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["arrival_date_month"] = pd.Categorical(df["arrival_date_month"], categories=MONTH_ORDER, ordered=True)
    return df


def run_analysis():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = load_data()

    print("=" * 70)
    print("DEMAND AND SEASONALITY ANALYSIS")
    print("=" * 70)

    # --- Bookings by month (all years combined - historical pattern) ---
    monthly = df.groupby("arrival_date_month", observed=True).size().reindex(MONTH_ORDER)
    print("\n--- Total historical bookings by arrival month (all years combined) ---")
    print(monthly.to_string())

    plt.figure(figsize=(11, 5))
    ax = sns.barplot(x=monthly.index, y=monthly.values, hue=monthly.index, palette="mako", legend=False)
    ax.set_title("Historical Booking Volume by Arrival Month (All Years Combined)", fontsize=13, fontweight="bold")
    ax.set_ylabel("Number of Bookings")
    ax.set_xlabel("")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "demand_by_month.png")
    plt.savefig(path)
    plt.close()
    print(f"Saved chart: {path}")

    # --- Bookings by month split by hotel type ---
    monthly_hotel = df.groupby(["arrival_date_month", "hotel"], observed=True).size().unstack().reindex(MONTH_ORDER)
    plt.figure(figsize=(11, 5))
    monthly_hotel.plot(kind="line", marker="o", ax=plt.gca())
    plt.title("Monthly Booking Volume by Hotel Type", fontsize=13, fontweight="bold")
    plt.ylabel("Number of Bookings")
    plt.xlabel("")
    plt.xticks(range(len(MONTH_ORDER)), MONTH_ORDER, rotation=35, ha="right")
    plt.legend(title="Hotel")
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "demand_by_month_hotel_type.png")
    plt.savefig(path)
    plt.close()
    print(f"Saved chart: {path}")

    # Coefficient of variation per hotel type - which hotel has stronger seasonality
    cv = (monthly_hotel.std() / monthly_hotel.mean()).sort_values(ascending=False)
    print("\n--- Seasonal variability by hotel type (coefficient of variation) ---")
    print(cv.to_string())
    print("Higher CV = more seasonal swings in demand.")

    # --- Year-over-year trend (only full historical range available: 2015-2017 partial) ---
    yearly = df.groupby("arrival_date_year").size()
    print("\n--- Bookings by year (note: 2015 and 2017 are partial calendar years in this dataset) ---")
    print(yearly.to_string())

    # --- Peak vs low demand periods ---
    peak_month = monthly.idxmax()
    low_month = monthly.idxmin()
    print(f"\nPeak demand month (historical): {peak_month} ({monthly.max():,} bookings)")
    print(f"Lowest demand month (historical): {low_month} ({monthly.min():,} bookings)")

    # --- Simple historical trend / moving-average forecasting demonstration ---
    print("\n--- Forecasting demonstration (historical trend only, NOT a predictive model) ---")
    # Build a monthly time series using year+month combined, ordered chronologically
    df_ts = df.dropna(subset=["arrival_date"]).copy()
    df_ts["arrival_date"] = pd.to_datetime(df_ts["arrival_date"])
    df_ts["year_month"] = df_ts["arrival_date"].dt.to_period("M")
    ts = df_ts.groupby("year_month").size().sort_index()

    # 3-month simple moving average as a naive trend estimate
    ts_ma = ts.rolling(window=3).mean()

    plt.figure(figsize=(12, 5))
    plt.plot(ts.index.astype(str), ts.values, marker="o", label="Actual Monthly Bookings", linewidth=1.5)
    plt.plot(ts.index.astype(str), ts_ma.values, linestyle="--", label="3-Month Moving Average (Trend)", linewidth=2)
    plt.title("Historical Monthly Booking Volume with Trend Line", fontsize=13, fontweight="bold")
    plt.ylabel("Number of Bookings")
    plt.xlabel("")
    plt.xticks(rotation=90, fontsize=7)
    plt.legend()
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "demand_trend_moving_average.png")
    plt.savefig(path)
    plt.close()
    print(f"Saved chart: {path}")
    print("NOTE: This moving average is a descriptive historical trend line,")
    print("not a validated forecast of future bookings. No forward-looking")
    print("prediction beyond the observed date range is claimed.")

    print("\nDemand and seasonality analysis complete.")
    return {"monthly": monthly, "cv_by_hotel": cv, "yearly": yearly}


if __name__ == "__main__":
    run_analysis()
