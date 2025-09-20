import sqlite3

class Database:
    """
    Database class for managing SQLite database connection and operations.
    
    Attributes:
         conn (sqlite3.Connection): The SQLite database connection object.
         cursor (sqlite3.Cursor): The cursor object for executing SQL queries.
    
    Methods:
         __init__(): Initializes the database connection and cursor.
         close(): Closes the database connection.
    """
    def __init__(self):
        self.conn = sqlite3.connect('crowdfunding.db')
        self.cursor = self.conn.cursor()
        self.cursor.row_factory = sqlite3.Row  # For dict-like access

    def close(self):
        self.conn.close()