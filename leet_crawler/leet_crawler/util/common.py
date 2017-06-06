import json
import sys
import time
import traceback

DEBUG = False
START_TIME = time.time()

# def get_questions():
#     with open('data/questions_meta.json', 'r') as f:
#         f_dict = json.loads(f.read())
#     return f_dict


# print processing message
def log(line):
    global DEBUG
    global START_TIME
    if DEBUG:
        print("DEBUG: " + str(round(float(time.time() - START_TIME), 3)) + "s - " + str(line), end='\r')

# print error message and exit program with errorcode 1
def elog(err, description=None):
    traceback.print_stack()
    sys.stderr.write("LEET ERROR: " + str(err) + "\nDESCRIPTION: " + str(description) + "\n")
    sys.exit(1)