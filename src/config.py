import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for Snowflake agent"""
    
    SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
    SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
    SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
    SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE')
    SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
    
    # Validation
    @staticmethod
    def validate():
        required = ['SNOWFLAKE_ACCOUNT', 'SNOWFLAKE_USER', 'SNOWFLAKE_PASSWORD', 
                   'SNOWFLAKE_DATABASE', 'SNOWFLAKE_WAREHOUSE']
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing environment variables: {missing}")