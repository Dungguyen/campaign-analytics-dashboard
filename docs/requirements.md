# Campaign Analytics Requirements

## Objective

Build a synthetic campaign delivery dataset for a Power BI dashboard
that analyzes campaign delivery performance across communication channels.

## Dataset Scale

- Campaigns: 50,000
- Delivery logs: 500,000
- Channels: 5
- Calendar: generated from the dataset date range

## Required Channels

- PWA
- LINE OA
- Email
- SMS
- Push Notification

## Campaign Status

Valid campaign statuses:

- Scheduled
- Running
- Completed
- Failed
- Partial Success

## Fact Table Grain

One row in `fact_delivery_log` represents the delivery performance
of one campaign through one channel at one send timestamp.

## Business Rules

- `campaign_id` must reference an existing campaign.
- `channel_id` must reference an existing channel.
- `scheduled_date >= created_date`.
- `sent >= 0`.
- `delivered >= 0`.
- `failed >= 0`.
- `clicks >= 0`.
- `delivered + failed <= sent`.
- `clicks <= delivered`.
- A campaign may use multiple channels.
- `sent_at >= scheduled_date`.

## Date Range

Synthetic data will cover:

- Start date: 2024-01-01
- End date: 2026-12-31

The Calendar dimension must cover the complete date range.

### Delivery Log Business Rules

- The delivery log dataset must contain exactly 500,000 rows.
- Each delivery log must reference a valid campaign.
- Each delivery log must reference a valid channel.
- Campaigns with status `Scheduled` must not have delivery logs.
- A campaign may have delivery logs across multiple channels.
- `sent_at` must be greater than or equal to the campaign's `scheduled_date`.
- `sent_at` must not exceed the configured dataset end date.
- `sent_date` must equal the date component of `sent_at`.
- `sent` must be greater than or equal to 0.
- `delivered` must be greater than or equal to 0.
- `failed` must be greater than or equal to 0.
- `clicks` must be greater than or equal to 0.
- `delivered + failed` must equal `sent`.
- `clicks` must not exceed `delivered`.
- Channel selection, send volume, delivery rate, and CTR use configured synthetic distributions.
- Campaign status affects delivery performance.