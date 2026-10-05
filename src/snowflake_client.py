"""Snowflake connection, query execution, and audit logging."""

import logging
import time
from typing import Any, List, Optional

import snowflake.connector

logger = logging.getLogger(__name__)


class SnowflakeClient:
    """Client for Snowflake database operations with query audit logging."""

    def __init__(
        self,
        account: str,
        user: str,
        password: str,
        database: str,
        warehouse: str,
    ) -> None:
        """Store Snowflake connection parameters.

        Args:
            account: Snowflake account identifier.
            user: Snowflake username.
            password: Snowflake password.
            database: Default database name.
            warehouse: Warehouse to use for queries.
        """
        self.account = account
        self.user = user
        self.password = password
        self.database = database
        self.warehouse = warehouse
        self.conn: Optional[Any] = None
        self.cursor: Optional[Any] = None

    @staticmethod
    def _sql_escape(value: str) -> str:
        """Escape single quotes for safe inclusion in SQL string literals."""
        return value.replace("'", "''")

    def connect(self) -> bool:
        """Connect to Snowflake and set the PUBLIC schema.

        Returns:
            True if the connection is established.

        Raises:
            Exception: If the connection or schema switch fails.
        """
        try:
            logger.info(f"Connecting to Snowflake account: {self.account}")
            self.conn = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                password=self.password,
                database=self.database,
                warehouse=self.warehouse,
                connect_timeout=30,
            )
            self.cursor = self.conn.cursor()
            self.cursor.execute("USE SCHEMA PUBLIC")
            logger.info("✓ Connected to Snowflake")
            return True
        except Exception as e:
            logger.error(f"✗ Connection failed: {type(e).__name__}: {e}")
            raise

    def execute_query(self, query: str) -> List[Any]:
        """Execute a SQL query and return all result rows.

        Args:
            query: SQL statement to execute.

        Returns:
            List of result rows.

        Raises:
            Exception: If query execution fails.
        """
        try:
            start_time = time.time()
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            execution_time_ms = (time.time() - start_time) * 1000
            logger.info(
                f"✓ Query executed in {execution_time_ms:.2f}ms, "
                f"returned {len(results)} rows"
            )
            return results
        except Exception as e:
            logger.error(f"✗ Query execution failed: {e}")
            raise

    def execute_and_log(
        self,
        agent_action: str,
        query: str,
        query_type: str = "SELECT",
        table_name: str = "UNKNOWN",
    ) -> List[Any]:
        """Execute a query and write a row to AGENT_QUERY_AUDIT.

        Args:
            agent_action: Name of the agent action that triggered the query.
            query: SQL statement to execute.
            query_type: SQL statement type (default SELECT).
            table_name: Table(s) involved in the query.

        Returns:
            List of result rows from the original query.

        Raises:
            Exception: If query execution fails (after writing a FAILED audit row).
        """
        start_time = time.time()
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            execution_time_ms = int((time.time() - start_time) * 1000)
            rows_returned = len(results)

            audit_query = f"""
            INSERT INTO AGENT_QUERY_AUDIT (
                execution_timestamp, agent_action, query_type, table_name,
                execution_time_ms, rows_returned, execution_status,
                warehouse_used, user_executed
            ) VALUES (
                CURRENT_TIMESTAMP(),
                '{self._sql_escape(agent_action)}',
                '{self._sql_escape(query_type)}',
                '{self._sql_escape(table_name)}',
                {execution_time_ms},
                {rows_returned},
                'SUCCESS',
                '{self._sql_escape(self.warehouse)}',
                '{self._sql_escape(self.user)}'
            )
            """
            self.cursor.execute(audit_query)
            self.conn.commit()

            logger.info(f"✓ {agent_action}: {rows_returned} rows in {execution_time_ms}ms")
            return results
        except Exception as e:
            error_msg = self._sql_escape(str(e))
            error_query = f"""
            INSERT INTO AGENT_QUERY_AUDIT (
                execution_timestamp, agent_action, query_type, table_name,
                execution_status, error_message, warehouse_used, user_executed
            ) VALUES (
                CURRENT_TIMESTAMP(),
                '{self._sql_escape(agent_action)}',
                '{self._sql_escape(query_type)}',
                '{self._sql_escape(table_name)}',
                'FAILED',
                '{error_msg}',
                '{self._sql_escape(self.warehouse)}',
                '{self._sql_escape(self.user)}'
            )
            """
            try:
                self.cursor.execute(error_query)
                self.conn.commit()
            except Exception as audit_error:
                logger.error(f"✗ Failed to write audit error row: {audit_error}")

            logger.error(f"✗ {agent_action} failed: {e}")
            raise

    def close(self) -> None:
        """Close the cursor and Snowflake connection if they exist."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Connection closed")
