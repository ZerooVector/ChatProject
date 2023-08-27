import socket
import threading
#import pandas as pd # permanently act as an online database
#import numpy as np
import time 
import sqlite3
import datetime as dt 
import os 

DB_PATH = "./serverLogic/server.db"
FILE_PATH = "./serverLogic/filefolder/"

current_online = []





# global thread functions 
def message_update_detector(params): # detector the message to someone
    global users_data

    # users_data = pd.read_csv("users.csv")
    # messages_data = pd.read_csv("messages.csv")

    key_list = list(users_data["key"]) # read all of the key 

    for person in key_list:
        person_message = messages_data[messages_data["to"] == person]
        person_message_len = len(person_message)
        message_count_in_DB = len(users_data[users_data["key"] == person]["notice"])
        
        if person_message_len != message_count_in_DB :  # update triggered 
            users_data.loc[users_data["key"] == person, "notice"] = person_message_len
            users_data.loc[users_data["key"] == person, "notice_flag"] = 1 # raise the flag 

    users_data.to_csv("users.csv", index=False)
    time.sleep(0.1) # sleep 



# local thread functions 
def send_msg(sock, msg):
    # 将消息编码为字节流
    msg = msg.encode('utf-8')
    # 创建固定长度的消息头，例如4个字节，包含消息长度
    msg_header = f"{len(msg):<4}".encode('utf-8')
    # 发送消息头和消息主体
    sock.sendall(msg_header + msg)


def recv_msg_unblock(sock):

    sock.setblocking(False)
    try:
        msg_header = sock.recv(4).decode('utf-8').strip()
        
        if not msg_header:
            print("Connection closed by the server")
            return None

        msg_len = int(msg_header)
        return sock.recv(msg_len).decode('utf-8')

    except BlockingIOError:
        # 这里处理套接字当前不可用的情况
        # print("No data available yet.")
        return None

def recv_msg(sock):
    sock.setblocking(True)
    msg_header = sock.recv(4).decode('utf-8').strip()
        
    if not msg_header:
        print("Connection closed by the server")
        return None

    msg_len = int(msg_header)
    return sock.recv(msg_len).decode('utf-8')


def send_file(sock, file_chunk):
    # 发送文件块大小
    header = f"{len(file_chunk):<4}"
    sock.sendall(header.encode('utf-8'))

    # 发送文件块
    sock.sendall(file_chunk)

def recv_file(sock):
    try:
        # 设置套接字超时为10秒
        sock.settimeout(0.1)

        # 接收文件块大小
        header = sock.recv(4).decode('utf-8').strip()
        chunk_size = int(header)
        
        # 循环接收文件块直到达到期望的大小
        chunks = []
        bytes_received = 0
        while bytes_received < chunk_size:
            chunk = sock.recv(min(chunk_size - bytes_received, 4096))
            if not chunk:
                # Connection closed before receiving expected data
                raise Exception("Connection closed before receiving full data.")
            chunks.append(chunk)
            bytes_received += len(chunk)

        data = b''.join(chunks)

        # 重置套接字为阻塞模式（如果需要）
        sock.setblocking(True)

        return data

    except socket.timeout:
        print("Socket timed out while receiving data.")
        return None
    except Exception as e:
        print(f"Error while receiving data: {e}")
        return None


def signup(cursor,sock,data,db_conn):
    data = data.split("||-||")
    # print(data)
    input_id = data[0]
    input_nickname = data[1]
    input_password = data[2]
    cmd = '''
    SELECT id FROM user
    WHERE id = ?
    '''
    cursor.execute(cmd,(input_id,))
    result = cursor.fetchall()  # get all of the result 
    if len(result) > 0:
        send_msg(sock,"L00+ERROR")
        send_msg(sock,"There is a user with same ID!")
    else: # ok
        cmd = '''
        INSERT INTO user (id,nickname,password,status)
        VALUES (?,?,?,?)
        '''
        cursor.execute(cmd,(input_id,input_nickname,input_password,"offline",))
        db_conn.commit()
        send_msg(sock,"L00+SUCCESS")
        send_msg(sock,"Successfully Sign Up!")



def login(cursor,sock,data,db_conn):
    data = data.split("||-||")
    input_id = data[0] 
    input_password = data[1] 
    cmd = '''
    SELECT password FROM user
    WHERE id = ?
    '''
    cursor.execute(cmd,(input_id,))
    result = cursor.fetchall() 
    if len(result) == 0:
        # send_msg(sock,"L01+ERROR")
        send_msg(sock,"ID not exist!")
        return 0
    correct_password = result[0][0]
    if correct_password != input_password:
        send_msg(sock,"Password Wrong!")
        # send_msg(sock,"Password Incorrect!")
        return 0
    else :
        
        cmd = '''
        UPDATE user 
        SET status = ?
        WHERE id = ?
        '''
        cursor.execute(cmd,("online",input_id,))
        db_conn.commit()
        send_msg(sock,"L01+SUCCESS")
        # send_msg(sock,"Successfully Login!")
        return input_id
        


def searchuser(cursor,sock,data):
    search_request = data 
    pattern = "%" + search_request + "%"
    cmd = '''
    SELECT * 
    FROM user 
    WHERE nickname LIKE ?
    '''
    cursor.execute(cmd,(pattern,))
    rows = cursor.fetchall() 
    if len(rows) == 0 :
        send_msg(sock,"F00+ERROR")
        send_msg(sock,"Cannot match any user!")
    else :
        str_msg = str(rows)
        send_msg(sock,"F00+SUCCESS")
        send_msg(sock,str_msg)



def addfriendrequest(cursor,sock,data,userid,db_conn):
    add_request = data 
    cmd = '''
    SELECT id
    FROM user
    WHERE id = ?
    '''
    cursor.execute(cmd,(add_request,))
    rows = cursor.fetchall() 
    if len(rows) == 0:
        send_msg(sock,"F01+ERROR")
        send_msg(sock,"Cannot find this user!")
    else :
        cmd = '''
        SELECT *
        FROM friendrelation
        WHERE user1 = ? AND user2 = ?
        '''
        cursor.execute(cmd,(userid,add_request,))
        rows = cursor.fetchall() 
        if len(rows) > 0:
            send_msg(sock,"F01+ERROR")
            send_msg(sock,"You have added this user!")
        else :
            if add_request == userid:
                send_msg(sock,"F01+ERROR")
                send_msg(sock,"You cannot add yourself!")
            else :
                ct = dt.datetime.now()
                cmd = '''
                INSERT INTO message(initial,via,terminal,type,unreadflag,datetime,content)
                VALUES(?,?,?,?,?,?,?)
                '''
                cursor.execute(cmd,(userid,"none",add_request,"friendrq","activate",ct,"friendrq"))
                db_conn.commit() 
                send_msg(sock,"F01+SUCCESS")
                send_msg(sock,"Please wait another user to check 5your request!")


def getpreviousrequest_(cursor,sock,userid):
    current_time = dt.datetime.now()
    current_time = str(current_time)
    cmd = '''
    SELECT initial,unreadflag FROM message
    WHERE 
    via = ?
    AND type = ?
    AND datetime < ?
    AND terminal = ?
    '''
    cursor.execute(cmd,("none","friendrq",current_time,userid))
    rows = cursor.fetchall()
    return rows 


def getpreviousrequest(cursor,sock,userid,):
    # source = data 
    rows = getpreviousrequest_(cursor,sock,userid)
    rows = str(rows)
    if len(rows) == 0:
        send_msg(sock,"F03+ERROR")
        send_msg(sock,"You have not recieved request!")
    else :
        send_msg(sock,"F03+SUCCESS")
        send_msg(sock,rows)
    

def getunreadrequest_(cursor,sock,userid):
    cmd = '''
    SELECT initial,unreadflag FROM message
    WHERE 
    via = ?
    AND type = ?
    AND terminal = ?
    AND unreadflag = ?
    '''
    cursor.execute(cmd,("none","friendrq",userid,"activate"))
    rows = cursor.fetchall()
    return rows 


def getunreadrequest(cursor,sock,userid,):
    rows = getunreadrequest_(cursor,sock,userid,)
    # rows = str(rows)
    if len(rows) == 0:
        send_msg(sock,"F04+ERROR")
        send_msg(sock,"You have checked all of the request!")
    else :
        send_msg(sock,"F04+SUCCESS")
        send_msg(sock,str(rows))

def dealwithrequest(cursor,sock,data,userid,db_conn):
    data = data.split("||-||")
    source = data[0]
    reply = data[1] 
    cmd = '''
    SELECT * FROM message 
    WHERE initial = ?
    AND via = ?
    AND terminal = ?
    AND type = ?
    AND unreadflag = ?
    '''
    cursor.execute(cmd,(source,"none",userid,"friendrq","activate"))
    rows = cursor.fetchall() 
    if len(rows) == 0:
        send_msg(sock,"F05+ERROR")
        send_msg(sock,"Request Do not exists!")
        return 
    if reply == "Y" or reply == "y":
        cmd = '''
        UPDATE message 
        SET unreadflag = ?
        WHERE initial = ?
        AND via = ?
        AND terminal = ?
        AND type = ?
        AND unreadflag = ?
        '''
        cursor.execute(cmd,("accept",source,"none",userid,"friendrq","activate"))
        db_conn.commit()

        cmd = '''
        INSERT INTO friendrelation(user1,user2)
        VALUES(?,?)
        '''
        cursor.execute(cmd,(source,userid))
        db_conn.commit()
        cursor.execute(cmd,(userid,source))
        db_conn.commit() 
        send_msg(sock,"F05+SUCCESS")
        send_msg(sock,"You accept another user's request!")
    else :
        cmd = '''
        UPDATE message 
        SET unreadflag = ?
        WHERE initial = ?
        AND via = ?
        AND terminal = ?
        AND type = ?
        AND unreadflag = ?
        '''
        cursor.execute(cmd,("refuse",source,"none",userid,"friendrq","activate"))
        db_conn.commit()
        send_msg(sock,"F05+SUCCESS")
        send_msg(sock,"You refuse another user's request!")
    


def getfriendslist_(cursor,sock,userid):
    cmd = '''
    SELECT user2 FROM friendrelation
    WHERE user1 = ?
    '''
    cursor.execute(cmd,(userid,))
    rows = cursor.fetchall() 
    res = [] 
    for row in rows:
        res.append(row[0])
    return res 

def getfriendslist(cursor,sock,userid):
    
    rows = getfriendslist_(cursor,sock,userid)
    if len(rows) == 0:
        send_msg(sock,"F02+ERROR")
        send_msg(sock,"You have not added any friend!")
    else :
        str_msg = str(rows)
        send_msg(sock,"F02+SUCCESS")
        send_msg(sock,str_msg)


def creategroup(cursor,sock,data,userid,db_conn): # G00;test;[A00,A01]
    data = data.split("||-||")
    input_id = data[0] # unique group id 
    input_name = data[1] # group name 
    members = data[2].strip("[]").split(",")
    members.append(userid)
    # count = len(members)
    cmd = '''
    SELECT id FROM usergroup 
    WHERE id = ?
    '''
    cursor.execute(cmd,(input_id,))
    rows = cursor.fetchall() 
    if len(rows) > 0:
        send_msg(sock,"G00+ERROR")
        send_msg(sock,"Duplicate Group id!")
    else :
        friend = getfriendslist_(cursor,sock,userid)
        friend.append(userid)
        if set(members).issubset(set(friend)) == 0 :
            send_msg(sock,"G00+ERROR")
            send_msg(sock,"Some users are not your friend!")
        else :
            cmd = '''
            INSERT INTO usergroup(id,name,master)
            VALUES(?,?,?)
            '''
            cursor.execute(cmd,(input_id,input_name,userid,))
            db_conn.commit()
            cmd = '''
            INSERT INTO grouprelation(groupid,userid)
            VALUES(?,?)
            ''' 
            for item in members:
                cursor.execute(cmd,(input_id,item,))
                db_conn.commit()
            cmd = '''
            INSERT INTO groupmanager(groupid,userid)
            VALUES(?,?)
            '''
            cursor.execute(cmd,(input_id,userid))
            db_conn.commit()

            send_msg(sock,"G00+SUCCESS")
            send_msg(sock,"Successfully Create a Group!")

def askgroup_(cursor,sock,userid):
    cmd = '''
    SELECT groupid FROM grouprelation
    WHERE userid = ?
    '''
    cursor.execute(cmd,(userid,))
    rows = cursor.fetchall() 
    res = []
    for row in rows :
        res.append(row[0])
    return res


def askgroup(cursor,sock,userid):
    # userid = data 
    rows = askgroup_(cursor,sock,userid)
    if len(rows) == 0:
        send_msg(sock,"G01+ERROR")
        send_msg(sock,"You have not add any group!")
    else :
        send_msg(sock,"G01+SUCCESS")
        str_msg = str(rows)
        send_msg(sock,str_msg)


def sendmessage(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    target = data[0] 
    content = data[1] 
    cmd = '''
    SELECT * FROM friendrelation
    WHERE user1 = ? AND user2 = ?
    '''
    cursor.execute(cmd,(userid,target,))
    rows = cursor.fetchall() 
    if len(rows) == 0:
        send_msg(sock,"C00+ERROR")
        send_msg(sock,"This user isn't your friend!")
    else :
        current_time = dt.datetime.now()
        current_time = str(current_time)
        cmd = '''
        INSERT INTO message(initial,via,terminal,type,unreadflag,datetime,content)
        VALUES (?,?,?,?,?,?,?)
        '''
        cursor.execute(cmd,(userid,"none",target,"chat","activate",current_time,content))
        db_conn.commit()
        send_msg(sock,"C00+SUCCESS")



def getpreviousmessage_(cursor,sock,userid,source,db_conn,clear = 1):
    current_time = dt.datetime.now()
    current_time = str(current_time)
    cmd = '''
    SELECT content FROM message
    WHERE 
    via = ?
    AND type = ?
    AND datetime < ?
    AND initial = ?
    AND terminal = ?
    '''
    cursor.execute(cmd,("none","chat",current_time,source,userid))
    rows = cursor.fetchall()
    if clear == 1 :  # clear unread flag
        cmd = '''
        UPDATE message 
        SET unreadflag = ?
        WHERE 
        via = ?
        AND type = ?
        AND datetime < ?
        AND initial = ?
        AND terminal = ?
        '''
        cursor.execute(cmd,("release","none","chat",current_time,source,userid))
    db_conn.commit()
    res = [] 
    for row in rows:
        res.append(row[0])
    return res 



def getpreviousmessage(cursor,sock,userid,data,db_conn,N = 1000):
    source = data 
    rows = getpreviousmessage_(cursor,sock,userid,source,db_conn,clear = 1)
    rows = rows[-N:]
    # rows = str(rows)
    if len(rows) == 0 :
        send_msg(sock,"C01+ERROR")
        send_msg(sock,"No chat History!")
    else :
        rows = str(rows)
        send_msg(sock,"C01+SUCCESS")
        send_msg(sock,str(rows) )



def getnewmessage_(cursor,sock,userid,source,db_conn):
    cmd = '''
    SELECT content FROM message
    WHERE
    via = ?
    AND type = ?
    AND unreadflag = ?
    AND initial = ?
    AND terminal = ?
    '''
    cursor.execute(cmd,("none","chat","activate",source,userid))
    rows = cursor.fetchall()
    cmd =  '''
    UPDATE  message
    SET unreadflag = ?
    WHERE
    via = ?
    AND type = ?
    AND unreadflag = ?
    AND initial = ?
    AND terminal = ?
    '''
    cursor.execute(cmd,("release","none","chat","activate",source,userid))  # release the flag
    db_conn.commit()
    res = [] 
    for row in rows:
        res.append(row[0])
    return res 


def getnewmessage(cursor,sock,userid,data,db_conn):
    source = data 
    rows = getnewmessage_(cursor,sock,userid,source,db_conn)
    if len(rows) == 0 :
        send_msg(sock,"C02+ERROR")
        send_msg(sock,"No new message!")
    else :
        rows = str(rows)
        send_msg(sock,"C02+SUCCESS")
        send_msg(sock,str(rows))


def getgroupmember_(cursor,sock,groupid):
    cmd = '''
    SELECT userid FROM grouprelation
    WHERE groupid = ?
    '''
    cursor.execute(cmd,(groupid,))
    rows = cursor.fetchall() 
    res = []
    for row in rows :
        res.append(row[0])
    return res 

def getgroupmember(cursor,sock,data):
    groupid = data
    res = getgroupmember_(cursor,sock,groupid)
    if len(res) == 0:
        send_msg(sock,"G02+ERROR")
        send_msg(sock,"Group not exist or group without members!")
    else :
        send_msg(sock,"G02+SUCCESS")
        send_msg(sock,res)
    

def setgroupmanager(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    target = data[0] 
    memlist = data[1].strip("[]").split(",")
    cmd = '''
    SELECT master FROM usergroup 
    WHERE groupid = ? 
    '''
    cursor.execute(cmd,(target,))
    res = cursor.fetchall()[0][0] 
    if res != userid:
        send_msg(sock,"G03+ERROR")
        send_msg(sock,"You cannot modifiy group info!")
        return 
    
    cmd = '''
    INSERT INTO groupmanager
    VALUES (?,?)
    '''
    for item in memlist:
        cursor.execute(cmd,(target,item,))
        db_conn.commit() 
    send_msg(sock,"G03+SUCCESS")
    send_msg(sock,"Modify Groupinfo Success!")


def getgroupmanager_(cursor,sock,group):
    cmd = '''
    SELECT userid FROM groupmanager
    WHERE groupid = ?
    '''
    cursor.execute(cmd,(group,))
    res = [] 
    rows = cursor.fetchall() 
    for row in rows :
        res.append(row[0])
    return res 


def addgrouprequest(cursor,sock,userid,data,db_conn):
    rq = data 
    cmd = '''
    SELECT * FROM usergroup 
    WHERE groupid = ?
    '''
    cursor.execute(cmd,(rq,))
    rows = cursor.fetchall() 
    if len(rows) == 0 :
        send_msg(sock,"G04+ERROR")
        send_msg(sock,"Cannot find this group!")
        return 
    cmd = '''
    INSERT INTO message(initial,via,terminal,type,datetime,unreadflag)
    VALUES(?,?,?,?,?,?)
    '''
    ct = dt.datetime.now() 
    manager = getgroupmanager_(cursor,sock,rq)
    for person in manager:
        cursor.execute(ct,(userid,rq,person,"grouprq",ct,"activate"))
        db_conn.commit() 
    send_msg(sock,"G04+SUCCESS")
    send_msg(sock,"Successfully Send Request!")


def inversegetmanager_(cursor,sock,userid): # buguan
    cmd = '''
    SELECT groupid FROM groupmanager
    WHERE userid = ?
    '''
    cursor.execute(cmd,(userid,))
    rows = cursor.fetchall() 
    res = [] 
    for row in rows :
        res.append(row[0])
    return res 


def getpreviousgrouprequest_(cursor,sock,userid):
    manage_group = inversegetmanager_(cursor,sock,userid)
    if len(manage_group) == 0:
        send_msg(sock,"G05+ERROR")
        send_msg(sock,"You are not the manager of a group!")
        return 
    ct = dt.datetime.now()
    cmd = '''
    SELECT initial,via,status FROM message
    WHERE via = ?
    AND terminal = ?
    AND datetime < ?
    AND type = ?
    '''
    res = [] 
    for g in  manage_group:
        cursor.execute(cmd,(g,userid,ct,"grouprq"))
        rows = cursor.fetchall()
        for row in rows:
            res.append(row)
    return res 

def getunreadgrouprequest_(cursor,sock,userid):
    manage_group = inversegetmanager_(cursor,sock,userid)
    if len(manage_group) == 0:
        send_msg(sock,"G05+ERROR")
        send_msg(sock,"You are not the manager of a group!")
        return 
    ct = dt.datetime.now()
    cmd = '''
    SELECT initial,via FROM message
    WHERE via = ?
    AND terminal = ?
    AND datetime < ?
    AND type = ?
    AND unreadflag = ?
    '''
    res = [] 
    for g in  manage_group:
        cursor.execute(cmd,(g,userid,dt,"grouprq","activate"))
        rows = cursor.fetchall()
        for row in rows:
            res.append(row)
    return res 


def dealwithgrouprequest(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    group = data[1] 
    user = data[0] 
    respose = data[2]
    cmd = '''
    SELECT * FROM message
    WHERE initial = ?
    AND via = ?
    AND terminal = ?
    AND type = ?
    AND unreadflag = ?
    '''
    cursor.execute(cmd,(user,group,userid,"grouprq","activate",))
    rows = cursor.fetchall() 
    if len(rows) == 0:
        send_msg(sock,"G06+ERROR")
        send_msg(sock,"Cannot find this request!")
        return 
    manager = getgroupmanager_(cursor,sock,group)
    if userid not in manager:
        send_msg(sock,"G06+ERROR")
        send_msg(sock,"You are not the manager of the group!")
    if respose =="Y" or respose == "y":
        cmd = '''
        UPDATE message 
        SET unreadflag = ? 
        WHERE initial = ?
        AND via = ?
        AND type = ?
        AND unreadflag = ?
        '''
        cursor.execute(cmd,("accept",user,group,"groupeq","activate"))
        db_conn.commit() 
        cmd = '''
        INSERT INTO grouprelation(groupid,userid)
        VALUES(?,?)
        '''
        cursor.execute(cmd,(group,user))
        db_conn.commit()
        send_msg(sock,"G06+SUCCESS")
        send_msg(sock,"You accept a user's request!")
    else :
        cmd = '''
        UPDATE message 
        SET unreadflag = ? 
        WHERE initial = ?
        AND via = ?
        AND type = ?
        AND unreadflag = ?
        '''
        cursor.execute(cmd,("refuse",user,group,"groupeq","activate"))
        db_conn.commit()
        send_msg(sock,"G06+SUCCESS")
        send_msg(sock,"You refuse a user's request!") 



def manageradduser(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    group = data[0] 
    user = data[1] 
    cmd = '''
    SELECT * FROM user
    WHERE userid = ?
    '''
    cursor.execute(cmd,(user,))
    res = cursor.fetchall() 
    if len(res) == 0:
        send_msg(sock,"G07+ERROR")
        send_msg(sock,"User Not Exist!")
        return 
    
    cmd = '''
    SELECT * FROM usergroup 
    WHERE groupid = ?
    '''
    cursor.execute(cmd,(group,))
    res = cursor.fetchall() 
    if len(res) == 0:
        send_msg(sock,"G07+ERROR")
        send_msg(sock,"Group Not Exist!")
        return 
    
    manager = getgroupmanager_(cursor,sock,group)
    if userid not in manager:
        send_msg(sock,"G07+ERROR")
        send_msg(sock,"You are not a manager of the group!")
        return 
    cmd = '''
    INSERT INTO grouprelation(groupid,userid)
    VALUES(?,?)
    '''
    cursor.execute(cmd,(group,user))
    db_conn.commit() 
    send_msg(sock,"G07+SUCCESS")
    send_msg(sock,"You pulled a user into the group!")



def managerremoveuser(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    group = data[0] 
    user = data[1] 
    cmd = '''
    SELECT * FROM usergroup
    WHERE group = ?
    '''
    cursor.execute(cmd,(group,))
    rows = cursor.fetchall() 
    if len(rows) == 0:
        send_msg(sock,"G08+ERROR")
        send_msg(sock,"Group not Exist!")
        return 
    
    mem = getgroupmember_(group)
    if user not in mem:
        send_msg(sock,"G08+ERROR")
        send_msg(sock,"User not in the group!")
        return 
    
    manager = getgroupmanager_(cursor,sock,group)
    if userid not in manager:
        send_msg(sock,"G08+ERROR")
        send_msg(sock,"You are not a manager of the group!")
        return 
    cmd = '''
    DELETE FROM grouprelation
    WHERE groupid = ? AND userid = ?
    '''
    cursor.execute(cmd,(group,user))
    db_conn.commit() 
    send_msg(sock,"G08+SUCCESS")
    send_msg(sock,"You removed a user into the group!")
    
    

def sendgroupmessage(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    target = data[0]
    content = data[1] 
    added_groups = askgroup_(cursor,sock,userid)
    if target not in added_groups:
        send_msg(sock,"C03+ERROR")
        send_msg(sock,"You have not add this group!")
    else :
        members = getgroupmember_(cursor,sock,target)
        if len(members) == 0 :
            send_msg(sock,"C03+ERROR")
            send_msg(sock,"No members in the group!")
        else :
            current_time = dt.datetime.now()
            current_time = str(current_time)
            cmd = '''
            INSERT INTO message(initial,via,terminal,type,unreadflag,datetime,content)
            VALUES(?,?,?,?,?,?,?)
            '''
            for person in members:
                cursor.execute(cmd,(userid,target,person,"chat","activate",current_time,content))
                db_conn.commit()
            send_msg(sock,"C03+SUCCESS")

    
def getgrouppreviousmessage_(cursor,sock,userid,groupid,db_conn,clear = 1):
    current_time = dt.datetime.now()
    current_time = str(current_time)
    cmd = '''
    SELECT initial,content FROM message
    WHERE 
    via = ?
    AND type = ?
    AND datetime < ?
    AND terminal = ?
    '''
    cursor.execute(cmd,(groupid,"chat",current_time,userid))
    rows = cursor.fetchall()
    if clear == 1 :  # clear unread flag
        cmd = '''
        UPDATE message 
        SET unreadflag = ?
        WHERE 
        via = ?
        AND type = ?
        AND datetime < ?
        AND terminal = ?
        '''
        cursor.execute(cmd,("release",groupid,"chat",current_time,userid))
        db_conn.commit()
    # res = [] 
    # for row in rows:
    #     res.append(row[0])
    return rows

def getgrouppreviousmessage(cursor,sock,userid,data,db_conn,N = 1000):
    groupid = data 
    rows = getgrouppreviousmessage_(cursor,sock,userid,groupid,db_conn)
    rows = rows[-N:]
    if len(rows) == 0 :
        send_msg(sock,"C04+ERROR")
        send_msg(sock,"No chat History!")
    else :
        rows = str(rows)
        send_msg(sock,"C04+SUCCESS")
        send_msg(sock,rows)
        

def getgroupnewmessage_(cursor,sock,userid,source,db_conn):
    cmd = '''
    SELECT initial, content FROM message
    WHERE
    via = ?
    AND type = ?
    AND unreadflag = ?
    AND terminal = ?
    '''
    cursor.execute(cmd,(source,"chat","activate",userid))
    rows = cursor.fetchall()
    cmd =  '''
    UPDATE  message
    SET unreadflag = ?
    WHERE
    via = ?
    AND type = ?
    AND unreadflag = ?
    AND terminal = ?
    '''
    cursor.execute(cmd,("release",source,"chat","activate",userid))  # release the flag
    db_conn.commit()
    # res = [] 
    # for row in rows:
    #     res.append(row[0])
    return rows 



def getgroupnewmessage(cursor,sock,userid,data,db_conn):
    groupid = data 
    rows = getgroupnewmessage_(cursor,sock,userid,groupid,db_conn)
    if len(rows) == 0 :
        send_msg(sock,"C05+ERROR")
        send_msg(sock,"No new message!")
    else :
        rows = str(rows)
        send_msg(sock,"C05+SUCCESS")
        send_msg(sock,rows)



def getfilecount_(cursor): #buguan
    cmd = '''
    SELECT * FROM file
    '''
    cursor.execute(cmd)
    rows = cursor.fetchall() 
    return len(rows)


def serverrecievefile(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    target = data[0] 
    address = data[1]
    originname = os.path.basename(address)
    savename = str(getfilecount_(cursor)) +"-" + originname 
    savepath = FILE_PATH + savename
    friend = getfriendslist_(cursor,sock,userid)
    if target not in friend:
        while True :
            file_chunk = recv_file(sock)  # recieve a chunk
            if not file_chunk:
                break
            # file.write(file_chunk)
        file_chunk = ""
        send_msg(sock,"T02+ERROR")
        send_msg(sock,"This user is not your friend!")
        return 
    # else :
        # send_msg(sock,"T01+CONTINUE")
    # cnt = 0 
    with open(savepath,"wb") as file :
        while True :
            file_chunk = recv_file(sock)  # recieve a chunk
            if not file_chunk:
                break
            file.write(file_chunk)
            print("recieving...")

    cmd = '''
    INSERT INTO file(originalname,storagename,initial,via,terminal,type,status,datetime)
    VALUES(?,?,?,?,?,?,?,?)
    '''
    current_time = dt.datetime.now() 
    current_time = str(current_time)
    cursor.execute(cmd,(originname,savename,userid,"none",target,"chatfile","activate",current_time))
    db_conn.commit()
    send_msg(sock,"T02+SUCCESS")
    # send_msg(sock,"No new message!")


def getallfile_(cursor,userid,):
    cmd = '''
    SELECT storagename FROM file 
    WHERE via = ?
    AND terminal = ?
    '''
    cursor.execute(cmd,("none",userid,))
    rows = cursor.fetchall() 
    res = [] 
    for row in rows:
        res.append(row[0])
    return res 


def serversendfile(cursor,sock,userid,data,db_conn):
    strname = data 
    all_file = getallfile_(cursor,userid)
    if strname not in all_file:
        send_msg(sock,"T03+ERROR")
        send_msg(sock,"You cannot recieve this file!")
    else :
        savepath = FILE_PATH +  strname 
        if not os.path.exists(savepath):
            send_msg(sock,"T03+ERROR")
            send_msg(sock,"File not Exist!")
            print(f"File {savepath} does not exist!")  # client checks the file is or not exist 
            return
    # pause_event.clear()
        cmd ='''
        SELECT originalname FROM file 
        WHERE storagename = ?
        '''
        cursor.execute(cmd,(strname,))
        rows = cursor.fetchall() 
        res = rows[0][0] 
        msg_to_send = "T03+"+res
        send_msg(sock,msg_to_send)

        with open(savepath,"rb") as file :
    
            file_chunk = file.read(4096*2)
            while file_chunk:
                send_file(sock,file_chunk)
                file_chunk = file.read(4096*2) 
                print("sending...")
        time.sleep(0.15)
        send_msg(sock,"T03+SUCCESS")
        send_msg(sock,"Successfully Send the file!")



def getpreviousfile_(cursor,sock,userid,source,db_conn,clear = 1):
    ct = dt.datetime.now()
    ct = str(ct)
    cmd = '''
    SELECT originalname, storagename FROM file
    WHERE initial = ?
    AND via = ?
    AND terminal = ?
    AND type = ?
    AND datetime < ?
    '''
    cursor.execute(cmd,(source,"none",userid,"chatfile",ct))
    rows = cursor.fetchall() 
    if clear == 1:
        cmd = '''
        UPDATE file SET status = ?
        WHERE initial = ?
        AND via = ?
        AND terminal = ?
        AND type = ?
        AND status = ?
        '''
        cursor.execute(cmd,("release",source,"none",userid,"chatfile","activate"))
        db_conn.commit()
    return rows 



def getpreviousfile(cursor,sock,userid,data,db_conn):
    source = data
    rows = getpreviousfile_(cursor,sock,userid,source,db_conn)
    if len(rows) == 0:
        send_msg(sock,"T00+ERROR")
        send_msg(sock,"Cannot find previous files!")
    else :
        send_msg(sock,"T00+SUCCESS")
        send_msg(sock,str(rows))

    

def getnewfile_(cursor,sock,userid,source,db_conn):
    cmd = '''
    SELECT originalname,storagename
    FROM file 
    WHERE initial = ?
    AND via = ?
    AND terminal = ?
    AND type = ?
    AND status = ?
    '''
    cursor.execute(cmd,(source,"none",userid,"chatfile","activate"))
    rows = cursor.fetchall() 
    cmd = '''
    UPDATE file SET status = ? 
    WHERE initial = ?
    AND via = ?
    AND terminal = ?
    AND type = ?
    AND status = ?
    '''
    cursor.execute(cmd,("release",source,"none",userid,"chatfile","activate"))
    db_conn.commit() 
    return rows 



def getnewfile(cursor,sock,userid,data,db_conn):
    source = data
    rows = getnewfile_(cursor,sock,userid,source,db_conn)
    if len(rows) == 0:
        send_msg(sock,"T01+ERROR")
        send_msg(sock,"Cannot find previous files!")
    else :
        send_msg(sock,"T01+SUCCESS")
        send_msg(sock,str(rows))



def serverrecievegroupfile_(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    target = data[0] 
    address = data[1]
    originname = os.path.basename(address)
    savename = str(getfilecount_(cursor)) +"-" + originname 
    savepath = FILE_PATH + savename
    # friend = getfriendslist_(cursor,sock,userid)
    added_groups = askgroup_(userid)
    if target not in added_groups:
        send_msg(sock,"T04+ERROR")
        send_msg(sock,"You have not add this group!")
        while True :
            file_chunk = recv_file(sock)  # recieve a chunk
            if not file_chunk:
                break
    else :
        members = getgroupmember_(target)
        if len(members) == 0 :
            send_msg(sock,"T04+ERROR")
            send_msg(sock,"No members in the group!")
            while True :
                file_chunk = recv_file(sock)  # recieve a chunk
                if not file_chunk:
                    break
        
        else :
            with open(savepath,"wb") as file :
                while True :
                    file_chunk = recv_file(sock)  # recieve a chunk
                    if not file_chunk:
                        break
                    file.write(file_chunk)
                    print("recieving...")

            current_time = dt.datetime.now()
            current_time = str(current_time)
            cmd = '''
            INSERT INTO file(initial,via,terminal,type,status,datetime,originalname,storagename)
            VALUES(?,?,?,?,?,?,?)
            '''
            for person in members:
                cursor.execute(cmd,(userid,target,person,"groupfile","activate",current_time,originname,savename))
                db_conn.commit()
            send_msg(sock,"T04+SUCCESS")
    # else :
        # send_msg(sock,"T01+CONTINUE")
    # cnt = 0 
    


def getpreiviousgroupfile_(cursor,sock,userid,source,db_conn,clear = 1):
    ct = dt.datetime.now()
    ct = str(ct)
    cmd = '''
    SELECT originalname, storagename FROM file
    WHERE via = ?
    AND terminal = ?
    AND type = ?
    AND datetime < ?
    '''
    cursor.execute(cmd,(source,userid,"groupfile",ct))
    rows = cursor.fetchall() 
    if clear == 1:
        cmd = '''
        UPDATE file SET status = ?
        WHERE 
        via = ?
        AND terminal = ?
        AND type = ?
        AND status = ?
        '''
        cursor.execute(cmd,("release",source,userid,"groupfile","activate"))
        db_conn.commit()
    return rows 



def getnewgroupfile_(cursor,sock,userid,source,db_conn,clear = 1):
    cmd = '''
    SELECT originalname,storagename
    FROM flie 
    WHERE 
    via = ?
    AND terminal = ?
    AND type = ?
    AND status = ?
    '''
    cursor.execute(cmd,(source,userid,"groupfile","activate"))
    rows = cursor.fetcgall() 
    cmd = '''
    UPDATE file SET status = ? 
    WHERE 
    via = ?
    AND terminal = ?
    AND type = ?
    AND status = ?
    '''
    cursor.execute(cmd,("release",source,userid,"groupfile","activate"))
    db_conn.commit() 
    return rows 



def handle_client(client_sock): # callback function, all functions of our app should start from here 
    
    user_id = None
    print("Start a new thread!")

    global current_online
    
    
    # info_dict = {"user_key":user_key,"client_sock":client_sock}
    # current_online.append(info_dict)

    db_conn = sqlite3.connect(DB_PATH,timeout = 20)
    
    cursor = db_conn.cursor()
    # cursor.execute("PRAGMA journal_mode=WAL")

    

    while True:
        data = recv_msg(client_sock)
        print(data)

        flag_bits = data[0:4]
        data = data[4:]
        


        if flag_bits == "L00+": #signup 
            signup(cursor,client_sock,data,db_conn)

        elif flag_bits == "L01+": #login
            user_id = login(cursor,client_sock,data,db_conn)

        if user_id is not None :
            if flag_bits == "F00+":
                searchuser(cursor,client_sock,data)

            if flag_bits == "F01+":
                addfriendrequest(cursor,client_sock,data,user_id,db_conn)

            if flag_bits == "F02+":
                getfriendslist(cursor,client_sock,user_id)

            if flag_bits == "F03+":
                getpreviousrequest(cursor,client_sock,user_id)

            if flag_bits == "F04+":
                getunreadrequest(cursor,client_sock,user_id)
            
            if flag_bits == "F05+":
                dealwithrequest(cursor,client_sock,data,user_id,db_conn)
            
            if flag_bits == "C00+":
                sendmessage(cursor,client_sock,user_id,data,db_conn)
            
            if flag_bits == "C01+":
                getpreviousmessage(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "C02+":
                getnewmessage(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "G00+":
                creategroup(cursor,client_sock,data,user_id,db_conn)

            if flag_bits == "G01+":
                askgroup(cursor,client_sock,user_id)
            
            if flag_bits == "G02+":
                getgroupmember(cursor,client_sock,data)

            if flag_bits == "C03+":
                sendgroupmessage(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "C04+":
                getgrouppreviousmessage(cursor,client_sock,user_id,data,db_conn)
            
            if flag_bits == "C05+":
                getgroupnewmessage(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "T02+":
                serverrecievefile(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "T00+":
                getpreviousfile(cursor,client_sock,user_id,data,db_conn)
            
            if flag_bits == "T01+":
                getnewfile(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "T03+":
                serversendfile(cursor,client_sock,user_id,data,db_conn)
            
            # if flag_bits == "T03+":
                


            



        # if len(data) > 0:

        #     print(data)

        
        # if data == "!SEEKFRIEND!":
        #     seek_friend(client_sock,user_key)

        # elif data == "!CHATTING!":
        #     chatting(client_sock,user_key)

        # elif data == "!CREATEGROUP!":
        #     create_group(client_sock,user_key)

        # elif data == "!ASKGROUP!":
        #     ask_group(client_sock,user_key)
        
        # elif data == "!GROUPCHAT!":
        #     groupchat(client_sock,user_key)

        # elif data == "!SENDFILE!":
        #     recieve_file(client_sock)



        if data is None:  # 如果data为None，说明客户端已经关闭，退出循环
            print("Client has closed the connection.")

            # global users_data
            # print(user_key)
            # print(users_data)
            # index_to_update = users_data[users_data["key"] == user_key].index[0]
            # if index_to_update >= 0:
            #     users_data.loc[index_to_update, "status"] = "offline"

            # global current_online
            # current_online = [d for d in current_online if d.get('user_key') != user_key]
            # send_msg(client_sock, "LOGIN Success!")
            # print(users_data)
            # users_data.to_csv("users.csv", index=False)
            break


        db_conn.commit()
        time.sleep(0.01)

    client_sock.close()



def main():

    # detect_thread = threading.Thread(target=message_update_detector, args=(0,))
    # detect_thread.daemon = True
    # detect_thread.start()


    SERVER_IP = "0.0.0.0"
    SERVER_PORT = 10020

    # Create socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind socket to IP and port
    try:
        server_sock.bind((SERVER_IP, SERVER_PORT))
    except socket.error as e:
        print("Bind failed! Error: ", str(e))
        server_sock.close()
        exit()

    print("Start Listening!")
    server_sock.listen(5)  # Allow up to 5 incoming connections in the queue

    # Continuous loop to keep server running and accepting multiple clients
    while True:
        client_sock, client_addr = server_sock.accept()
        print(f"Connection established with {client_addr}")
        
        # Start a new thread to handle this client
        client_thread = threading.Thread(target=handle_client, args=(client_sock,))

        client_thread.start()

    

    server_sock.close()  # In this example, we never reach here, but it's good practice to close the server socket

if __name__ == "__main__":
    main()
