import json, sys, time, traceback, re
from util.data_settings import *
from os import path
START_TIME = time.time()

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

"""
    This function removes cpp and java comment from both clean code and escaped code
"""
def remove_cjcomment(code):
    # return re.sub('//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"', '', code, flags=re.DOTALL)
    code = re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" ,code) # remove all occurance streamed comments (/*COMMENT */) from string
    code = re.sub(re.compile("//.*?\n" ) ,"" ,code) # remove all occurance singleline comments (//COMMENT\n ) from string
    code = re.sub(re.compile("//.*?--newline--" ) ,"" ,code) 
    return code

"""
    This function removes python inline comment from both clean code and escaped code
"""
def remove_pycomment(code):
    code = re.sub('#.*?--newline--', '', code)
    code = re.sub('#.*?\n', '', code)
    return code

def write_file(content, dir_name, f_name):
    try:
        with open(path.join(dir_name, f_name), 'w') as f:
            if not DEBUG:
                f.write(content)
            return True
    except IOError as err:
        return None

def read_file(dir_name, f_name):
    try:
        with open(path.join(dir_name, f_name), 'r') as f:
            return f.read()
    except IOError as err:
        return None

def JSONDumps(_dict):
    if type(_dict) not in [dict, list]:
        raise TypeError("_dict must be dict or list instead of {0}".format(str(type(_dict))))
    try:
        return json.dumps(_dict, indent=4)
    except json.JSONEncodeError as err:
        return None

def JSONLoads(_json):
    if type(_json) is not str:
        raise TypeError("_json must be str instead of {0}".format(str(type(_json))))
    try:
        return json.loads(_json)
    except json.JSONDecodeError as err:
        return None
