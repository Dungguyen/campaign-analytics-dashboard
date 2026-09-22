import argparse

import numpy as np
import pandas as pd

from campaign_data.config import (
    CHANNEL_CTR_RANGES,
    CHANNEL_DELIVERY_RATE_RANGES,
    CHANNEL_SENT_RANGES,
    CHANNEL_WEIGHTS,
    END_DATE,
    MAX_SEND_DELAY_DAYS,
    NUM_DELIVERY_LOGS,
    RANDOM_SEED,
    RAW_DATA_DIR,
    STATUS_DELIVERY_MULTIPLIERS,
)
from campaign_data.generate_campaigns import generate_campaigns


def get_eligible_campaigns() -> pd.DataFrame:
    """
    Return campaigns that are eligible to have delivery logs.

    Scheduled campaigns are excluded because they have not been sent yet.
    """
    campaigns = generate_campaigns()

    eligible = campaigns[
        campaigns["status"] != "Scheduled"
    ].copy()

    eligible["scheduled_date"] = pd.to_datetime(
        eligible["scheduled_date"]
    )

    return eligible.reset_index(drop=True)


def generate_delivery_logs(
    num_rows: int = NUM_DELIVERY_LOGS,
) -> pd.DataFrame:
    """
    Generate synthetic delivery log fact data.

    One row represents one campaign send event
    through one channel at one timestamp.
    """
    if num_rows <= 0:
        raise ValueError("num_rows must be greater than 0")

    rng = np.random.default_rng(RANDOM_SEED)

    campaigns = get_eligible_campaigns()

    if campaigns.empty:
        raise ValueError(
            "No eligible campaigns available for delivery logs"
        )

    # --------------------------------------------------------
    # Sample campaigns
    # --------------------------------------------------------

    campaign_indexes = rng.integers(
        low=0,
        high=len(campaigns),
        size=num_rows,
    )

    sampled_campaigns = campaigns.iloc[
        campaign_indexes
    ].reset_index(drop=True)

    # --------------------------------------------------------
    # Sample channels
    # --------------------------------------------------------

    channel_ids = np.array(
        list(CHANNEL_WEIGHTS.keys()),
        dtype=np.int64,
    )

    channel_probabilities = np.array(
        list(CHANNEL_WEIGHTS.values()),
        dtype=float,
    )

    channel_probabilities = (
        channel_probabilities
        / channel_probabilities.sum()
    )

    sampled_channels = rng.choice(
        channel_ids,
        size=num_rows,
        p=channel_probabilities,
    )

    # --------------------------------------------------------
    # Generate send timestamp
    # --------------------------------------------------------

    scheduled_dates = sampled_campaigns[
        "scheduled_date"
    ].to_numpy(dtype="datetime64[D]")

    end_date = np.datetime64(END_DATE, "D")

    days_available = (
        end_date - scheduled_dates
    ).astype(np.int64)

    max_delays = np.minimum(
        days_available,
        MAX_SEND_DELAY_DAYS,
    )

    random_fractions = rng.random(num_rows)

    delay_days = np.floor(
        random_fractions * (max_delays + 1)
    ).astype(np.int64)

    sent_dates = (
        scheduled_dates
        + delay_days.astype("timedelta64[D]")
    )

    seconds_in_day = 24 * 60 * 60

    random_seconds = rng.integers(
        0,
        seconds_in_day,
        size=num_rows,
    )

    sent_at = (
        sent_dates.astype("datetime64[s]")
        + random_seconds.astype("timedelta64[s]")
    )

    # --------------------------------------------------------
    # Generate sent volume
    # --------------------------------------------------------

    sent = np.empty(
        num_rows,
        dtype=np.int64,
    )

    for channel_id, (
        minimum,
        maximum,
    ) in CHANNEL_SENT_RANGES.items():
        mask = sampled_channels == channel_id

        sent[mask] = rng.integers(
            minimum,
            maximum + 1,
            size=mask.sum(),
        )

    # --------------------------------------------------------
    # Generate baseline delivery rates
    # --------------------------------------------------------

    delivery_rates = np.empty(
        num_rows,
        dtype=float,
    )

    for channel_id, (
        minimum,
        maximum,
    ) in CHANNEL_DELIVERY_RATE_RANGES.items():
        mask = sampled_channels == channel_id

        delivery_rates[mask] = rng.uniform(
            minimum,
            maximum,
            size=mask.sum(),
        )

    # --------------------------------------------------------
    # Apply campaign status effect
    # --------------------------------------------------------

    statuses = sampled_campaigns[
        "status"
    ].to_numpy()

    status_multipliers = np.empty(
        num_rows,
        dtype=float,
    )

    for status, (
        minimum,
        maximum,
    ) in STATUS_DELIVERY_MULTIPLIERS.items():
        mask = statuses == status

        status_multipliers[mask] = rng.uniform(
            minimum,
            maximum,
            size=mask.sum(),
        )

    final_delivery_rates = np.clip(
        delivery_rates * status_multipliers,
        0.0,
        1.0,
    )

    delivered = np.floor(
        sent * final_delivery_rates
    ).astype(np.int64)

    failed = sent - delivered

    # --------------------------------------------------------
    # Generate CTR and clicks
    # --------------------------------------------------------

    ctr = np.empty(
        num_rows,
        dtype=float,
    )

    for channel_id, (
        minimum,
        maximum,
    ) in CHANNEL_CTR_RANGES.items():
        mask = sampled_channels == channel_id

        ctr[mask] = rng.uniform(
            minimum,
            maximum,
            size=mask.sum(),
        )

    clicks = np.floor(
        delivered * ctr
    ).astype(np.int64)

    # --------------------------------------------------------
    # Build fact dataframe
    # --------------------------------------------------------

    delivery_log_ids = np.char.add(
        "DLV",
        np.char.zfill(
            np.arange(
                1,
                num_rows + 1,
            ).astype(str),
            9,
        ),
    )

    df = pd.DataFrame(
        {
            "delivery_log_id": delivery_log_ids,
            "campaign_id": sampled_campaigns[
                "campaign_id"
            ].to_numpy(),
            "channel_id": sampled_channels,
            "sent_at": pd.to_datetime(sent_at),
            "sent_date": pd.to_datetime(sent_dates).date,
            "sent": sent,
            "delivered": delivered,
            "failed": failed,
            "clicks": clicks,
        }
    )

    return df


def save_delivery_logs(
    df: pd.DataFrame,
    filename: str = "fact_delivery_log.csv",
) -> None:
    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = RAW_DATA_DIR / filename

    df.to_csv(
        output_path,
        index=False,
        date_format="%Y-%m-%d %H:%M:%S",
    )

    print(f"Generated {len(df):,} delivery logs")
    print(f"Saved to: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic delivery log data."
    )

    parser.add_argument(
        "--rows",
        type=int,
        default=NUM_DELIVERY_LOGS,
        help=(
            "Number of delivery log rows to generate. "
            f"Default: {NUM_DELIVERY_LOGS:,}"
        ),
    )

    parser.add_argument(
        "--output",
        default="fact_delivery_log.csv",
        help="Output CSV filename.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    df = generate_delivery_logs(
        num_rows=args.rows,
    )

    save_delivery_logs(
        df,
        filename=args.output,
    )


if __name__ == "__main__":
    main()