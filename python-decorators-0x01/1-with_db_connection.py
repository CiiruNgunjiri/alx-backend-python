import sqlite3
import functools

def with_db_connection(func):
    """
    Decorator to automatically open a SQLite database connection,
    pass the connection object as the first argument to the decorated function,
    and ensure the connection is closed after the function completes,
    even if an exception occurs.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open the database connection
        conn = sqlite3.connect('users.db')
        try:
            # Pass the connection as the first argument to the decorated function
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Ensure the connection is closed regardless of success or error
            conn.close()
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# Fetch user by ID with automatic connection handling
user = get_user_by_id(user_id=1)
print(user)

