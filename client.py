# Client Side
# PLEASE USE PYTHON3

import sys
import json
from threading import Thread
import time
from socket import *

# Defines
SUCCESS_LOGIN = '1'
FAILURE_LOGIN = '0'
BLOCKED_LOGIN = '-1'
BANNED = '-2'
NO_USER = '-3'

# ////////////////////////////////////////////////////
# ///////////           FUNCTIONS       //////////////
# ////////////////////////////////////////////////////

def loginCheck(c_udp_port):

    # Each client should have a dictionary which holds their information;
    # username, password, udp_port and command request
    # i.e.
    # {
    #    "command":
    #    "username":
    #    "password":
    #    "port":
    #
    # }

    while True:
        u_name = input("Please enter your username: ")
        u_pass = input("Please enter your password: ")

        u_data = {
            "command": "login",
            "username": u_name,
            "password": u_pass,
            "port": c_udp_port
        }

        # Translate to server
        temp = json.dumps(u_data)
        cSocket.sendall(temp.encode())
        temp2 = cSocket.recv(2048)

        return_value = temp2.decode()

        # Conditions of logins
        if return_value == SUCCESS_LOGIN:
            print("Welcome to Miscord! :)")
            break
        
        elif return_value == FAILURE_LOGIN:
            print("Incorrect login. Please try again. >:(")
        
        elif return_value == BLOCKED_LOGIN:
            print("Incorrect login. Your account has been blocked from Miscord. Please try again later. :(")

        elif return_value == BANNED:
            print("Too many login attempts. Your account has been blocked. Please try again later. :/")

        elif return_value == NO_USER:
            print("No username found in the system. Please try again.")
        
    return u_name

def get_file():
    while True:
        cSocket2.settimeout(None)
        
        # To obtain uploader name
        uploader, cAdd = cSocket2.recvfrom(2048)
        uploader_name = uploader.decode()

        # To obtain file name
        f, cAdd = cSocket2.recvfrom(2048)
        f_name = f.decode()

        formatted = uploader_name + "_" + f_name

        # Now open file to transfer
        f = open(formatted, "wb")

        try:
            while True:
                cSocket2.settimeout(1)
                content, cAdd = cSocket2.recvfrom(2048)
                f.write(content)

        except timeout:
            f.close()
            print("\n")
            print("File received.")
            print("Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, OUT, UPD): ")

        


def broadcast_message(message):
    # Error testing
    if len(message.split(" ")) == 1:
        print("Error: Please enter a message when using this command.")
        return

    message = message.split(' ', 1)[1]

    # Info to translate to server
    u_data = {
        "command": "BCM",
        "message": message,
        "username": u_name
    }

    # Translate to server
    temp = json.dumps(u_data)
    cSocket.sendall(temp.encode())
    temp2 = cSocket.recv(2048)

    print(temp2.decode())

def dload_users(command):
    # Error testing
    if len(command.split(" ")) != 1:
        print("Error: There are additional arguments that are not required. Please try again.")
        return

    u_data = {
        "command": "ATU",
        "username": u_name,
        "valid": "1"
    }

    # Translate to server
    temp = json.dumps(u_data)
    cSocket.sendall(temp.encode())
    temp2 = cSocket.recv(2048)
    temp2 = temp2.decode()

    if temp2 == "empty":
        print("Error: There is noone else in the server.")
    else:
        print(temp2.strip())


def logout(command):
    u_data = {
        "command": "OUT",
        "username": u_name
    }

    # Translate to server
    temp = json.dumps(u_data)
    cSocket.sendall(temp.encode())
    temp2 = cSocket.recv(2048)
    temp2 = temp2.decode()

    print(temp2)

def upload_to_receiver(f_name, ip_address, udp_address):
    # Send to receiver first
    add = (ip_address, udp_address)
    cSocket2.sendto(u_name.encode(), add)
    cSocket2.sendto(f_name.encode(), add)

    f = open(f_name, "rb")
    content = f.read(2048)

    while (content):
        if (cSocket2.sendto(content, add)):
            content = f.read(2048)
        
    f.close()

def upload_file(command):
    # Error testing
    if len(command.split(" ")) != 3:
        print("Error: There are a wrong number of arguments entered. Please try again.")
        return

    receiver_name = command.split(" ")[1]
    file_name = command.split(" ")[2]

    # Check if the receiving user is active
    active_data = {
        "command": "ATU",
        "username": u_name,
        "valid": "0"

    }

    # Translate ATU command to server
    temp = json.dumps(active_data)
    cSocket.sendall(temp.encode())
    temp2 = cSocket.recv(2048)
    temp2 = temp2.decode()

    if receiver_name not in temp2:
        print("Error: The user is not online.")
        return

    # Now, upload file
    u_data = {
        "command": "UPD",
        "username": u_name,
        "receiver": receiver_name,
        "file": file_name
    }

    # Translate to server
    temp3 = json.dumps(u_data)
    cSocket.sendall(temp3.encode())
    temp4 = cSocket.recv(2048)
    temp4 = temp4.decode()

    # Split string into UDP and IP
    UDP_address = int(temp4.split(" ")[1])
    IP_address = (temp4.split(" ")[0])

    print("The file has been uploaded.")

    newT = Thread(target = upload_to_receiver, args = (file_name, IP_address, UDP_address))
    newT.daemon = True
    newT.start()


def create_room(command):
    # Error testing
    if len(command.split(" ")) == 1:
        print("Error: You cannot create a room by yourself.")
        return

    # Check if the users are active
    active_data = {
        "command": "ATU",
        "username": u_name,
        "valid": "0"
    }

    # Translate ATU command to server
    temp = json.dumps(active_data)
    cSocket.sendall(temp.encode())
    temp2 = cSocket.recv(2048)
    temp2 = temp2.decode()

    # Users list
    user_room = command.split(" ")[1:]

    if u_name in user_room:
        print("Error: You cannot create a room with yourself.")
        return

    if not all(x in temp2 for x in user_room):
        print("Error: These users are not available.")
        return

    # Now create the room
    u_data = {
        "command": "SRB",
        "username": u_name,
        "users": user_room
    }

    # Translate to server
    temp3 = json.dumps(u_data)
    cSocket.sendall(temp3.encode())
    temp4 = cSocket.recv(2048)
    temp4 = temp4.decode()

    if temp4.split(" ")[0] == "invalid":
        print("Error: A seperate room (ID: " + temp4.split(" ")[1] + ") has already been created for these users.")
    else:
        print(temp4)

def send_room_message(command):
    # Error testing
    if len(command.split(" ")) < 2:
        print("Error: Wrong input of the command. Please try again.")
        return

    message = " ".join(command.split(" ")[2:])

    u_data = {
        "command": "SRM",
        "username": u_name,
        "room_id": command.split(" ")[1],
        "message": message
    }

    # Translate to server
    temp = json.dumps(u_data)
    cSocket.sendall(temp.encode())
    temp2 = cSocket.recv(2048)
    temp2 = temp2.decode()

    if temp2 == "-1":
        print("The seperate room does not exist.")
    
    elif temp2 == "-2":
        print("You are not in this room.")

    else:
        print(temp2)

def read_messages(command):
    # Error testing
    if len(command.split(" ")) != 6 :
        print("Error: Wrong input of the command. Please try again.")
        return

    type_list = ["b", "s"]
    if command.split(" ")[1] not in type_list:
        print("Error: Wrong message type. Please enter either 'b' or 's'.")
        return

    time = command.split(" ")[2:]

    u_data = {
        "command": "RDM",
        "username": u_name,
        "timestamp": time,
        "message_type": command.split(" ")[1]
    }

    # Translate to server
    temp = json.dumps(u_data)
    cSocket.sendall(temp.encode())
    temp2 = cSocket.recv(2048)
    temp2 = temp2.decode()

    if temp2 == "empty":
        print("There has been no new messages of type '" + command.split(" ")[1] + "' since " + " ".join(time) + ".")
    else:
        print("Messages in seperate rooms since " + " ".join(time))
        print(temp2.strip())


# ////////////////////////////////////////////////////
# ///////////           MAIN            //////////////
# ////////////////////////////////////////////////////

# Error testing
if len(sys.argv) != 4:
    print("Usage: python3 client.py server_IP server_port client_udp_port")
    exit(0)

if not sys.argv[2].isdecimal() or not sys.argv[3].isdecimal():
    print("Invalid input, decimal values used.")
    exit(0)

s_ip = sys.argv[1]
s_port = int(sys.argv[2])
c_udp_port = int(sys.argv[3])

# TCP Socket creation
cSocket = socket(AF_INET, SOCK_STREAM)
cSocket.settimeout(10)
cSocket.connect((gethostbyname(gethostname()), s_port))

# Login
u_name = loginCheck(c_udp_port)

# UDP Socket creation (for upload file function)
cSocket2 = socket(AF_INET, SOCK_DGRAM)
cSocket2.bind((gethostbyname(gethostname()), c_udp_port))

# Receive
udpStart = Thread(target = get_file)
udpStart.daemon = True
udpStart.start()


# Command prompt centre
while True:
    command = input("Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, OUT, UPD): ")

    if command.split(" ")[0] == 'BCM':
        broadcast_message(command)

    elif command.split(" ")[0] == 'ATU':
        dload_users(command)

    elif command.split(" ")[0] == 'SRB':
        create_room(command)

    elif command.split(" ")[0] == 'SRM':
        send_room_message(command)

    elif command.split(" ")[0] == 'RDM':
        read_messages(command)

    elif command.split(" ")[0] == 'UPD':
        upload_file(command)

    elif command.split(" ")[0] == 'OUT':
        logout(command)
        break
    
    else:
        print("Invalid command. Please try again.")


cSocket.close()
cSocket2.close()









        

    



