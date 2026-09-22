import pandas as pd

from campaign_data.config import CHANNELS, RAW_DATA_DIR


def generate_channels() -> pd.DataFrame:
    df = pd.DataFrame(
        CHANNELS,
        columns=["channel_id", "channel_name"],
    )

    return df


def save_channels(df: pd.DataFrame) -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_path = RAW_DATA_DIR / "dim_channel.csv"

    df.to_csv(
        output_path,
        index=False,
    )

    print(f"Generated {len(df):,} channels")
    print(f"Saved to: {output_path}")


def main() -> None:
    df = generate_channels()
    save_channels(df)


if __name__ == "__main__":
    main()