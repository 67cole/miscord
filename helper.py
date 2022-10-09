import sys
import select
import os
import datetime
from socket import *
from threading import Thread

def credChecker():
    # Check credentials for login status and add it to a dictionary to cross-reference
    temp = {}

    cred = open("credentials.txt", 'r')
    u_data = cred.read().strip()
    u_data = u_data.replace(' ', '\n').split('\n')

    length_data = len(u_data)
    i = 0
    while i in range(length_data):
        if i % 2 == 1:
            temp[u_data[i - 1]] = {'password': u_data[i], 'login_time': 0, 'invalid': 0}

        i = i + 1


    return temp

def userLog(c_user, c_ip, c_port, online_users):
    # Write into the user log
    time = datetime.datetime.now().strftime("%d %b %Y %H:%M:%S")
    num = 1 + len(online_users)

    u_info = {
        "u_name": c_user,
        "number": num,
        "time_active": time,
        "IP": c_ip,
        "c_port": c_port
    }

    online_users.append(u_info)

    u_log = open("userlog.txt", "a")
    u_log.write(str(num) + "; " + time + "; " + c_user + "; " + str(c_ip) + "; " + str(c_port) + '\n')
    u_log.close()

    return online_users

def messageLog(c_user, message, message_list):
    # Write into the message log
    time = datetime.datetime.now().strftime("%d %b %Y %H:%M:%S")
    m_no = len(message_list) + 1

    message_data = {
        "username": c_user,
        "message": message,
        "message_number": m_no,
        "timestamp": time,
    }

    message_list.append(message_data)

    m_log = open("msglog.txt", "a")
    m_log.write(str(m_no) + "; " + time + "; " + c_user + "; " + message + '\n')
    m_log.close()

    return message_list, time, m_no

def SR_ChatLog(users_list, rooms_created):
    # Update rooms list
    room_no = len(rooms_created) + 1
    messages = []

    room_data = {
        "room_no": str(room_no),
        "users": users_list,
        "messages": messages
    }

    rooms_created.append(room_data)

    # Create room message log
    f_name = "SR_" + str(room_no) + "_messagelog.txt"

    room_log = open(f_name, 'w')
    room_log.close()

    return rooms_created, room_no

def SR_messageLog(rooms_created, id, message, username):
    time = datetime.datetime.now().strftime("%d %b %Y %H:%M:%S")

    # Find room
    for rooms in range(len(rooms_created)):
        if rooms_created[rooms]["room_no"] == id:
            break

    m_no = len(rooms_created[rooms]["messages"]) + 1

    message_data = {
        "username": username,
        "message": message,
        "message_number": m_no,
        "timestamp": time,
    }

    rooms_created[rooms]["messages"].append(message_data)
    f_name = "SR_" + id + "_messagelog.txt"

    m_log = open(f_name, "a")
    m_log.write(str(m_no) + "; " + time + "; " + username + "; " + message + '\n')
    m_log.close()

    return rooms_created, time, m_no

def userLogUpdate(online_users):
    u_log = open("userlog.txt", "w")
    
    for users in range(len(online_users)):
        u_log.write(str(online_users[users]["number"]) + "; " + online_users[users]["time_active"] + "; " + online_users[users]["u_name"] + "; " + str(online_users[users]["IP"]) + "; " + str(online_users[users]["c_port"]) + '\n')
    
    u_log.close()

