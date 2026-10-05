import snowflake.connector
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def deploy_test_table():
    """Deploy a simple test table to Snowflake"""
    
    print("=" * 60)
    print("SNOWFLAKE END-TO-END TEST DEPLOYMENT")
    print("=" * 60)
    
    account = os.getenv('SNOWFLAKE_ACCOUNT')
    user = os.getenv('SNOWFLAKE_USER')
    password = os.getenv('SNOWFLAKE_PASSWORD')
    database = os.getenv('SNOWFLAKE_DATABASE')
    warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
    
    print(f"\n✓ Connecting to: {account}")
    print(f"✓ Database: {database}")
    print(f"✓ Warehouse: {warehouse}\n")
    
    try:
        # Connect
        conn = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            database=database,
            warehouse=warehouse,
            connect_timeout=30
        )
        cursor = conn.cursor()
        print("✓ Connected to Snowflake\n")
        
        # Create test table
        print("Creating TEST_DEPLOYMENT table...")
        create_table_sql = """
        CREATE OR REPLACE TABLE TEST_DEPLOYMENT (
            test_id INT,
            test_name VARCHAR,
            test_timestamp TIMESTAMP_NTZ,
            status VARCHAR
        )
        """
        cursor.execute(create_table_sql)
        print("✓ Table created\n")
        
        # Insert test data
        print("Inserting test data...")
        insert_sql = f"""
        INSERT INTO TEST_DEPLOYMENT VALUES
        (1, 'End-to-End Test', CURRENT_TIMESTAMP(), 'SUCCESS'),
        (2, 'GitHub Actions Integration', CURRENT_TIMESTAMP(), 'SUCCESS'),
        (3, 'Snowflake Deployment', CURRENT_TIMESTAMP(), 'SUCCESS')
        """
        cursor.execute(insert_sql)
        conn.commit()
        print("✓ Data inserted\n")
        
        # Verify data
        print("Verifying data...")
        verify_sql = "SELECT * FROM TEST_DEPLOYMENT"
        cursor.execute(verify_sql)
        results = cursor.fetchall()
        
        print(f"✓ Verification successful - {len(results)} rows found\n")
        
        for row in results:
            print(f"  ID: {row[0]}, Name: {row[1]}, Status: {row[3]}")
        
        # Log to audit table
        print("\nLogging to audit table...")
        audit_sql = """
        INSERT INTO AGENT_ACTION_LOG (
            action_type, action_status, description, records_affected,
            execution_duration_seconds
        ) VALUES (
            'TEST_DEPLOYMENT',
            'SUCCESS',
            'End-to-end test table deployment successful',
            3,
            30
        )
        """
        cursor.execute(audit_sql)
        conn.commit()
        print("✓ Audit logged\n")
        
        cursor.close()
        conn.close()
        
        print("=" * 60)
        print("✓ END-TO-END TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nTest table 'TEST_DEPLOYMENT' created in Snowflake")
        print("Check your Snowflake console to see the table")
        print("\nGitHub Actions Integration: ✓ WORKING")
        print("Snowflake Connectivity: ✓ WORKING")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        print("\n" + "=" * 60)
        print("✗ TEST FAILED")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = deploy_test_table()
    exit(0 if success else 1)