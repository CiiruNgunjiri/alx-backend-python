import time
import sqlite3
import functools
import threading
import hashlib
import json

# Thread-safe cache dictionary storing tuples of (timestamp, result)
query_cache = {}
cache_lock = threading.Lock()

def with_db_connection(func):
    """
    Opens and closes SQLite connection automatically.
    Passes connection as first argument to decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

def make_cache_key(query, params=None):
    """
    Creates a unique cache key by hashing the JSON serialization of the query and params.
    Ensures different queries or params generate different keys.
    """
    key_data = {
        "query": query,
        "params": params if params is not None else []
    }
    key_json = json.dumps(key_data, sort_keys=True)
    return hashlib.sha256(key_json.encode('utf-8')).hexdigest()

def cache_query(expiration=60):
    """
    Decorator factory to cache database query results with expiration and parameter support.

    Args:
        expiration (int): Cache expiration time in seconds (default 60).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract query and params from args or kwargs
            query = kwargs.get('query', None)
            params = kwargs.get('params', None)

            # Assuming function signature: func(conn, query, params=None)
            if query is None and len(args) > 1:
                query = args[1]
            if params is None and len(args) > 2:
                params = args[2]

            if query is None:
                raise ValueError("No SQL query string found in arguments.")

            cache_key = make_cache_key(query, params)

            with cache_lock:
                cache_entry = query_cache.get(cache_key)
                if cache_entry:
                    cached_time, result = cache_entry
                    if (time.time() - cached_time) < expiration:
                        print(f"[CACHE HIT] Returning cached result for query: {query} with params: {params}")
                        return result
                    else:
                        print(f"[CACHE EXPIRED] Cache expired for query: {query} with params: {params}")
                        del query_cache[cache_key]

            # Cache miss or expired, execute the query
            print(f"[CACHE MISS] Executing query: {query} with params: {params}")
            result = func(*args, **kwargs)

            with cache_lock:
                query_cache[cache_key] = (time.time(), result)

            return result
        return wrapper
    return decorator

@with_db_connection
@cache_query(expiration=120)  # Cache expires after 2 minutes
def fetch_users_with_cache(conn, query, params=None):
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    return cursor.fetchall()

if __name__ == "__main__":
    # First call caches the result
    users = fetch_users_with_cache(query="SELECT * FROM users WHERE id > ?", params=(0,))
    print(f"First fetch: {users}")

    # Second call returns cached result
    users_again = fetch_users_with_cache(query="SELECT * FROM users WHERE id > ?", params=(0,))
    print(f"Second fetch (from cache): {users_again}")

