import json
import hashlib
import datetime
import os
import socket
from maths_module import getDatafileData

host = getDatafileData("serverIP")
port = getDatafileData("host")

def checksum(file): #used to generate checksums. Lets us know if code was tampered with.
    with open(file, "rb") as f: #rb = read in binary mode
        return hashlib.md5(str(f.read()).encode("utf")).hexdigest() #returns hash

def generateLog(exceptiontype, traceback, variables):

    userText = input("OpenPyFlySim has crashed! Please decribe any details prior to this event, or just press enter to send this report to the developer.")
    try:
        systemDetails = os.uname()
    except:
        systemDetails = '' # might not work on windows based on https://stackoverflow.com/questions/62798371/os-uname-function-not-working-in-windows
    
    crashReport = {
        "timestamp": str(datetime.datetime.now()),
        "exception": str(exceptiontype),
        "traceback": str(traceback),
        "variables": str(variables),
        "usertext": userText,
        "checksum": checksum("main.py"),
        "systemDetails": systemDetails,
        "logchecksum": "",
        "sent": 0 #determines whether the log has been sent to the developers
    }
    crashReport["logchecksum"] = hashlib.md5(str(crashReport).encode("utf")).hexdigest() #generate log's checksum
    
    with open(f"error_logs/{datetime.datetime.now()}.json", "w") as w:
        json.dump(crashReport, w)

    try:
        sendErrorLogs() #send the log, as well as any dormant unsent logs
    except:
        print("Server offline")

def sendFile(filepath):

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #connect to ipv4 and tcp
    connection.connect((host, port))

    #first, send a rts message
    connection.sendall(b"rts")
    response = connection.recv(1024).decode()
    if response != "cts":
        print("an error has occured in the network connection.")
    else:
        #Send the JSON file
        with open(filepath, 'rb') as f:
            data = f.read()
            connection.sendall(data)
            log = json.loads(data.decode())
        response = connection.recv(1024).decode()
        if response == "accepted":
            log["sent"] = 1 #marks as sent
            with open(filepath, 'w') as f: #rewrites the file with the new data
                json.dump(log, f)
            
    connection.close()

def sendErrorLogs(): #parses through all error logs to find ones that havent been sent yet (In case of network going down etc)
    files = os.listdir("error_logs")
    for fileName in files:
        with open(f"error_logs/{fileName}") as f:
            contents = json.loads(f.read())
            if contents["sent"] == 0: #indicates that the JSON file has not been sent yet
                sendFile(f"error_logs/{fileName}")
