"""Flask web server for Snowflake chatbot using Cortex AI."""

import json
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from snowflake.snowpark import Session

load_dotenv()

app = Flask(__name__)

# Snowflake credentials
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')


def load_semantic_layer():
    """Load semantic layer files for schema context."""
    config_dir = Path(__file__).parent / "config"
    
    schema_context = {}
    
    try:
        with open(config_dir / "data_dictionary.json") as f:
            data_dict = json.load(f)
            schema_context['tables'] = data_dict.get('tables', [])
    except Exception as e:
        print(f"Warning: Could not load data_dictionary.json: {e}")
        schema_context['tables'] = []
    
    try:
        with open(config_dir / "table_relationships.json") as f:
            relationships = json.load(f)
            schema_context['relationships'] = relationships.get('relationships', [])
    except Exception as e:
        print(f"Warning: Could not load table_relationships.json: {e}")
        schema_context['relationships'] = []
    
    return schema_context


def create_schema_prompt(semantic_layer):
    """Create schema context string for Cortex."""
    tables = semantic_layer.get('tables', [])
    relationships = semantic_layer.get('relationships', [])
    
    schema_text = "SCHEMA CONTEXT:\n\n"
    
    # Add table definitions
    schema_text += "TABLES:\n"
    for table in tables:
        name = table.get('table_name', 'UNKNOWN')
        desc = table.get('description', '')
        columns = table.get('columns', [])
        
        schema_text += f"\n{name} - {desc}\n"
        schema_text += "Columns: "
        col_names = [col.get('column_name', '') for col in columns]
        schema_text += ", ".join(col_names) + "\n"
    
    # Add relationships
    if relationships:
        schema_text += "\n\nTABLE RELATIONSHIPS:\n"
        for rel in relationships:
            schema_text += f"{rel}\n"
    
    return schema_text


def create_snowflake_session():
    """Create Snowflake session."""
    try:
        session = Session.builder.configs({
            "account": SNOWFLAKE_ACCOUNT,
            "user": SNOWFLAKE_USER,
            "password": SNOWFLAKE_PASSWORD,
            "database": SNOWFLAKE_DATABASE,
            "warehouse": SNOWFLAKE_WAREHOUSE,
        }).create()
        return session
    except Exception as e:
        raise Exception(f"Failed to connect to Snowflake: {str(e)}")


def generate_sql_from_question(session, question, schema_prompt):
    """Use Snowflake Cortex to generate SQL from natural language question."""
    try:
        prompt = f"""{schema_prompt}

USER QUESTION: {question}

Generate ONLY the SQL query to answer this question. 
Do NOT include any explanation or markdown.
Return ONLY the pure SQL statement."""
        
        response = session.sql(
            "SELECT snowflake.cortex.complete('snowflake-arctic', ?) as result",
            params=[prompt]
        ).collect()
        
        sql = response[0]['RESULT']
        return sql.strip()
    except Exception as e:
        raise Exception(f"Failed to generate SQL: {str(e)}")


def execute_sql_in_snowflake(session, sql):
    """Execute SQL query in Snowflake and return results."""
    try:
        results = session.sql(sql).collect()
        
        # Convert to list of dicts
        data = []
        for row in results:
            if hasattr(row, 'as_dict'):
                data.append(row.as_dict())
            else:
                # Handle tuple results
                data.append(dict(enumerate(row)))
        
        return data
    except Exception as e:
        raise Exception(f"Failed to execute query: {str(e)}")


@app.route('/')
def index():
    """Serve chat interface."""
    return render_template('chat.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle user questions and return results."""
    try:
        data = request.get_json()
        question = data.get('message', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Please enter a question'
            })
        
        # Load semantic layer
        semantic_layer = load_semantic_layer()
        schema_prompt = create_schema_prompt(semantic_layer)
        
        # Create Snowflake session
        session = create_snowflake_session()
        
        # Generate SQL from question
        sql = generate_sql_from_question(session, question, schema_prompt)
        
        # Execute SQL
        results = execute_sql_in_snowflake(session, sql)
        
        # Close session
        session.close()
        
        return jsonify({
            'success': True,
            'data': results,
            'sql': sql  # Include generated SQL for transparency
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)