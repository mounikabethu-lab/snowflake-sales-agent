# Snowflake Sales Data Agent

AI-powered sales data agent that automatically analyzes Snowflake data and generates insights.

## Features

- Daily sales summaries
- Sales rep performance tracking
- Product demand analysis
- Churn risk alerts
- Manufacturing schedules
- Inventory monitoring
- Customer lifetime value insights

## Setup

1. Clone repository
2. Create GitHub Secrets with Snowflake credentials
3. Push code to main branch
4. GitHub Actions runs automatically

## GitHub Secrets Required

- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_WAREHOUSE`

## Execution

The agent runs automatically via GitHub Actions on every push to main branch.

View results in Snowflake AGENT_QUERY_AUDIT table.