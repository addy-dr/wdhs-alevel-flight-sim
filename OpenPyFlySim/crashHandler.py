import json
import hashlib
import datetime
import os
import socket

def checksum(file): #used to generate checksums. Lets us know if code was tampered with.
    with open(file, "rb") as f: #rb = read in binary mode
        return hashlib.file_digest(f, 'md5').hexdigest() #returns hash

def generateLog(exceptiontype, traceback, variables):

    userText = input("OpenPyFlySim has crashed! Please decribe any details prior to this event, or just press enter to send this report to the developer.")
    try:
        systemDetails = os.uname()
    except:
        systemDetails = '' # might not work on windows based on https://stackoverflow.com/questions/62798371/os-uname-function-not-working-in-windows
    
    crashReport = {
        "timestamp": datetime.datetime.now(),
        "exception": str(exceptiontype),
        "traceback": str(traceback),
        "variables": str(variables),
        "usertext": userText,
        "checksum": checksum("main.py"),
        "systemDetails": systemDetails,
        "logchecksum": ""
    }
    crashReport["logchecksum"] = hashlib.md5(str(crashReport).encode("utf")).hexdigest() #generate log's checksum
    
    with open(f"error_logs/{datetime.datetime.now()}.json", "w") as w:
        json.dump(crashReport, w)