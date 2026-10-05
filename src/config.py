"""Configuration and semantic layer metadata for the Snowflake sales agent."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Manage Snowflake environment variables loaded from a .env file."""

    SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
    SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
    SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
    SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
    SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")

    @staticmethod
    def validate():
        """Check that all required Snowflake environment variables are set.

        Raises:
            ValueError: If one or more required variables are missing.
        """
        required = [
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER",
            "SNOWFLAKE_PASSWORD",
            "SNOWFLAKE_DATABASE",
            "SNOWFLAKE_WAREHOUSE",
        ]
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing environment variables: {missing}")


class SemanticLayer:
    """Load and query semantic layer metadata from JSON config files."""

    def __init__(self):
        """Load data dictionary, table relationships, and business context JSON."""
        self.config_dir = Path(__file__).resolve().parent.parent / "config"
        self.data_dictionary = self._load_json("data_dictionary.json")
        self.table_relationships = self._load_json("table_relationships.json")
        self.business_context = self._load_json("business_context.json")

    def _load_json(self, filename):
        """Load a JSON file from the config directory.

        Args:
            filename: Name of the JSON file to load.

        Returns:
            Parsed JSON as a dict, or an empty dict if the file is missing
            or cannot be parsed.
        """
        path = self.config_dir / filename
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError) as exc:
            print(f"Warning: could not load {path}: {exc}")
            return {}

    def _find_table(self, table_name):
        """Find a table entry in the data dictionary by name.

        Args:
            table_name: Name of the table to look up (case-insensitive).

        Returns:
            Matching table dict, or None if not found.
        """
        tables = self.data_dictionary.get("tables", [])
        target = table_name.upper()
        for table in tables:
            if table.get("table_name", "").upper() == target:
                return table
        return None

    def get_table_description(self, table_name):
        """Return the description for a table from the data dictionary.

        Args:
            table_name: Name of the table to describe.

        Returns:
            Table description string, or None if the table is not found.
        """
        table = self._find_table(table_name)
        if table is None:
            return None
        return table.get("description")

    def get_table_columns(self, table_name):
        """Return the columns list for a table from the data dictionary.

        Args:
            table_name: Name of the table whose columns to retrieve.

        Returns:
            List of column definitions, or an empty list if not found.
        """
        table = self._find_table(table_name)
        if table is None:
            return []
        return table.get("columns", [])

    def get_business_rule(self, rule_type):
        """Return a business rule by type from business_context.json.

        Args:
            rule_type: Key identifying the business rule to retrieve.

        Returns:
            The matching business rule value, or None if not found.
        """
        rules = self.business_context.get("business_rules", {})
        if isinstance(rules, dict):
            return rules.get(rule_type)
        if isinstance(rules, list):
            for rule in rules:
                if rule.get("rule_type") == rule_type or rule.get("type") == rule_type:
                    return rule
        return None

    def get_kpis(self):
        """Return KPIs defined in business_context.json.

        Returns:
            KPI definitions, or an empty dict if absent.
        """
        return self.business_context.get("kpis", {})
