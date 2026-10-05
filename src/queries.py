class SalesQueries:
    """SQL queries for sales data analysis"""
    
    @staticmethod
    def daily_sales_summary():
        """Daily sales summary by rep"""
        return """
        SELECT 
            sr.rep_name,
            SUM(o.final_value) as total_revenue,
            COUNT(*) as deals_closed,
            AVG(o.final_value) as avg_deal_size
        FROM ORDERS o
        JOIN SALES_REPS sr ON o.rep_id = sr.rep_id
        WHERE DATE(o.order_date) = CURRENT_DATE()
        GROUP BY sr.rep_name
        ORDER BY total_revenue DESC
        """
    
    @staticmethod
    def sales_rep_performance(month='2024-01'):
        """Sales rep performance metrics"""
        return f"""
        SELECT 
            sr.rep_name,
            sp.quota,
            sp.actual_revenue,
            sp.quota_attainment_percent,
            sp.deals_won,
            sp.deals_lost,
            sp.pipeline_value
        FROM SALES_PERFORMANCE sp
        JOIN SALES_REPS sr ON sp.rep_id = sr.rep_id
        WHERE sp.performance_month = '{month}'
        ORDER BY sp.quota_attainment_percent DESC
        """
    
    @staticmethod
    def product_demand_trends():
        """Product demand and growth trends"""
        return """
        SELECT 
            product_name,
            purchase_frequency,
            growth_trend_percent,
            total_revenue,
            peak_season,
            inventory_recommendation
        FROM PRODUCT_DEMAND_FREQUENCY
        ORDER BY growth_trend_percent DESC
        """
    
    @staticmethod
    def churn_risk_accounts():
        """High-risk accounts for churn"""
        return """
        SELECT 
            c.customer_name,
            clv.churn_risk_percent,
            clv.total_revenue,
            clv.last_order_date,
            DATEDIFF(day, clv.last_order_date, CURRENT_DATE()) as days_since_order
        FROM CUSTOMER_LIFETIME_VALUE clv
        JOIN CUSTOMERS c ON clv.customer_id = c.customer_id
        WHERE clv.churn_risk_percent > 25
        ORDER BY clv.churn_risk_percent DESC
        """
    
    @staticmethod
    def manufacturing_schedule(forecast_month='2024-02'):
        """Manufacturing schedule based on demand forecast"""
        return f"""
        SELECT 
            df.product_name,
            df.forecasted_units,
            df.lead_time_days,
            df.manufacturing_deadline,
            df.risk_level,
            pi.quantity_available,
            (df.forecasted_units - pi.quantity_available) as units_to_manufacture
        FROM DEMAND_FORECAST df
        JOIN PRODUCT_INVENTORY pi ON df.product_id = pi.product_id
        WHERE df.forecast_month = '{forecast_month}'
        ORDER BY df.manufacturing_deadline ASC
        """
    
    @staticmethod
    def inventory_alerts():
        """Low inventory alerts"""
        return """
        SELECT 
            pdf.product_name,
            pi.quantity_available,
            pdf.safety_stock,
            ROUND((pi.quantity_available / NULLIF(df.forecasted_units, 0)) * 100, 1) as days_of_supply
        FROM PRODUCT_DEMAND_FREQUENCY pdf
        JOIN PRODUCT_INVENTORY pi ON pdf.product_id = pi.product_id
        JOIN DEMAND_FORECAST df ON pdf.product_id = df.product_id
        WHERE pi.quantity_available < (pdf.safety_stock * 1.5)
        ORDER BY days_of_supply ASC
        """
    
    @staticmethod
    def customer_lifetime_value_insights():
        """Top customers by LTV"""
        return """
        SELECT TOP 10
            c.customer_name,
            clv.total_revenue,
            clv.predicted_ltv,
            clv.renewal_likelihood_percent,
            clv.average_order_value,
            clv.total_orders
        FROM CUSTOMER_LIFETIME_VALUE clv
        JOIN CUSTOMERS c ON clv.customer_id = c.customer_id
        ORDER BY clv.predicted_ltv DESC
        """