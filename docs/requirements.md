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