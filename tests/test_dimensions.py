import pandas as pd
import pytest

from campaign_data.config import (
    CAMPAIGN_STATUSES,
    CHANNELS,
    END_DATE,
    NUM_CAMPAIGNS,
    START_DATE,
)
from campaign_data.generate_calendar import generate_calendar
from campaign_data.generate_campaigns import generate_campaigns
from campaign_data.generate_channels import generate_channels

@pytest.fixture(scope="module")
def channels_df():
    return generate_channels()


@pytest.fixture(scope="module")
def campaigns_df():
    return generate_campaigns()


@pytest.fixture(scope="module")
def calendar_df():
    return generate_calendar()

def test_channels_count(channels_df):
    assert len(channels_df) == len(CHANNELS)

def test_channel_ids_are_unique(channels_df):
    assert channels_df["channel_id"].is_unique



def test_required_channels_exist(channels_df):
    required_channels = {
        "PWA",
        "LINE OA",
    }

    assert required_channels.issubset(
        set(channels_df["channel_name"])
    )



def test_campaign_count(campaigns_df):
    assert len(campaigns_df) == NUM_CAMPAIGNS



def test_campaign_ids_are_unique(campaigns_df):
    assert campaigns_df["campaign_id"].is_unique


def test_campaign_required_fields_have_no_nulls(campaigns_df):
    required_columns = [
        "campaign_id",
        "campaign_name",
        "created_date",
        "scheduled_date",
        "status",
    ]

    assert not (
        campaigns_df[required_columns]
        .isnull()
        .any()
        .any()
    )


def test_campaign_scheduled_date_not_before_created_date(
    campaigns_df,
):
    created_dates = pd.to_datetime(
        campaigns_df["created_date"]
    )

    scheduled_dates = pd.to_datetime(
        campaigns_df["scheduled_date"]
    )

    assert (
        scheduled_dates >= created_dates
    ).all()


def test_campaign_dates_within_range(campaigns_df):
    created_dates = pd.to_datetime(
        campaigns_df["created_date"]
    )

    scheduled_dates = pd.to_datetime(
        campaigns_df["scheduled_date"]
    )

    start_date = pd.Timestamp(START_DATE)
    end_date = pd.Timestamp(END_DATE)

    assert (
        created_dates >= start_date
    ).all()

    assert (
        scheduled_dates <= end_date
    ).all()


def test_campaign_status_values(campaigns_df):
    actual_statuses = set(
        campaigns_df["status"]
    )

    allowed_statuses = set(
        CAMPAIGN_STATUSES
    )

    assert actual_statuses.issubset(
        allowed_statuses
    )


def test_calendar_date_range(calendar_df):
    assert (
        calendar_df["date"].min()
        == pd.Timestamp(START_DATE)
    )

    assert (
        calendar_df["date"].max()
        == pd.Timestamp(END_DATE)
    )



def test_calendar_dates_are_unique(calendar_df):
    assert calendar_df["date"].is_unique



def test_calendar_has_no_nulls(calendar_df):
    assert not (
        calendar_df
        .isnull()
        .any()
        .any()
    )


def test_calendar_quarters(calendar_df):
    expected_quarters = {
        "Q1",
        "Q2",
        "Q3",
        "Q4",
    }

    assert (
        set(calendar_df["quarter"])
        == expected_quarters
    )