"""Intelligent sales data agent that queries Snowflake and flags operational alerts."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Iterable, List, Sequence

from src.config import Config, SemanticLayer
from src.queries import SalesQueries
from src.snowflake_client import SnowflakeClient

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class SalesDataAgent:
    """AI sales data agent that runs Snowflake analyses and emits daily reports."""

    def __init__(self) -> None:
        """Validate config, load semantic metadata, and connect to Snowflake."""
        Config.validate()
        self.semantic_layer = SemanticLayer()
        self.client = SnowflakeClient(
            account=Config.SNOWFLAKE_ACCOUNT,
            user=Config.SNOWFLAKE_USER,
            password=Config.SNOWFLAKE_PASSWORD,
            database=Config.SNOWFLAKE_DATABASE,
            warehouse=Config.SNOWFLAKE_WAREHOUSE,
        )
        self.client.connect()

    @staticmethod
    def _row_values(row: Any) -> Sequence[Any]:
        """Return cell values from a tuple/list row or a mapping row."""
        if isinstance(row, dict):
            return list(row.values())
        return row

    @classmethod
    def _rows_with_status(cls, results: Iterable[Any], status: str) -> List[Any]:
        """Return rows that contain the given status string."""
        matches = []
        for row in results or []:
            if status in [str(value) for value in cls._row_values(row)]:
                matches.append(row)
        return matches

    def get_daily_sales_summary(self) -> List[Any]:
        """Fetch today's sales totals, deal counts, and average deal size by rep."""
        logger.info("📊 Generating daily sales summary...")
        query = SalesQueries.daily_sales_summary()
        return self.client.execute_and_log(
            agent_action="DAILY_SALES_SUMMARY",
            query=query,
            query_type="SELECT",
            table_name="ORDERS,SALES_REPS",
        )

    def get_sales_rep_performance(self, month: str = "2024-01") -> List[Any]:
        """Fetch quota attainment for a month and warn on underperforming reps."""
        logger.info(f"📈 Analyzing sales rep performance for {month}...")
        query = SalesQueries.sales_rep_performance(month)
        results = self.client.execute_and_log(
            agent_action="REP_PERFORMANCE",
            query=query,
            query_type="SELECT",
            table_name="SALES_PERFORMANCE,SALES_REPS",
        )
        underperforming = self._rows_with_status(results, "UNDERPERFORMING")
        if underperforming:
            logger.warning(
                f"⚠️ {len(underperforming)} sales rep(s) are UNDERPERFORMING for {month}"
            )
        return results

    def get_product_demand_trends(self) -> List[Any]:
        """Fetch product demand trends and log high-growth products."""
        logger.info("📦 Analyzing product demand trends...")
        query = SalesQueries.product_demand_trends()
        results = self.client.execute_and_log(
            agent_action="PRODUCT_TRENDS",
            query=query,
            query_type="SELECT",
            table_name="PRODUCT_DEMAND_FREQUENCY",
        )
        high_growth = self._rows_with_status(results, "HIGH_GROWTH")
        if high_growth:
            logger.info(f"📈 {len(high_growth)} product(s) flagged as HIGH_GROWTH")
        return results

    def get_churn_risk_accounts(self) -> List[Any]:
        """Fetch churn-risk accounts and warn on high-risk customers."""
        logger.info("🚨 Identifying churn risk accounts...")
        query = SalesQueries.churn_risk_accounts()
        results = self.client.execute_and_log(
            agent_action="CHURN_ALERT",
            query=query,
            query_type="SELECT",
            table_name="CUSTOMER_LIFETIME_VALUE,CUSTOMERS",
        )
        high_risk = self._rows_with_status(results, "HIGH_RISK")
        if high_risk:
            logger.warning(f"🚨 {len(high_risk)} account(s) flagged as HIGH_RISK")
        return results

    def get_manufacturing_schedule(self, forecast_month: str = "2024-02") -> List[Any]:
        """Fetch manufacturing schedule and warn on urgent or overdue items."""
        logger.info(f"🏭 Creating manufacturing schedule for {forecast_month}...")
        query = SalesQueries.manufacturing_schedule(forecast_month)
        results = self.client.execute_and_log(
            agent_action="MANUFACTURING_SCHEDULE",
            query=query,
            query_type="SELECT",
            table_name="DEMAND_FORECAST,PRODUCT_INVENTORY",
        )
        urgent = self._rows_with_status(results, "URGENT")
        overdue = self._rows_with_status(results, "OVERDUE")
        if urgent or overdue:
            logger.warning(
                f"⚠️ Manufacturing alerts: {len(urgent)} URGENT, {len(overdue)} OVERDUE"
            )
        return results

    def get_inventory_alerts(self) -> List[Any]:
        """Fetch inventory alerts and log critical/warning stock levels."""
        logger.info("📦 Checking inventory levels...")
        query = SalesQueries.inventory_alerts()
        results = self.client.execute_and_log(
            agent_action="INVENTORY_ALERTS",
            query=query,
            query_type="SELECT",
            table_name="PRODUCT_DEMAND_FREQUENCY,PRODUCT_INVENTORY,DEMAND_FORECAST",
        )
        critical = self._rows_with_status(results, "CRITICAL")
        warning = self._rows_with_status(results, "WARNING")
        if critical:
            logger.error(f"🔴 {len(critical)} product(s) at CRITICAL stock level")
        if warning:
            logger.warning(f"⚠️ {len(warning)} product(s) at WARNING stock level")
        return results

    def get_customer_ltv_insights(self) -> List[Any]:
        """Fetch top customers ranked by predicted lifetime value."""
        logger.info("💰 Analyzing customer lifetime value...")
        query = SalesQueries.customer_ltv_insights()
        return self.client.execute_and_log(
            agent_action="CUSTOMER_LTV",
            query=query,
            query_type="SELECT",
            table_name="CUSTOMER_LIFETIME_VALUE,CUSTOMERS",
        )

    def generate_daily_report(self) -> Dict[str, Any]:
        """Run all sales analyses and return a combined daily report."""
        logger.info("=" * 70)
        logger.info("🤖 SNOWFLAKE SALES DATA AGENT - DAILY REPORT")
        logger.info("=" * 70)

        report = {
            "timestamp": datetime.now().isoformat(),
            "execution_status": "SUCCESS",
            "reports": {
                "daily_sales": self.get_daily_sales_summary(),
                "rep_performance": self.get_sales_rep_performance(),
                "product_trends": self.get_product_demand_trends(),
                "churn_alerts": self.get_churn_risk_accounts(),
                "manufacturing": self.get_manufacturing_schedule(),
                "inventory": self.get_inventory_alerts(),
                "customer_insights": self.get_customer_ltv_insights(),
            },
        }

        logger.info("✅ REPORT GENERATION COMPLETE")
        logger.info("=" * 70)
        return report

    def close(self) -> None:
        """Close the Snowflake connection used by the agent."""
        self.client.close()


if __name__ == "__main__":
    try:
        agent = SalesDataAgent()
        agent.generate_daily_report()
        agent.close()
        logger.info("✓ Agent execution successful")
    except Exception as e:
        logger.error(f"✗ Agent failed: {str(e)}")
        raise
