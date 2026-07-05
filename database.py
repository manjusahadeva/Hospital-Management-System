import mysql.connector
from mysql.connector import Error
import os
import config


class DBConnection:
    """
    Context manager for managing MySQL connections and cursors.
    """

    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        try:
            self.conn = mysql.connector.connect(
                host=config.DB_HOST,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                database=config.DB_NAME,
                port=config.DB_PORT
            )

            self.cursor = self.conn.cursor(dictionary=True)
            return self.conn, self.cursor

        except Error as e:
            print(f"\n[Database Error] Failed to connect: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()

        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
                print("\nTransaction Rolled Back.")

            self.conn.close()


def initialize_database():
    """
    Create database if it doesn't exist and execute schema.sql.
    """

    try:
        # -----------------------------
        # Create Database
        # -----------------------------
        conn = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            port=config.DB_PORT
        )

        cursor = conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.DB_NAME}")

        conn.commit()

        cursor.close()
        conn.close()

        # -----------------------------
        # Read schema.sql
        # -----------------------------
        schema_path = os.path.join(
            os.path.dirname(__file__),
            "sql",
            "schema.sql"
        )

        if not os.path.exists(schema_path):
            print(f"Schema file not found: {schema_path}")
            return False

        with open(schema_path, "r", encoding="utf-8") as file:
            sql_script = file.read()

        # -----------------------------
        # Connect to database
        # -----------------------------
        conn = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            port=config.DB_PORT
        )

        cursor = conn.cursor()

        # -----------------------------
        # Execute SQL Statements
        # -----------------------------
        sql_commands = sql_script.split(";")

        for command in sql_commands:
            command = command.strip()

            if command:
                try:
                    cursor.execute(command)
                except Error as err:
                    print(f"\nSQL Error:\n{err}")
                    print(f"\nFailed Query:\n{command}\n")

        conn.commit()

        cursor.close()
        conn.close()

        print("\nDatabase initialized successfully!")

        return True

    except Error as e:
        print(f"\n[Database Init Error] {e}")
        return False