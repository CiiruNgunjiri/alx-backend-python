import sqlite3
import functools

def log_queries():
    """
    Decorator factory that returns a decorator for logging SQL queries.
    Logs the SQL query before executing the decorated function.
    Assumes the SQL query is passed as a keyword argument 'query' or as the first positional argument.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract the SQL query from kwargs or args
            query = kwargs.get('query', None)
            if query is None and len(args) > 0:
                query = args[0]
            # Log the query
            print(f"[LOG] Executing SQL query: {query}")
            # Call the original function
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

# Example usage: fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")

