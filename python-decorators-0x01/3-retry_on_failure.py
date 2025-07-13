import time
import sqlite3
import functools

def with_db_connection(func):
    """
    Decorator to automatically open a SQLite database connection,
    pass the connection object as the first argument to the decorated function,
    and ensure the connection is closed after the function completes.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

def retry_on_failure(retries=3, delay=2):
    """
    Decorator factory that retries the decorated function if it raises an exception.
    
    Parameters:
    - retries (int): Number of retry attempts before giving up.
    - delay (int or float): Seconds to wait between retries.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts > retries:
                        print(f"[ERROR] Function '{func.__name__}' failed after {retries} retries. Exception: {e}")
                        raise
                    else:
                        print(f"[WARNING] Function '{func.__name__}' failed with exception: {e}. Retrying {attempts}/{retries} after {delay} seconds...")
                        time.sleep(delay)
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Attempt to fetch users with automatic retry on failure
if __name__ == "__main__":
    try:
        users = fetch_users_with_retry()
        print("Fetched users successfully:")
        print(users)
    except Exception as e:
        print(f"Failed to fetch users: {e}")

