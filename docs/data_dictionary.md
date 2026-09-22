# Data Dictionary

## dim_campaign

| Column | Type | Key | Nullable | Description |
|---|---|---|---|---|
| campaign_id | string | PK | No | Unique campaign identifier |
| campaign_name | string | | No | Campaign display name |
| created_date | date | | No | Date the campaign was created |
| scheduled_date | date | | No | Planned campaign delivery date |
| status | string | | No | Current campaign status |

### Allowed Status Values

- Scheduled
- Running
- Completed
- Failed
- Partial Success

---

## dim_channel

| Column | Type | Key | Nullable | Description |
|---|---|---|---|---|
| channel_id | integer | PK | No | Unique channel identifier |
| channel_name | string | | No | Communication channel name |

### Expected Channels

- PWA
- LINE OA
- Email
- SMS
- Push Notification

---

## fact_delivery_log

| Column | Type | Key | Nullable | Description |
|---|---|---|---|---|
| delivery_log_id | integer | PK | No | Unique delivery log identifier |
| campaign_id | string | FK | No | References `dim_campaign.campaign_id` |
| channel_id | integer | FK | No | References `dim_channel.channel_id` |
| sent_at | datetime | | No | Campaign delivery timestamp |
| sent | integer | | No | Number of messages sent |
| delivered | integer | | No | Number successfully delivered |
| failed | integer | | No | Number failed |
| clicks | integer | | No | Number of delivered messages clicked |

### Constraints

`sent >= 0`

`delivered >= 0`

`failed >= 0`

`clicks >= 0`

`delivered + failed <= sent`

`clicks <= delivered`

---

## dim_calendar

| Column | Type | Key | Nullable | Description |
|---|---|---|---|---|
| date | date | PK | No | Calendar date |
| month | integer | | No | Month number (1–12) |
| quarter | string | | No | Quarter (Q1–Q4) |
| year | integer | | No | Calendar year |