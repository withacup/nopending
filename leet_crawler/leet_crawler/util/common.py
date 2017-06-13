import json
import sys
import time
import traceback
from util.data_settings import *
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

# since json.dumps will escape \n and \t, I have to use my own strategy
def replace_newline_tab(s):
    return s.replace('\r\n', NEW_LINE).replace('\n', NEW_LINE).replace('\t', TAB)

def recover_newline_tab(s):
    return s.replace(NEW_LINE, '\n').replace(TAB, '    ')

def to_int(s):
    return int(s)