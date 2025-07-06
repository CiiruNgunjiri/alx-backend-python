
# Import Required Modules

import mariadb
import csv
import uuid

# Define connect_db() to Connect to MariaDB Server (without specifying a database)

def connect_db():
    try:
        connection = mariadb.connect(
            host='localhost',
            user='root',
            password='1395'
        )
        return connection
    except mariadb.Error as err:
        print(f"Error: {err}")
        return None

# Define create_database(connection) to Create ALX_prodev Database if Not Exists

def create_database(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
    cursor.close()


# Define connect_to_prodev() to Connect to ALX_prodev Database

def connect_to_prodev():
    try:
        connection = mariadb.connect(
            host='localhost',
            user='root',
            password='1395',
            database='ALX_prodev'
        )
        return connection
    except mariadb.Error as err:
        print(f"Error: {err}")
        return None

# Define create_table(connection) to Create user_data Table

def create_table(connection):
    cursor = connection.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS user_data (
        user_id CHAR(36) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        age DECIMAL NOT NULL,
        INDEX idx_user_id (user_id)
    )
    """
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()
    print("Table user_data created successfully")


# Define insert_data(connection, csv_file_path) to Insert Data from CSV

def insert_data(connection, csv_file_path):
    cursor = connection.cursor()
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            user_id = str(uuid.uuid4())
            name = row['name']
            email = row['email']
            age = row['age']

            # Check if email exists to avoid duplicates
            cursor.execute("SELECT email FROM user_data WHERE email = ?", (email,))
            if cursor.fetchone():
                continue

            insert_query = """
            INSERT INTO user_data (user_id, name, email, age)
            VALUES (?, ?, ?, ?)
            """
            cursor.execute(insert_query, (user_id, name, email, age))
    connection.commit()
    cursor.close()
