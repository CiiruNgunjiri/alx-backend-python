#!/usr/bin/python3

import mariadb  # Import the MariaDB connector module to connect to MariaDB

def stream_users():
    """
    Generator function that streams rows from the user_data table one by one.
    Each row is yielded as a dictionary with keys: user_id, name, email, age.
    """
    cursor = None
    connection = None

    try:
        # Connect to the ALX_prodev database on MariaDB server
        connection = mariadb.connect(
            host='localhost',
            user='root',       # Replace with your MariaDB username
            password='1395',   # Replace with your MariaDB password
            database='ALX_prodev'
        )

        # Create a cursor that returns rows as dictionaries
        cursor = connection.cursor(dictionary=True)

        # Execute query to select all users from user_data
        cursor.execute("SELECT user_id, name, email, age FROM user_data")

        # Fetch and yield rows one by one using a single loop
        row = cursor.fetchone()
        while row:
            yield row
            row = cursor.fetchone()

    except mariadb.Error as err:
        print(f"Database error: {err}")

    finally:
        # Close cursor and connection if they were opened
        if cursor:
            cursor.close()
        if connection:
            connection.close()
