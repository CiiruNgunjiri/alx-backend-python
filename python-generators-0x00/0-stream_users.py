
--Generator to Stream Rows One by One

def stream_rows(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, name, email, age FROM user_data")
    row = cursor.fetchone()
    while row:
        yield row
        row = cursor.fetchone()
    cursor.close()

