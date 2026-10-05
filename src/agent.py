import logging
from src.snowflake_client import SnowflakeClient
from src.queries import SalesQueries
from src.config import Config
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SalesDataAgent:
    """AI Sales Data Agent for Snowflake"""
    
    def __init__(self):
        """Initialize agent with Snowflake connection"""
        Config.validate()
        self.client = SnowflakeClient(
            account=Config.SNOWFLAKE_ACCOUNT,
            user=Config.SNOWFLAKE_USER,
            password=Config.SNOWFLAKE_PASSWORD,
            database=Config.SNOWFLAKE_DATABASE,
            warehouse=Config.SNOWFLAKE_WAREHOUSE
        )
        self.client.connect()
    
    def get_daily_sales_summary(self):
        """Get daily sales summary"""
        logger.info("Generating daily sales summary...")
        query = SalesQueries.daily_sales_summary()
        results = self.client.execute_and_log(
            agent_action='DAILY_SALES_SUMMARY',
            query=query,
            query_type='SELECT',
            table_name='ORDERS,SALES_REPS'
        )
        return results
    
    def get_sales_rep_performance(self, month='2024-01'):
        """Get sales rep performance metrics"""
        logger.info(f"Getting rep performance for {month}...")
        query = SalesQueries.sales_rep_performance(month)
        results = self.client.execute_and_log(
            agent_action='REP_PERFORMANCE',
            query=query,
            query_type='SELECT',
            table_name='SALES_PERFORMANCE,SALES_REPS'
        )
        return results
    
    def get_product_demand_trends(self):
        """Get product demand trends"""
        logger.info("Analyzing product demand trends...")
        query = SalesQueries.product_demand_trends()
        results = self.client.execute_and_log(
            agent_action='PRODUCT_TRENDS',
            query=query,
            query_type='SELECT',
            table_name='PRODUCT_DEMAND_FREQUENCY'
        )
        return results
    
    def get_churn_risk_accounts(self):
        """Get high-risk accounts"""
        logger.info("Identifying churn risk accounts...")
        query = SalesQueries.churn_risk_accounts()
        results = self.client.execute_and_log(
            agent_action='CHURN_ALERT',
            query=query,
            query_type='SELECT',
            table_name='CUSTOMER_LIFETIME_VALUE,CUSTOMERS'
        )
        return results
    
    def get_manufacturing_schedule(self, forecast_month='2024-02'):
        """Get manufacturing schedule"""
        logger.info(f"Getting manufacturing schedule for {forecast_month}...")
        query = SalesQueries.manufacturing_schedule(forecast_month)
        results = self.client.execute_and_log(
            agent_action='MANUFACTURING_SCHEDULE',
            query=query,
            query_type='SELECT',
            table_name='DEMAND_FORECAST,PRODUCT_INVENTORY'
        )
        return results
    
    def get_inventory_alerts(self):
        """Get inventory alerts"""
        logger.info("Checking inventory levels...")
        query = SalesQueries.inventory_alerts()
        results = self.client.execute_and_log(
            agent_action='INVENTORY_ALERTS',
            query=query,
            query_type='SELECT',
            table_name='PRODUCT_DEMAND_FREQUENCY,PRODUCT_INVENTORY,DEMAND_FORECAST'
        )
        return results
    
    def get_customer_ltv_insights(self):
        """Get customer LTV insights"""
        logger.info("Analyzing customer lifetime value...")
        query = SalesQueries.customer_ltv_insights()
        results = self.client.execute_and_log(
            agent_action='CUSTOMER_LTV',
            query=query,
            query_type='SELECT',
            table_name='CUSTOMER_LIFETIME_VALUE,CUSTOMERS'
        )
        return results
    
    def generate_daily_report(self):
        """Generate comprehensive daily report"""
        logger.info("=" * 50)
        logger.info("GENERATING DAILY SALES REPORT")
        logger.info("=" * 50)
        
        report = {
            'timestamp': str(datetime.now()),
            'sales_summary': self.get_daily_sales_summary(),
            'rep_performance': self.get_sales_rep_performance(),
            'product_trends': self.get_product_demand_trends(),
            'churn_alerts': self.get_churn_risk_accounts(),
            'manufacturing': self.get_manufacturing_schedule(),
            'inventory': self.get_inventory_alerts(),
            'customer_insights': self.get_customer_ltv_insights()
        }
        
        logger.info("=" * 50)
        logger.info("REPORT COMPLETE")
        logger.info("=" * 50)
        return report
    
    def close(self):
        """Close agent connection"""
        self.client.close()

if __name__ == "__main__":
    from datetime import datetime
    
    try:
        agent = SalesDataAgent()
        report = agent.generate_daily_report()
        print(json.dumps(str(report), indent=2))
        agent.close()
    except Exception as e:
        logger.error(f"Agent failed: {str(e)}")
        raise