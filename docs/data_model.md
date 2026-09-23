# Campaign Analytics Data Model

## 1. Overview

The Campaign Analytics Dashboard uses a star schema optimized for analytical
queries and Power BI reporting.

The model contains one fact table and three dimensions:

- `fact_delivery_log` — campaign delivery performance
- `dim_campaign` — campaign descriptive attributes
- `dim_channel` — delivery channel attributes
- `dim_calendar` — reporting date attributes

## 2. Model Diagram

```text
                     dim_campaign
                          |
                          | 1:N
                          |
dim_calendar 1:N --> fact_delivery_log <-- N:1 dim_channel
All relationships use single-direction filtering from dimension tables to the
fact table.

3. Fact Table
fact_delivery_log

Grain

One row represents the delivery performance of one campaign through one
channel at one send timestamp.

This means the same campaign can appear multiple times because:

a campaign can use multiple channels;
a campaign/channel combination can have multiple send events at different
timestamps.

Columns

Column	Role	Description
delivery_log_id	Primary Key	Unique delivery event identifier
campaign_id	Foreign Key	References dim_campaign
channel_id	Foreign Key	References dim_channel
sent_at	Timestamp	Time when the delivery event occurred
sent_date	Foreign Key	Date used to join dim_calendar
sent	Measure	Number of messages attempted
delivered	Measure	Number successfully delivered
failed	Measure	Number that failed delivery
clicks	Measure	Number of delivered messages that received clicks

Core business rules:

sent = delivered + failed
clicks <= delivered
all metrics are non-negative
sent_at >= scheduled_date
Scheduled campaigns do not have delivery log records
4. Dimension Tables
dim_campaign

Grain: one row per campaign.

Column	Description
campaign_id	Unique campaign identifier
campaign_name	Campaign display name
created_date	Date campaign was created
scheduled_date	Planned execution date
status	Campaign lifecycle status

Supported statuses:

Scheduled
Running
Completed
Failed
Partial Success

Campaign attributes are stored outside the fact table to avoid repeatedly
storing campaign metadata for every delivery event.

dim_channel

Grain: one row per delivery channel.

Column	Description
channel_id	Unique channel identifier
channel_name	Channel name

Channels:

PWA
LINE OA
Email
SMS
Push Notification

Separating channels into a dimension provides a consistent channel definition
and enables channel-level filtering and comparison.

dim_calendar

Grain: one row per calendar date.

The calendar covers:

2024-01-01 through 2026-12-31

with 1,096 rows.

It contains reporting attributes such as:

Date
Day
Month
Month Year
Quarter
Year
Day of Week
Day of Week Number

A dedicated calendar dimension enables consistent date filtering,
chronological sorting, time-based analysis, and Power BI date intelligence.

5. Relationships
From	To	Cardinality	Filter Direction
dim_campaign[campaign_id]	fact_delivery_log[campaign_id]	1:N	Single
dim_channel[channel_id]	fact_delivery_log[channel_id]	1:N	Single
dim_calendar[date]	fact_delivery_log[sent_date]	1:N	Single

The dimension tables filter the fact table.

Bidirectional relationships are intentionally avoided because they are not
required by the reporting requirements and could introduce ambiguous filter
paths as the model grows.

6. Why a Star Schema?

The model separates descriptive business entities from measurable delivery
events.

For example, instead of storing:

campaign_name, status, and channel_name

repeatedly across 500,000 delivery rows, the fact table stores their keys.

This design provides:

simpler analytical queries;
clear fact and dimension responsibilities;
reusable dimensions;
efficient Power BI filtering;
easier DAX measures;
reduced duplication of descriptive attributes;
easier model extension.
7. Fact Grain and Aggregation

The most important modeling decision is the fact grain:

One campaign + one channel + one send timestamp.

Therefore, campaign_id alone is not unique in the fact table.

For example:

Campaign A | PWA     | 2026-01-10 08:00
Campaign A | LINE OA | 2026-01-10 08:00
Campaign A | PWA     | 2026-01-11 09:00

These are three valid delivery events.

Consequently, campaign-level metrics such as Total Campaigns use a distinct
campaign count rather than counting fact rows.

8. Model Scale

Current synthetic dataset:

Table	Rows
dim_campaign	50,000
dim_channel	5
dim_calendar	1,096
fact_delivery_log	500,000

The dataset is intentionally large enough to exercise realistic analytical
modeling and Power BI behavior while remaining reproducible locally.

9. Design Decisions
Why sent_date exists when sent_at already exists

sent_at represents the exact event timestamp.

sent_date provides a date-level foreign key to dim_calendar.

This keeps the relationship simple:

dim_calendar[date] -> fact_delivery_log[sent_date]

while retaining the exact timestamp for detailed reporting.

Why status belongs to dim_campaign

Status describes the campaign rather than an individual delivery event.

Keeping it in dim_campaign allows campaign-level filtering without
duplicating the same descriptive value throughout delivery records.

Why delivery metrics belong to the fact table

sent, delivered, failed, and clicks are measurable outcomes of a
delivery event.

They therefore belong at the delivery-event grain in fact_delivery_log.

10. Data Quality Constraints

Before the dataset is consumed by Power BI, automated validation checks verify:

primary key uniqueness;
foreign key integrity;
required fields;
valid campaign statuses;
valid date relationships;
non-negative delivery metrics;
delivered + failed = sent;
clicks <= delivered;
Scheduled campaigns have no delivery logs;
sent_date matches the date component of sent_at.

The current generated dataset passes all 29 validation checks.