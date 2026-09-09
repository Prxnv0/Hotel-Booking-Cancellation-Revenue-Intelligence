"""
Hotel Booking Cancellation & Revenue Intelligence Analytics
------------------------------------------------------------
Script: cancellation_analysis.py
Purpose: Analyze booking cancellation patterns across hotel type, lead
time, market segment, distribution channel, customer type, deposit
type, season, and repeat-guest / prior-cancellation history. This is
the main analytical component of the project.

Run independently with (after running data_cleaning.py first):
    python src/cancellation_analysis.py
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


def cancellation_rate_by(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    grp = df.groupby(group_col)["is_canceled"].agg(["mean", "count"]).reset_index()
    grp.columns = [group_col, "cancellation_rate", "booking_count"]
    grp["cancellation_rate_pct"] = (grp["cancellation_rate"] * 100).round(2)
    return grp.sort_values("cancellation_rate", ascending=False)


def plot_bar(df: pd.DataFrame, x: str, y: str, title: str, filename: str,
             ylabel: str = "Cancellation Rate (%)", figsize=(9, 5)):
    plt.figure(figsize=figsize)
    order = df.sort_values(y, ascending=False)
    ax = sns.barplot(data=order, x=x, y=y, hue=x, palette="crest", legend=False)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.set_xlabel("")
    plt.xticks(rotation=35, ha="right")
    for p in ax.patches:
        h = p.get_height()
        if pd.notna(h):
            ax.annotate(f"{h:.1f}", (p.get_x() + p.get_width() / 2, h),
                        ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, filename)
    plt.savefig(path)
    plt.close()
    print(f"Saved chart: {path}")


def run_analysis():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = load_data()

    print("=" * 70)
    print("BOOKING CANCELLATION ANALYSIS")
    print("=" * 70)

    overall_rate = df["is_canceled"].mean()
    print(f"\nOverall cancellation rate: {overall_rate:.2%} "
          f"({df['is_canceled'].sum():,} of {len(df):,} bookings)")

    # --- By hotel type ---
    by_hotel = cancellation_rate_by(df, "hotel")
    print("\n--- Cancellation rate by Hotel Type ---")
    print(by_hotel.to_string(index=False))
    plot_bar(by_hotel, "hotel", "cancellation_rate_pct",
              "Cancellation Rate by Hotel Type", "cancellation_by_hotel_type.png")

    # --- By market segment ---
    by_segment = cancellation_rate_by(df, "market_segment")
    print("\n--- Cancellation rate by Market Segment ---")
    print(by_segment.to_string(index=False))
    plot_bar(by_segment, "market_segment", "cancellation_rate_pct",
              "Cancellation Rate by Market Segment", "cancellation_by_market_segment.png")

    # --- By distribution channel ---
    by_channel = cancellation_rate_by(df, "distribution_channel")
    print("\n--- Cancellation rate by Distribution Channel ---")
    print(by_channel.to_string(index=False))
    plot_bar(by_channel, "distribution_channel", "cancellation_rate_pct",
              "Cancellation Rate by Distribution Channel", "cancellation_by_distribution_channel.png")

    # --- By lead time category ---
    by_lead = cancellation_rate_by(df, "lead_time_category")
    print("\n--- Cancellation rate by Lead Time Category ---")
    print(by_lead.to_string(index=False))
    plot_bar(by_lead, "lead_time_category", "cancellation_rate_pct",
              "Cancellation Rate by Booking Lead Time Category", "cancellation_by_lead_time.png")

    # --- By customer type ---
    by_cust = cancellation_rate_by(df, "customer_type")
    print("\n--- Cancellation rate by Customer Type ---")
    print(by_cust.to_string(index=False))
    plot_bar(by_cust, "customer_type", "cancellation_rate_pct",
              "Cancellation Rate by Customer Type", "cancellation_by_customer_type.png")

    # --- By deposit type ---
    by_deposit = cancellation_rate_by(df, "deposit_type")
    print("\n--- Cancellation rate by Deposit Type ---")
    print(by_deposit.to_string(index=False))
    plot_bar(by_deposit, "deposit_type", "cancellation_rate_pct",
              "Cancellation Rate by Deposit Type", "cancellation_by_deposit_type.png")

    # --- By season ---
    by_season = cancellation_rate_by(df, "season")
    print("\n--- Cancellation rate by Season ---")
    print(by_season.to_string(index=False))
    plot_bar(by_season, "season", "cancellation_rate_pct",
              "Cancellation Rate by Season", "cancellation_by_season.png")

    # --- By prior cancellation history ---
    by_prior = cancellation_rate_by(df, "has_prior_cancellation_history")
    print("\n--- Cancellation rate by Prior Cancellation History ---")
    print(by_prior.to_string(index=False))

    # --- High-risk segment identification (booking volume >= 500 for reliability) ---
    print("\n--- Highest-risk segments (min. 500 bookings for statistical reliability) ---")
    reliable_segments = by_segment[by_segment["booking_count"] >= 500]
    print(reliable_segments.head(3).to_string(index=False))

    # --- Lead time vs cancellation correlation (numeric, not categorical) ---
    corr = df["lead_time"].corr(df["is_canceled"])
    print(f"\nCorrelation between raw lead_time and is_canceled: {corr:.3f}")
    print("Interpretation: bookings made further in advance show a positive")
    print("association with cancellation likelihood. This is an association,")
    print("not a proven causal driver.")

    # Combined heatmap: hotel type x lead time category
    pivot = df.pivot_table(values="is_canceled", index="lead_time_category",
                            columns="hotel", aggfunc="mean") * 100
    plt.figure(figsize=(7, 5))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="rocket_r", cbar_kws={"label": "Cancellation Rate (%)"})
    plt.title("Cancellation Rate (%): Hotel Type x Lead Time Category", fontsize=12, fontweight="bold")
    plt.ylabel("")
    plt.xlabel("")
    plt.tight_layout()
    path = os.path.join(OUT_DIR, "cancellation_heatmap_hotel_leadtime.png")
    plt.savefig(path)
    plt.close()
    print(f"Saved chart: {path}")

    print("\nCancellation analysis complete.")
    return {
        "overall_rate": overall_rate,
        "by_hotel": by_hotel,
        "by_segment": by_segment,
        "by_channel": by_channel,
        "by_lead": by_lead,
        "by_customer": by_cust,
        "by_deposit": by_deposit,
        "by_season": by_season,
    }


if __name__ == "__main__":
    run_analysis()
