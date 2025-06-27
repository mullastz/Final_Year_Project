# detection_engine/db_clients.py

import psycopg2
import mysql.connector

class PostgreSQLClient:
    def __init__(self, host, port, user, password, dbname, **kwargs):
        self.conn = psycopg2.connect(
            host=host, port=port, user=user, password=password, dbname=dbname
        )
        self.cursor = self.conn.cursor()

    def fetch_tables(self):
        self.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        return [row[0] for row in self.cursor.fetchall()]

    def get_schema(self):
        """
        Returns a dictionary: table_name -> list of column names
        """
        schema = {}
        self.cursor.execute("""
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)
        rows = self.cursor.fetchall()
        for table, column in rows:
            schema.setdefault(table, []).append(column)
        return schema

    def close(self):
        self.cursor.close()
        self.conn.close()


class MySQLClient:
    def __init__(self, host, port, user, password, dbname, **kwargs):
        self.conn = mysql.connector.connect(
            host=host, port=port, user=user, password=password, database=dbname
        )
        self.cursor = self.conn.cursor()

    def fetch_tables(self):
        self.cursor.execute("SHOW TABLES")
        return [row[0] for row in self.cursor.fetchall()]

    def get_schema(self):
        """
        Returns a dictionary: table_name -> list of column names
        """
        schema = {}
        self.cursor.execute("""
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
            ORDER BY table_name, ordinal_position
        """)
        rows = self.cursor.fetchall()
        for table, column in rows:
            schema.setdefault(table, []).append(column)
        return schema

    def close(self):
        self.cursor.close()
        self.conn.close()
