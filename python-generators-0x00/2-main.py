#!/usr/bin/python3
import sys
processing = __import__('1-batch_processing')

# Print processed users in batches of 50
try:
    for user in processing.batch_processing(50):
        print(user)
except BrokenPipeError:
    # Handle broken pipe error gracefully when piping output to commands like head
    sys.stderr.close()

