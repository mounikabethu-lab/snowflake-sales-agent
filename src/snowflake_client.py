import snowflake.connector
from snowflake.connector.errors import DatabaseError, ProgrammingError
import time
import logging
from datetime import datetime
from src.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SnowflakeClient:
    """Snowflake connection and query execution with audit logging"""
    
    def __init__(self, account, user, password, database, warehouse):
        """Initialize Snowflake client"""
        self.account = account
        self.user = user
        self.password = password
        self.database = database
        self.warehouse = warehouse
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish connection to Snowflake"""
        try:
            logger.info(f"Connecting to Snowflake account: {self.account}")
            self.conn = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                password=self.password,
                database=self.database,
                warehouse=self.warehouse,
                connect_timeout=30
            )
            self.cursor = self.conn.cursor()
            logger.info("✓ Connected to Snowflake successfully")
            return True
        except DatabaseError as e:
            logger.error(f"✗ Database connection failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"✗ Connection error: {str(e)}")
            raise
    
    def execute_query(self, query: str, return_dict: bool = True):
        """Execute SELECT query and return results"""
        try:
            start_time = time.time()
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            execution_time = (time.time() - start_time) * 1000
            
            logger.info(f"✓ Query executed in {execution_time:.2f}ms, returned {len(results)} rows")
            return results
        except ProgrammingError as e:
            logger.error(f"✗ Query error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"✗ Execution error: {str(e)}")
            raise
    
    def execute_and_log(self, agent_action: str, query: str, query_type: str = 'SELECT', table_name: str = 'UNKNOWN'):
        """Execute query and log to AGENT_QUERY_AUDIT table"""
        try:
            start_time = time.time()
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            execution_time = int((time.time() - start_time) * 1000)
            rows_returned = len(results)
            
            # Log to audit table
            audit_query = f"""
            INSERT INTO AGENT_QUERY_AUDIT (
                execution_timestamp, agent_action, query_type, table_name,
                query_text, execution_time_ms, rows_returned, execution_status,
                warehouse_used, user_executed
            ) VALUES (
                CURRENT_TIMESTAMP(), 
                '{agent_action}', 
                '{query_type}', 
                '{table_name}',
                '{query.replace(chr(39), chr(39) + chr(39))}',
                {execution_time},
                {rows_returned},
                'SUCCESS',
                '{self.warehouse}',
                '{self.user}'
            )
            """
            self.cursor.execute(audit_query)
            self.conn.commit()
            
            logger.info(f"✓ {agent_action}: {rows_returned} rows in {execution_time}ms")
            return results
        except Exception as e:
            # Log failure
            error_msg = str(e).replace(chr(39), chr(39) + chr(39))
            error_query = f"""
            INSERT INTO AGENT_QUERY_AUDIT (
                execution_timestamp, agent_action, query_type, table_name,
                execution_status, error_message, warehouse_used, user_executed
            ) VALUES (
                CURRENT_TIMESTAMP(),
                '{agent_action}',
                '{query_type}',
                '{table_name}',
                'FAILED',
                '{error_msg}',
                '{self.warehouse}',
                '{self.user}'
            )
            """
            try:
                self.cursor.execute(error_query)
                self.conn.commit()
            except:
                pass
            
            logger.error(f"✗ {agent_action} failed: {str(e)}")
            raise
    
    def close(self):
        """Close Snowflake connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Connection closed")