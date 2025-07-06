#!/usr/bin/python3
import mariadb

def stream_user_ages():
    """
    Generator that connects to the ALX_prodev database and yields user ages one by one.
    """
    connection = None
    cursor = None
    try:
        connection = mariadb.connect(
            host='localhost',
            user='root',           # Replace with your MariaDB username
            password='1395',       # Replace with your MariaDB password
            database='ALX_prodev'
        )
        cursor = connection.cursor()

        # Execute query to fetch only the age column for all users
        cursor.execute("SELECT age FROM user_data")

        # Fetch one age at a time and yield it
        age = cursor.fetchone()
        while age:
            yield age[0]  # age is a tuple like (age_value,)
            age = cursor.fetchone()

    except mariadb.Error as err:
        print(f"Database error: {err}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def calculate_average_age():
    """
    Uses stream_user_ages generator to calculate average age without loading all data at once.
    Uses no more than two loops.
    """
    total_age = 0
    count = 0

    # Loop 1: Iterate over ages yielded one by one
    for age in stream_user_ages():
        total_age += age
        count += 1

    if count == 0:
        print("No users found.")
        return

    average_age = total_age / count
    print(f"Average age of users: {average_age:.2f}")


if __name__ == "__main__":
    calculate_average_age()

