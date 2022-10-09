# Server Side
# PLEASE USE PYTHON3

import sys
from helper import *
import select
import datetime
import time
import os
import json 
from socket import *
from threading import Thread

# Defines
B_SIZE = 2048

# File and list creations
open('userlog.txt', 'w').close()
open('msglog.txt', 'w').close()
credList = {}
online_users = []
messages_sent = []
rooms_created = []



# ////////////////////////////////////////////////////
# ///////////           FUNCTIONS       //////////////
# ////////////////////////////////////////////////////

# Main hub in which it loops through constantly
def trainStation(threaded, addr):
    while True:
        return_console = threaded.recv(2048)
        data = json.loads(return_console.decode())
        command = data["command"]

        if command == 'login':
            clientLogin(data, threaded, addr)
        
        elif command == 'BCM':
            broadcast_msg(data, threaded, addr)

        elif command == 'ATU':
            download_users(data, threaded, addr)

        elif command == 'OUT':
            logout_user(data, threaded, addr)
            break

        elif command == 'UPD':
            upload_file(data, threaded, addr)

        elif command == 'SRB':
            create_room(data, threaded, addr)

        elif command == 'SRM':
            send_room_message(data, threaded, addr)

        elif command == 'RDM':
            read_messages(data, threaded, addr)

    threaded.close()
        

# Client login function
def clientLogin(data, threaded, addr):
    i = 0
    valid = 1
    return_value = '0'   # Set it to 0 for now

    # Loop through the credentials list to find the login
    # Make sure to also have a variable indicating whether the username was found in the database or not (valid = 0 means found!)
    for i in credList.keys():

        # If we find an account
        if i == data["username"]:
            valid = 0

            # If the password is correct to the right account
            if credList[i]["password"] == data["password"]:
                return_value = '1'
                
                # Reset the counter back to 0 as it is a successful login
                credList[i]["invalid"] = 0

                # Update online users and the user log file
                global online_users
                online_users = userLog(data["username"], addr[0], data["port"], online_users)


                print(f"{i} logged in.")
                break

            # If the password is incorrect 
            else:
                credList[i]["invalid"] = credList[i]["invalid"] + 1

                # Login whilst blocked
                if credList[i]["login_time"] != 0 and credList[i]["login_time"] > time.time():
                    print(f"{i} attempted to login but the account was blocked.")
                    return_value = '-2'
                    break
                
                # Too many attempts (blocked)
                elif credList[i]["invalid"] % 5 == 0:
                    print(f"{i} has logged in with the wrong password many times. The account is now blocked for 10 seconds.")
                    credList[i]["login_time"] = time.time() + 10
                    return_value = '-1'
                    break
                    
                # Wrong Password
                else:
                    print(f"{i} attempted to login with the wrong password.")
                    return_value = '0'
                    break


    if valid == 1:
        print('The username is not registered within the database. Please try again.')
        return_value = '-3'
    
    threaded.sendall(return_value.encode())


# Broadcast message function
def broadcast_msg(data, threaded, addr):
    message = data["message"]
    user = data["username"]

    # Log into the file
    global messages_sent
    messages_sent, time, m_no = messageLog(data["username"], data["message"], messages_sent)

    print(user + " broadcasted BCM #" + str(m_no) + " \"" + message + "\"" + " at " + time + ".")

    return_message = "Broadcast message, #" + str(m_no) + " broadcast at " + time + "."
    threaded.sendall(return_message.encode())



# Download active users function
def download_users(data, threaded, addr):
    # return value is empty for now, assuming active users in Miscord
    string_list = ""

    global online_users
    for users in online_users:

        if users["u_name"] == data["username"]:
            continue

        # Print all details of OTHER users
        string_list = string_list + users["u_name"] + ", " + str(users["IP"]) + ", " + str(users["c_port"]) +  ", active since " + users["time_active"] + ".\n"


    # Only person in the server
    if len(online_users) == 1:
        string_list = "empty"

    else:
        # If the request was ATU directly, print out results
        if data["valid"] == "1":
            print("Printing the request of ATU from " + data["username"] + ".\n")
            print(string_list)


 
    threaded.sendall(string_list.encode())


# Log out function
def logout_user(data, threaded, addr):
    u_name = data["username"]

    global online_users
    for users in range(len(online_users)):
        if online_users[users]["u_name"] == u_name:
            break
        
    online_users.remove(online_users[users])

    while users < len(online_users):
        online_users[users]["number"] = online_users[users]["number"] - 1
        users = users + 1
    
    userLogUpdate(online_users)

    return_string = "Thank you for using Miscord! Bye " + data["username"] + "! :)"
    print(data["username"] + " has logged out.")
    threaded.sendall(return_string.encode())


# Upload file function
def upload_file(data, threaded, addr):
    string_return = ""

    for users in online_users:
        if users["u_name"] == data["receiver"]:
            string_return = str(users["IP"]) + " " + str(users["c_port"])

    threaded.sendall(string_return.encode())

# Create room function
def create_room(data, threaded, addr):
    print(data["username"] + " issued SRB command.")

    users_list = data["users"]
    users_list.append(data["username"])

    # Check whether a room already has all the users
    global rooms_created
    for rooms in rooms_created:
        if rooms["users"].sort() == users_list.sort():
            return_string = "invalid " + str(rooms["room_no"])
            threaded.sendall(return_string.encode())
            return

    # Create file and update rooms list
    rooms_created, room_no = SR_ChatLog(users_list, rooms_created)
    return_string = "Seperate chat room has been created, room ID: " + str(room_no) + ", users in this room: " + ", ".join(users_list)

    print(return_string)
    threaded.sendall(return_string.encode())


# Send message in room function
def send_room_message(data, threaded, addr):
    print(data["username"] + " issued SRM command.")
    
    return_string = ""
    valid_room = 0

    # Check if room ID exists
    global rooms_created
    for rooms in range(len(rooms_created)):
        if rooms_created[rooms]["room_no"] == data["room_id"]:
            valid_room = 1
            break
    
    if valid_room == 0:
        print("There is no room ID of the given input.")
        return_string = "-1"
        threaded.sendall(return_string.encode())
        return

    # Check if the user is in that room
    if not data["username"] in rooms_created[rooms]["users"]:
        print(data["username"] + " is not in this room.")
        return_string = "-2"
        threaded.sendall(return_string.encode())
        return

    rooms_created, time, m_no = SR_messageLog(rooms_created, data["room_id"], data["message"], data["username"])

    print(data["username"] + " sent SRM #" + str(m_no) + " \"" + data["message"] + "\"" + " at " + time + ". to Room #" + data["room_id"])

    return_string = data["username"] + " issued a message in seperate room " + data["room_id"] + ": " + "#" + str(m_no) + " sent at time: " + time + "."
    threaded.sendall(return_string.encode())


# Read messages function
def read_messages(data, threaded, addr):
    print(data["username"] + " issued RDM command.")
    return_string = ""
    messages_list = []
    room_number = []

    message_type = data["message_type"]

    # Get time into correct format
    time = " ".join(data["timestamp"])
    given_timestamp = datetime.datetime.strptime(time, '%d %b %Y %H:%M:%S')

    # Broadcasting messages
    if message_type == "b":
        
        # Loop through broadcasting messages
        global messages_sent
        for messages in messages_sent:
            message_timestamp = datetime.datetime.strptime(messages["timestamp"], '%d %b %Y %H:%M:%S')

            if given_timestamp < message_timestamp:
                messages_list.append(messages)
    
    elif message_type == "s":

        # Loop through room messages
        global rooms_created
        for rooms in rooms_created:
            if data["username"] in rooms["users"]:
                for messages in rooms["messages"]:
                    message_timestamp = datetime.datetime.strptime(messages["timestamp"], '%d %b %Y %H:%M:%S')

                    if given_timestamp < message_timestamp:
                        room_number.append(rooms["room_no"])
                        messages_list.append(messages)

    # If there are no messages to be read
    if len(messages_list) == 0:
        return_string = "empty"
        print("No new messages to present.")
        threaded.sendall(return_string.encode())
        return
    
    # If the message type is rooms, then it is printed somewhat differently
    current_room = 0
    if message_type == "s":

        for room_messages in range(len(room_number)):
            if int(room_number[room_messages]) > current_room:
                current_room = int(room_number[room_messages])
                return_string = return_string + "room-" + str(current_room) + ":\n"

            return_string = return_string + "#" + str(messages["message_number"]) + "; " + messages["timestamp"] + "; " + messages["username"] + "; " + messages["message"] + "\n"

    # Otherwise, just print broadcasted messages
    else: 
        for messages in messages_list:
            return_string = return_string + "#" + str(messages["message_number"]) + "; " + messages["timestamp"] + "; " + messages["username"] + "; " + messages["message"] + "\n"
    
    print("Return message")
    print(return_string.strip())
    threaded.sendall(return_string.encode())

# ////////////////////////////////////////////////////
# ///////////           MAIN            //////////////
# ////////////////////////////////////////////////////

# Error testing
if len(sys.argv) != 3:
    print("Usage: python3 server.py server_port number_of_consecutive_failed_attempts")
    exit(0)

f_apt = int(sys.argv[2])
if not sys.argv[2].isdecimal() or f_apt < 1 or f_apt > 5:
    print("Invalid number of allowed failed consecutive attempts. Please enter a number between 1 - 5")
    exit(0)


s_port = int(sys.argv[1])
if not sys.argv[1].isdecimal():
    print("Invalid input, decimal values used.")
    exit(0)

# Socket creation
sSocket = socket(AF_INET, SOCK_STREAM)
sSocket.bind((gethostbyname(gethostname()), s_port))
sSocket.listen(5)

# Get credentials list
credList = credChecker()

# Infinite loop to run all the commands
while True:
    connection, addr = sSocket.accept()
    add = (connection, addr)

    newT = Thread(target = trainStation, args = add)
    newT.daemon = True
    newT.start()

# Close at the end
sSocket.close()







