"""SQL query builders for Snowflake sales analysis."""


class SalesQueries:
    """Static methods that return Snowflake SQL strings for sales analysis."""

    @staticmethod
    def daily_sales_summary() -> str:
        """Return today's sales totals, deal counts, and average deal size by rep."""
        return """
        SELECT
            sr.rep_name,
            SUM(o.final_value) AS total_revenue,
            COUNT(*) AS deals_closed,
            AVG(o.final_value) AS avg_deal_size
        FROM ORDERS o
        JOIN SALES_REPS sr ON o.rep_id = sr.rep_id
        WHERE DATE(o.order_date) = CURRENT_DATE()
        GROUP BY sr.rep_name
        ORDER BY total_revenue DESC
        """

    @staticmethod
    def sales_rep_performance(month: str = "2024-01") -> str:
        """Return quota attainment and performance status for a given month."""
        return f"""
        SELECT
            sr.rep_name,
            sp.quota,
            sp.actual_revenue,
            sp.quota_attainment_percent,
            sp.deals_won,
            sp.deals_lost,
            sp.pipeline_value,
            CASE
                WHEN sp.quota_attainment_percent < 85 THEN 'UNDERPERFORMING'
                WHEN sp.quota_attainment_percent > 110 THEN 'EXCEEDING'
                ELSE 'ON_TRACK'
            END AS performance_status
        FROM SALES_PERFORMANCE sp
        JOIN SALES_REPS sr ON sp.rep_id = sr.rep_id
        WHERE sp.performance_month = '{month}'
        ORDER BY sp.quota_attainment_percent ASC
        """

    @staticmethod
    def product_demand_trends() -> str:
        """Return product demand, growth trend, and growth status ranking."""
        return """
        SELECT
            product_name,
            purchase_frequency,
            growth_trend_percent,
            total_revenue,
            peak_season,
            inventory_recommendation,
            CASE
                WHEN growth_trend_percent > 15 THEN 'HIGH_GROWTH'
                WHEN growth_trend_percent > 5 THEN 'MODERATE_GROWTH'
                ELSE 'DECLINING'
            END AS growth_status
        FROM PRODUCT_DEMAND_FREQUENCY
        ORDER BY growth_trend_percent DESC
        """

    @staticmethod
    def churn_risk_accounts() -> str:
        """Return accounts with medium or high churn risk and days since last order."""
        return """
        SELECT
            c.customer_name,
            c.industry,
            clv.churn_risk_percent,
            clv.total_revenue,
            clv.last_order_date,
            DATEDIFF(day, clv.last_order_date, CURRENT_DATE()) AS days_since_order,
            CASE
                WHEN clv.churn_risk_percent > 25 THEN 'HIGH_RISK'
                WHEN clv.churn_risk_percent > 15 THEN 'MEDIUM_RISK'
                ELSE 'LOW_RISK'
            END AS risk_category
        FROM CUSTOMER_LIFETIME_VALUE clv
        JOIN CUSTOMERS c ON clv.customer_id = c.customer_id
        WHERE clv.churn_risk_percent > 15
        ORDER BY clv.churn_risk_percent DESC
        """

    @staticmethod
    def manufacturing_schedule(forecast_month: str = "2024-02") -> str:
        """Return manufacturing units, stock, and deadline urgency for a forecast month."""
        return f"""
        SELECT
            df.product_name,
            df.forecasted_units,
            df.lead_time_days,
            df.manufacturing_deadline,
            df.risk_level,
            pi.quantity_available,
            (df.forecasted_units - pi.quantity_available) AS units_to_manufacture,
            DATEDIFF(day, CURRENT_DATE(), df.manufacturing_deadline) AS days_until_deadline,
            CASE
                WHEN DATEDIFF(day, CURRENT_DATE(), df.manufacturing_deadline) < 0 THEN 'OVERDUE'
                WHEN DATEDIFF(day, CURRENT_DATE(), df.manufacturing_deadline) < 7 THEN 'URGENT'
                ELSE 'ON_TRACK'
            END AS urgency
        FROM DEMAND_FORECAST df
        JOIN PRODUCT_INVENTORY pi ON df.product_id = pi.product_id
        WHERE df.forecast_month = '{forecast_month}'
        ORDER BY df.manufacturing_deadline ASC
        """

    @staticmethod
    def inventory_alerts() -> str:
        """Return products near or below safety stock with critical/warning status."""
        return """
        SELECT
            pdf.product_name,
            pi.quantity_available,
            pdf.safety_stock,
            (pi.quantity_available - pdf.safety_stock) AS units_above_safety,
            ROUND((pi.quantity_available / NULLIF(df.forecasted_units, 0)), 1) AS days_of_supply,
            CASE
                WHEN pi.quantity_available < pdf.safety_stock THEN 'CRITICAL'
                WHEN pi.quantity_available < (pdf.safety_stock * 1.5) THEN 'WARNING'
                ELSE 'OK'
            END AS stock_status
        FROM PRODUCT_DEMAND_FREQUENCY pdf
        JOIN PRODUCT_INVENTORY pi ON pdf.product_id = pi.product_id
        JOIN DEMAND_FORECAST df ON pdf.product_id = df.product_id
        WHERE pi.quantity_available < (pdf.safety_stock * 2)
        ORDER BY stock_status DESC, days_of_supply ASC
        """

    @staticmethod
    def customer_ltv_insights() -> str:
        """Return the top 10 customers ranked by predicted lifetime value."""
        return """
        SELECT TOP 10
            c.customer_name,
            c.industry,
            c.company_size,
            clv.total_revenue,
            clv.predicted_ltv,
            clv.renewal_likelihood_percent,
            clv.average_order_value,
            clv.total_orders,
            ROUND(clv.predicted_ltv / NULLIF(clv.total_orders, 0), 2) AS revenue_per_order
        FROM CUSTOMER_LIFETIME_VALUE clv
        JOIN CUSTOMERS c ON clv.customer_id = c.customer_id
        ORDER BY clv.predicted_ltv DESC
        """