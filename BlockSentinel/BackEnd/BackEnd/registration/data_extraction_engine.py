from typing import List, Dict, Any, Tuple
import psycopg2
import mysql.connector
import sqlite3
from pymongo import MongoClient
import cx_Oracle

class BaseExtractor:
    def __init__(self, connection_details):
        self.connection = self.connect(connection_details)

    def connect(self, connection_details):
        raise NotImplementedError

    def extract_tables(self) -> List[Tuple[str, str]]:
        raise NotImplementedError

    def fetch_schema(self, schema: str, table: str):
        raise NotImplementedError

    def fetch_data(self, schema: str, table: str):
        raise NotImplementedError


# PostgreSQL
class PostgreSQLExtractor(BaseExtractor):
    def connect(self, connection_details):
        if 'database' not in connection_details:
            raise ValueError("Missing 'database' in PostgreSQL connection details.")
        return psycopg2.connect(
            host=connection_details['host'],
            port=connection_details['port'],
            user=connection_details['user'],
            password=connection_details['password'],
            dbname=connection_details['database']
        )

    def extract_tables(self):
        cur = self.connection.cursor()
        cur.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_type = 'BASE TABLE'
              AND table_schema NOT IN ('pg_catalog', 'information_schema')
        """)
        return cur.fetchall()

    def fetch_schema(self, schema, table):
        cur = self.connection.cursor()
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = %s AND table_name = %s;
        """, (schema, table))
        return cur.fetchall()

    def fetch_data(self, schema, table):
        cur = self.connection.cursor()
        cur.execute(f'SET search_path TO "{schema}";')
        cur.execute(f'SELECT * FROM "{table}"')
        return cur.fetchall()


# MySQL
class MySQLExtractor(BaseExtractor):
    def connect(self, connection_details):
        if 'database' not in connection_details:
            raise ValueError("Missing 'database' in MySQL connection details.")
        return mysql.connector.connect(
            host=connection_details['host'],
            port=connection_details['port'],
            user=connection_details['user'],
            password=connection_details['password'],
            database=connection_details['database']
        )

    def extract_tables(self):
        cur = self.connection.cursor()
        cur.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME 
            FROM information_schema.tables 
            WHERE TABLE_TYPE='BASE TABLE'
              AND TABLE_SCHEMA NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
        """)
        return cur.fetchall()

    def fetch_schema(self, schema, table):
        cur = self.connection.cursor()
        cur.execute(f"DESCRIBE `{schema}`.`{table}`")
        return cur.fetchall()

    def fetch_data(self, schema, table):
        cur = self.connection.cursor()
        cur.execute(f"SELECT * FROM `{schema}`.`{table}`")
        return cur.fetchall()


# SQLite
class SQLiteExtractor(BaseExtractor):
    def connect(self, connection_details):
        return sqlite3.connect(connection_details['path'])

    def extract_tables(self):
        cur = self.connection.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [("main", row[0]) for row in cur.fetchall()]

    def fetch_schema(self, schema, table):
        cur = self.connection.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        return cur.fetchall()

    def fetch_data(self, schema, table):
        cur = self.connection.cursor()
        cur.execute(f"SELECT * FROM {table}")
        return cur.fetchall()


# MongoDB
class MongoDBExtractor(BaseExtractor):
    def connect(self, connection_details):
        client = MongoClient(connection_details['uri'])
        self.db = client[connection_details['database']]
        return self.db

    def extract_tables(self):
        return [("default", name) for name in self.connection.list_collection_names()]

    def fetch_schema(self, schema, table):
        sample = self.connection[table].find_one()
        return list(sample.keys()) if sample else []

    def fetch_data(self, schema, table):
        return list(self.connection[table].find())


# Oracle
class OracleExtractor(BaseExtractor):
    def connect(self, connection_details):
        dsn = cx_Oracle.makedsn(
            connection_details['host'],
            connection_details['port'],
            sid=connection_details['sid']
        )
        return cx_Oracle.connect(connection_details['user'], connection_details['password'], dsn)

    def extract_tables(self):
        cur = self.connection.cursor()
        cur.execute("""
            SELECT owner, table_name 
            FROM all_tables 
            WHERE owner NOT IN ('SYS', 'SYSTEM', 'OUTLN', 'XDB', 'DBSNMP', 'ORDDATA', 'CTXSYS')
        """)
        return cur.fetchall()

    def fetch_schema(self, schema, table):
        cur = self.connection.cursor()
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM all_tab_columns 
            WHERE owner = '{schema.upper()}' AND table_name = '{table.upper()}'
        """)
        return cur.fetchall()

    def fetch_data(self, schema, table):
        cur = self.connection.cursor()
        cur.execute(f'SELECT * FROM "{schema.upper()}"."{table.upper()}"')
        return cur.fetchall()


# 🔹 Normalizer
def _normalize_rows(rows: Any) -> List[List[str]]:
    normalized = []
    if isinstance(rows, list):
        if all(isinstance(row, dict) for row in rows):  # MongoDB
            for row in rows:
                normalized.append([str(value) for value in row.values()])
        else:  # SQL rows as tuple/list
            for row in rows:
                normalized.append([str(value) for value in row])
    return normalized


# Dispatcher
def extract_data(db_type: str, conn_info: Dict[str, Any], system_id: str, db_name: str) -> Dict[str, Any]:
    extractors = {
        "PostgreSQL": PostgreSQLExtractor,
        "MySQL": MySQLExtractor,
        "SQLite": SQLiteExtractor,
        "MongoDB": MongoDBExtractor,
        "Oracle": OracleExtractor
    }

    extractor_class = extractors.get(db_type)
    if not extractor_class:
        raise ValueError(f"Unsupported DB type: {db_type}")

    extractor = extractor_class(conn_info)
    tables = extractor.extract_tables()

    result = {
        system_id: {
            db_name: {
                "dbType": db_type,
                "tables": len(tables),
                "data": {},
                "messages": []
            }
        }
    }

    for idx, (schema, table) in enumerate(tables, start=1):
        try:
            schema_data = extractor.fetch_schema(schema, table)
            rows = extractor.fetch_data(schema, table)

            table_info = {
                "table_name": table,
                "schema_name": schema,
                "columns": len(schema_data),
                "rows": len(rows),
                "data": {
                    "schema": schema_data,
                    "rows": _normalize_rows(rows)
                }
            }

            result[system_id][db_name]["data"][f"{schema}.{table}"] = table_info

            if not rows:
                result[system_id][db_name]["messages"].append(
                    f'No data in table "{schema}.{table}"'
                )

        except Exception as e:
            result[system_id][db_name]["messages"].append(
                f'Error extracting from "{schema}.{table}": {str(e)}'
            )

    return result
