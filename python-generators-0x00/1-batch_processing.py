#!/usr/bin/python3
import mariadb

def stream_users_in_batches(batch_size):
    """
    Generator that fetches rows from user_data table in batches of size batch_size.
    Each batch is a list of dictionaries.
    """
    connection = None
    cursor = None
    try:
        # Connect to MariaDB ALX_prodev database
        connection = mariadb.connect(
            host='localhost',
            user='root',
            password='1395',
            database='ALX_prodev'
        )
        cursor = connection.cursor(dictionary=True)

        # Execute query to select all users
        cursor.execute("SELECT user_id, name, email, age FROM user_data")

        while True:
            # Fetch batch_size number of rows
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            yield batch

    except mariadb.Error as err:
        print(f"Database error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def batch_processing(batch_size):
    """
    Processes each batch from stream_users_in_batches and yields users over age 25.
    """
    # Loop 1: Iterate over batches from the generator
    for batch in stream_users_in_batches(batch_size):
        # Loop 2: Iterate over each user in the batch
        for user in batch:
            # Filter users over age 24
            if user['age'] > 25:
                yield user

