{{ config(materialized='table') }}

select
    event_date,
    total_requests,
    unique_ips,
    success_requests,
    client_errors,
    server_errors,
    bot_requests,
    avg_response_bytes,
    round(bot_ratio, 4) as bot_ratio,
from {{ source('gold', 'TRAFFIC_DAILY') }}
where event_date is not null
