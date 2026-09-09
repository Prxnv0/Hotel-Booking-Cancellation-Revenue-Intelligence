"""
Hotel Booking Cancellation & Revenue Intelligence Analytics
------------------------------------------------------------
Script: data_cleaning.py
Purpose: Perform a complete data quality assessment on the raw hotel
booking dataset, clean it based on the actual meaning of each column,
engineer business-relevant features, and save an analysis-ready CSV.

Dataset source: Kaggle "Hotel Booking Demand" by Jesse Mostipak
(originally published by Antonio, Almeida & Nunes, Data in Brief, 2019).

Run independently with:
    python src/data_cleaning.py
"""

import os
import numpy as np
import pandas as pd

RAW_PATH = os.path.join("data", "raw", "hotel_bookings.csv")
PROCESSED_PATH = os.path.join("data", "processed", "hotel_bookings_cleaned.csv")


def load_data(path: str = RAW_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def data_quality_report(df: pd.DataFrame) -> None:
    print("=" * 70)
    print("DATA QUALITY ASSESSMENT")
    print("=" * 70)
    print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

    print("\n--- Missing values (columns with at least 1) ---")
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    for col, n in missing.items():
        print(f"  {col:35s} {n:>8,} ({n / len(df):.2%})")

    print(f"\n--- Duplicate rows ---\n  {df.duplicated().sum():,} exact duplicate records")

    print("\n--- Data types ---")
    print(df.dtypes.value_counts())

    print("\n--- Invalid guest configurations (0 adults, 0 children, 0 babies) ---")
    zero_guests = ((df["adults"] == 0) & (df["children"].fillna(0) == 0) & (df["babies"] == 0)).sum()
    print(f"  {zero_guests:,} bookings with no guests recorded")

    print("\n--- Invalid ADR (Average Daily Rate) values ---")
    print(f"  ADR <= 0 : {(df['adr'] <= 0).sum():,}")
    print(f"  ADR > 1000 (extreme outliers): {(df['adr'] > 1000).sum():,}")

    print("\n--- Zero-night bookings (0 weekend nights AND 0 week nights) ---")
    zero_nights = ((df["stays_in_weekend_nights"] == 0) & (df["stays_in_week_nights"] == 0)).sum()
    print(f"  {zero_nights:,} bookings with no nights stayed")
    print("=" * 70)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleaning decisions (documented):

    1. `company` is dropped as an analytical feature source but its
       missingness (94% missing) is expected: most bookings are not
       linked to a company account. We do NOT drop the column outright
       from the raw record, but we do not impute it (imputing a
       categorical ID field with ~94% missingness would fabricate data).
       For the cleaned analytical dataset we keep a simplified
       `has_company` flag instead of the raw company ID.

    2. `agent` (13.7% missing) similarly represents "no travel agent
       was used for this booking" in many cases. We keep a `has_agent`
       flag and keep the raw `agent` column with NaN preserved (no
       fabrication of agent IDs).

    3. `children` has only 4 missing values out of 119,390 (0.003%).
       These are filled with 0, the mode, since the booking still has
       adults recorded and a missing children count most plausibly
       represents zero children rather than an unrecorded value.

    4. `country` has 488 missing values (0.4%). These are kept as the
       explicit label "Unknown" rather than imputed with a guessed
       country, since guessing nationality would fabricate data.

    5. Exact duplicate rows (31,994 of them, ~26.8% of raw records) are
       RETAINED, not deleted. This dataset does not provide a reliable
       unique booking identifier (no Booking ID / primary key column),
       so there is no way to reliably distinguish an accidental
       duplicate record from two separate, legitimate bookings that
       happen to share identical values across all 32 fields (e.g.
       two guests from the same country booking the same hotel type,
       same room, same rate, same arrival date via the same channel).
       Blanket-dropping ~27% of the dataset on that assumption would
       risk silently discarding real bookings and distorting every
       downstream KPI (cancellation rates, demand counts, revenue
       exposure). We therefore only CALCULATE and REPORT the duplicate
       count for transparency and keep all rows in the cleaned
       dataset. If a genuine primary key becomes available in a future
       version of the source data, this decision should be revisited.

    6. Rows where adults + children + babies == 0 (no guests at all)
       are logically invalid bookings (180 rows) and are removed, since
       a booking cannot exist with zero occupants.

    7. ADR (Average Daily Rate) negative values (implying a rebate/
       correction) are set to NaN and excluded from revenue
       calculations rather than deleted from the dataset, since the
       booking itself (occupancy, cancellation status, etc.) is still
       valid data. One extreme outlier at adr = 5400 is retained but
       flagged, since Resort Hotel + long stays can command high ADR;
       we do not assume it is an error without evidence.

    8. `reservation_status_date` is converted to a proper datetime.
    """
    df = df.copy()
    before = len(df)

    # 1 & 2: agent / company -> presence flags
    df["has_agent"] = df["agent"].notna()
    df["has_company"] = df["company"].notna()

    # 3: children missing -> 0
    df["children"] = df["children"].fillna(0).astype(int)

    # 4: country missing -> explicit Unknown label
    df["country"] = df["country"].fillna("Unknown")

    # Convert reservation_status_date to datetime
    df["reservation_status_date"] = pd.to_datetime(df["reservation_status_date"], errors="coerce")

    # 5: exact duplicate rows are NOT dropped (see docstring point 5).
    # The dataset has no unique Booking ID, so exact-duplicate rows
    # cannot be reliably distinguished from legitimate separate
    # bookings that share identical attribute values. We report the
    # count for transparency but retain every row.
    dup_count = df.duplicated().sum()
    print(f"Detected {dup_count:,} exact duplicate rows ({dup_count/before:.1%} of data) "
          f"- RETAINED (no reliable unique booking identifier exists to confirm they are accidental).")

    # 6: remove bookings with zero total guests (logically invalid)
    zero_guest_mask = (df["adults"] + df["children"] + df["babies"]) == 0
    print(f"Removed {zero_guest_mask.sum():,} bookings with zero total guests.")
    df = df[~zero_guest_mask]

    # 7: negative ADR -> NaN (kept as missing, not deleted)
    neg_adr_mask = df["adr"] < 0
    print(f"Set {neg_adr_mask.sum():,} negative ADR values to NaN (kept row, excluded from revenue calcs).")
    df.loc[neg_adr_mask, "adr"] = np.nan

    after = len(df)
    print(f"Rows before cleaning: {before:,} | after cleaning: {after:,} "
          f"({(before-after)/before:.1%} removed).")

    return df.reset_index(drop=True)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Total guests
    df["total_guests"] = df["adults"] + df["children"] + df["babies"]

    # Total stay duration
    df["total_stay_nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]

    # Lead time categories, based on the dataset's own quartile distribution
    q1, q2, q3 = df["lead_time"].quantile([0.25, 0.5, 0.75])
    print(f"Lead time quartiles used for categorization: Q1={q1:.0f}, Median={q2:.0f}, Q3={q3:.0f}")

    def lead_time_bucket(days):
        if days <= 7:
            return "Last Minute (0-7 days)"
        elif days <= q2:
            return f"Short Lead (8-{int(q2)} days)"
        elif days <= q3:
            return f"Medium Lead ({int(q2)+1}-{int(q3)} days)"
        else:
            return f"Long Lead ({int(q3)+1}+ days)"

    df["lead_time_category"] = df["lead_time"].apply(lead_time_bucket)

    # Arrival date as an actual date (day 1 fallback not needed - we build from year/month)
    month_map = {m: i for i, m in enumerate(
        ["January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December"], start=1)}
    df["arrival_month_num"] = df["arrival_date_month"].map(month_map)

    df["arrival_date"] = pd.to_datetime(
        dict(year=df["arrival_date_year"], month=df["arrival_month_num"], day=df["arrival_date_day_of_month"]),
        errors="coerce"
    )

    # Season (Northern Hemisphere, since hotels are located in Portugal)
    def month_to_season(m):
        if m in (12, 1, 2):
            return "Winter"
        elif m in (3, 4, 5):
            return "Spring"
        elif m in (6, 7, 8):
            return "Summer"
        else:
            return "Autumn"

    df["season"] = df["arrival_month_num"].apply(month_to_season)
    df["arrival_quarter"] = df["arrival_month_num"].apply(lambda m: (m - 1) // 3 + 1)

    # Cancellation risk indicators (associative, not causal language used downstream)
    df["is_returning_guest"] = df["is_repeated_guest"] == 1
    df["has_prior_cancellation_history"] = df["previous_cancellations"] > 0

    # Potential revenue per booking (ADR x nights) - only where ADR is known
    df["potential_booking_revenue"] = df["adr"] * df["total_stay_nights"]

    return df


def save_processed(df: pd.DataFrame, path: str = PROCESSED_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"\nSaved cleaned + feature-engineered dataset to: {path}")
    print(f"Final shape: {df.shape[0]:,} rows x {df.shape[1]} columns")


def main():
    df_raw = load_data()
    data_quality_report(df_raw)
    df_clean = clean_data(df_raw)
    df_feat = engineer_features(df_clean)
    save_processed(df_feat)


if __name__ == "__main__":
    main()
