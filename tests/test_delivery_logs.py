import pandas as pd
import pytest

from campaign_data.config import (
    END_DATE,
)
from campaign_data.generate_campaigns import generate_campaigns
from campaign_data.generate_channels import generate_channels
from campaign_data.generate_delivery_logs import generate_delivery_logs


TEST_ROWS = 10_000


@pytest.fixture(scope="module")
def campaigns_df():
    return generate_campaigns()


@pytest.fixture(scope="module")
def channels_df():
    return generate_channels()


@pytest.fixture(scope="module")
def delivery_logs_df():
    return generate_delivery_logs(
        num_rows=TEST_ROWS
    )


@pytest.fixture(scope="module")
def delivery_with_campaigns(
    delivery_logs_df,
    campaigns_df,
):
    return delivery_logs_df.merge(
        campaigns_df[
            [
                "campaign_id",
                "status",
                "scheduled_date",
            ]
        ],
        on="campaign_id",
        how="left",
    )


# ============================================================
# Basic Structure
# ============================================================

def test_delivery_log_count(delivery_logs_df):
    assert len(delivery_logs_df) == TEST_ROWS


def test_delivery_log_ids_are_unique(delivery_logs_df):
    assert delivery_logs_df[
        "delivery_log_id"
    ].is_unique


def test_delivery_logs_have_no_nulls(delivery_logs_df):
    assert not (
        delivery_logs_df
        .isnull()
        .any()
        .any()
    )


# ============================================================
# Foreign Keys
# ============================================================

def test_campaign_foreign_keys(
    delivery_logs_df,
    campaigns_df,
):
    valid_campaign_ids = set(
        campaigns_df["campaign_id"]
    )

    assert (
        delivery_logs_df["campaign_id"]
        .isin(valid_campaign_ids)
        .all()
    )


def test_channel_foreign_keys(
    delivery_logs_df,
    channels_df,
):
    valid_channel_ids = set(
        channels_df["channel_id"]
    )

    assert (
        delivery_logs_df["channel_id"]
        .isin(valid_channel_ids)
        .all()
    )


# ============================================================
# Campaign Rules
# ============================================================

def test_scheduled_campaigns_not_in_fact(
    delivery_with_campaigns,
):
    assert not (
        delivery_with_campaigns["status"]
        == "Scheduled"
    ).any()


def test_sent_at_not_before_scheduled_date(
    delivery_with_campaigns,
):
    sent_at = pd.to_datetime(
        delivery_with_campaigns["sent_at"]
    )

    scheduled_date = pd.to_datetime(
        delivery_with_campaigns["scheduled_date"]
    )

    assert (
        sent_at >= scheduled_date
    ).all()


# ============================================================
# Metric Rules
# ============================================================

@pytest.mark.parametrize(
    "column",
    [
        "sent",
        "delivered",
        "failed",
        "clicks",
    ],
)
def test_delivery_metrics_are_non_negative(
    delivery_logs_df,
    column,
):
    assert (
        delivery_logs_df[column] >= 0
    ).all()


def test_delivery_equation(delivery_logs_df):
    assert (
        delivery_logs_df["delivered"]
        + delivery_logs_df["failed"]
        == delivery_logs_df["sent"]
    ).all()


def test_clicks_do_not_exceed_delivered(
    delivery_logs_df,
):
    assert (
        delivery_logs_df["clicks"]
        <= delivery_logs_df["delivered"]
    ).all()


# ============================================================
# Date Rules
# ============================================================

def test_sent_date_matches_sent_at(delivery_logs_df):
    sent_at_dates = pd.to_datetime(
        delivery_logs_df["sent_at"]
    ).dt.date

    sent_dates = pd.to_datetime(
        delivery_logs_df["sent_date"]
    ).dt.date

    assert (
        sent_at_dates == sent_dates
    ).all()


def test_sent_at_not_after_end_date(
    delivery_logs_df,
):
    sent_at = pd.to_datetime(
        delivery_logs_df["sent_at"]
    )

    end_date = (
        pd.Timestamp(END_DATE)
        + pd.Timedelta(days=1)
    )

    assert (
        sent_at < end_date
    ).all()