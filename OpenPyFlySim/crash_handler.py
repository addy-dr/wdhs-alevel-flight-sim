import json
import hashlib
import datetime
import os
import socket
from maths_module import getDatafileData

host = getDatafileData("serverIP")
port = getDatafileData("host")

def checksum(file):
    """Used to generate checksums. 
    Lets us know if code was tampered with."""
    with open(file, "rb") as f: #   rb = read in binary mode
        # returns hash
        return hashlib.md5(str(f.read()).encode("utf")).hexdigest()

def generateLog(exceptiontype, traceback, variables):

    userText = input("""OpenPyFlySim has crashed! Please decribe any details prior
    to this event, or just press enter to send this report to the developer.""")
    try:
        systemDetails = os.uname()
    except:
        # os.uname works on linux, might not work on windows based on
        # https://stackoverflow.com/questions/62798371/os-uname-function-not-working-in-windows
        systemDetails = 'Unable to get OS details.'
    
    crashReport = {
        "timestamp": str(datetime.datetime.now()),
        "exception": str(exceptiontype),
        "traceback": str(traceback),
        "variables": str(variables),
        "usertext": userText,
        "checksum": checksum("flight_sim.py"),
        "systemDetails": systemDetails,
        "logchecksum": "",
        "sent": 0 # Determines whether the log has been sent to the developers
    }
    # Generate log's checksum
    crashReport["logchecksum"] = hashlib.md5(str(crashReport).encode("utf")).hexdigest()
    
    with open(f"error_logs/{datetime.datetime.now()}.json", "w") as w:
        json.dump(crashReport, w)

    try:
        # Send the log, as well as any dormant unsent logs
        sendErrorLogs()
    except:
        print("Server offline")

def sendFile(filepath):

    # Connect to ipv4 and tcp
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((host, port))

    # First, send a rts message
    connection.sendall(b"rts")
    response = connection.recv(1024).decode()
    if response != "cts":
        print("an error has occured in the network connection.")
    else:
        # Send the JSON file
        with open(filepath, 'rb') as f:
            data = f.read()
            connection.sendall(data)
            log = json.loads(data.decode())
        response = connection.recv(1024).decode()
        if response == "accepted":
            log["sent"] = 1 # Marks as sent
            with open(filepath, 'w') as f:
                # Rewrites the file with the new data
                json.dump(log, f)
            
    connection.close()

def sendErrorLogs():
    """parses through all error logs to find ones that
    haven't been sent yet (In case of network going down etc)"""
    files = os.listdir("error_logs")
    for fileName in files:
        with open(f"error_logs/{fileName}") as f:
            contents = json.loads(f.read())
            if contents["sent"] == 0:
                # Indicates that the JSON file has not been sent yet
                sendFile(f"error_logs/{fileName}")
