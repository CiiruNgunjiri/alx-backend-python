#!/usr/bin/python3

import mariadb
from itertools import islice
stream_users = __import__('0-stream_users')

# iterate over the generator function and print only the first 6 rows

for user in islice(stream_users.stream_users(), 6):
    print(user)
