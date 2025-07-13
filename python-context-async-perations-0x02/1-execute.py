import sqlite3

class ExecuteQuery:
    """
    Custom context manager that manages database connection and executes
    a given query with parameters, returning the results.
    """
    def __init__(self, query, params=None, db_path='users.db'):
        self.query = query
        self.params = params or ()
        self.db_path = db_path
        self.conn = None
        self.results = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        cursor.execute(self.query, self.params)
        self.results = cursor.fetchall()
        return self.results

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
        # Propagate exceptions if any
        return False

if __name__ == "__main__":
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)

    with ExecuteQuery(query, params) as results:
        for row in results:
            print(row)

