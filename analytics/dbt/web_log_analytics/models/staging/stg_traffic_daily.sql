{{ config(materialized='view') }}

select
    event_date,
    total_requests,
    unique_ips,
    success_requests,
    client_errors,
    server_errors,
    bot_requests,
    avg_response_bytes,
    bot_ratio
from {{ source('gold', 'TRAFFIC_DAILY') }}
