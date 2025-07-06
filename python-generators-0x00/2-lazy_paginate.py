#!/usr/bin/python3
seed = __import__('seed')

def paginate_users(page_size, offset):
    """
    Fetch a page of users from the database with LIMIT and OFFSET.
    Returns a list of dictionaries representing users.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows

def lazy_pagination(page_size):
    """
    Generator that lazily fetches pages of users from the database.
    Fetches the next page only when needed.
    Uses only one loop.
    """
    offset = 0

    while True:
        # Fetch the next page using paginate_users
        page = paginate_users(page_size, offset)
        if not page:
            # No more data, stop iteration
            break

        yield page  # Yield the current page (list of user dicts)

        # Increase offset for the next page
        offset += page_size

