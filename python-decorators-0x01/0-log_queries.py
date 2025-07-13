import sqlite3
import functools
from datetime import datetime

def log_queries():
    """
    Decorator factory that logs the SQL query with a timestamp before executing the function.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            query = kwargs.get('query', None)
            if query is None and len(args) > 0:
                query = args[0]
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{current_time}] Executing SQL query: {query}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@log_queries()
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Fetch users while logging the query with timestamp
users = fetch_all_users(query="SELECT * FROM users")
