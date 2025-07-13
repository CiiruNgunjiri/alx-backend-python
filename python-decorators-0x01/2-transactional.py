import sqlite3
import functools
import logging
import time

# Configure a logger for database operations
logger = logging.getLogger("db_decorators")
logger.setLevel(logging.DEBUG)  # Change as needed
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def with_db_connection(db_path='users.db'):
    """
    Decorator factory to create a decorator that manages opening and closing
    a database connection to the specified db_path.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            conn = sqlite3.connect(db_path)
            logger.debug(f"Opened connection to {db_path}")
            try:
                return func(conn, *args, **kwargs)
            finally:
                conn.close()
                logger.debug(f"Closed connection to {db_path}")
        return wrapper
    return decorator

def transactional(retries=0, delay=1):
    """
    Decorator factory to create a decorator that wraps a function in a database transaction.
    Automatically commits on success, rolls back on failure.
    Supports optional retries on failure with delay between attempts.
    
    Parameters:
    - retries (int): Number of times to retry on failure (default 0 = no retry)
    - delay (int or float): Seconds to wait between retries
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(conn, *args, **kwargs):
            attempts = 0
            while True:
                try:
                    result = func(conn, *args, **kwargs)
                    conn.commit()
                    logger.debug("Transaction committed successfully.")
                    return result
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Transaction failed and rolled back: {e}")
                    attempts += 1
                    if attempts > retries:
                        logger.error(f"Exceeded maximum retries ({retries}). Raising exception.")
                        raise
                    else:
                        logger.info(f"Retrying transaction in {delay} seconds... (Attempt {attempts}/{retries})")
                        time.sleep(delay)
        return wrapper
    return decorator

# Example usage with extended decorators

@with_db_connection(db_path='users.db')
@transactional(retries=3, delay=2)
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    logger.info(f"Updated email for user_id={user_id} to {new_email}")

if __name__ == "__main__":
    # Update user's email with automatic connection, transaction, and retry handling
    try:
        update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
        logger.info("User email updated successfully.")
    except Exception as e:
        logger.error(f"Failed to update user email: {e}")

