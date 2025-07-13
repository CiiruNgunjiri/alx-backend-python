import sqlite3

class DatabaseConnection:
    """
    Custom class-based context manager for SQLite database connection.
    Opens the connection on entering the context and closes it on exit.
    """
    def __init__(self, db_path='users.db'):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
        # Returning False will propagate exceptions, True will suppress them
        # We return False to let exceptions propagate
        return False

if __name__ == "__main__":
    # Use the custom context manager to query the users table
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        for row in results:
            print(row)

