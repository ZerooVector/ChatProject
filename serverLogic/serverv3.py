import socket
import threading
import requests
#import pandas as pd # permanently act as an online database
#import numpy as np
import time 
import sqlite3
import datetime as dt 
import os 
import openai 
import torch
import numpy as np
from transformers.models.gpt2 import GPT2LMHeadModel
from transformers import BertTokenizer
import sys
# sys.path.append("..")
from model import GPT2
import cv2
# import os
from PIL import Image
# import torch
# import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1


DB_PATH = "/home/syh/MyProjects/temp/serverLogic/server.db"
FILE_PATH = "/home/syh/MyProjects/temp/serverLogic/filefolder/"
FACE_PATH = "/home/syh/MyProjects/temp/serverLogic/facefolder/"
GPT_PERSONA_PATH = "/home/syh/MyProjects/temp/serverLogic/filefolder/"


os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
openai.api_key = "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" 


device = torch.device("cpu")
tokenizer = BertTokenizer.from_pretrained("/home/syh/MyProjects/temp/serverLogic/gpt2-chinese-cluecorpussmall")

model1 = GPT2().to(device)
model1.eval()
model1.load_state_dict(torch.load("/home/syh/MyProjects/temp/serverLogic/model_checkpoints/GPT3.pt",map_location=torch.device('cpu')),False)

model2 = GPT2().to(device)
model2.eval()
model2.load_state_dict(torch.load("/home/syh/MyProjects/temp/serverLogic/model_checkpoints/GPT2.pt",map_location=torch.device('cpu')),False)


resnet = InceptionResnetV1(pretrained='vggface2').eval()


current_online = []
thread_dict = {}



class ChatManager:
    def __init__(self, api_key, model_name="gpt-3.5-turbo", max_tokens=4096, persona="", max_messages=10):
        self.messages = []
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.set_persona(persona)

    def set_persona(self, persona):
        """Set or change the persona of the model."""
        self.persona = persona
        # self.messages = []
        if self.persona:
            self.messages.append({"role": "system", "content": f"You are {self.persona}."})

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        
        # Instead of checking token count, we simply limit the number of messages
        while len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def get_response(self):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "OpenAI Python v0.2.4"
        }

        data = {
            "model": self.model_name,
            "messages": self.messages
        }

        url = "https://api.openai.com/v1/chat/completions"
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()  # This will raise an exception for 4xx/5xx responses
            return response.json()['choices'][0]['message']['content']
        except requests.Timeout:
            return "AITLE||-||"
        except requests.RequestException as e:
            return "AIERROR||-||" + str(e) 


    def clear_messages(self):
        self.messages = []
        if self.persona:
            self.messages.append({"role": "system", "content": f"You are {self.persona}."})



def answer(sentence, model, tokenizer,max_length = 200):

    input_ids = []
    input_ids.extend(tokenizer.encode(sentence))

    answer = ''
    for i in range(max_length):
        inputs = torch.tensor(input_ids).unsqueeze(0).to(device)

        outputs = model(inputs)
        logits = outputs.logits

        last_token_id = int(np.argmax(logits[0][-1].cpu().detach().numpy()))

        last_token = tokenizer.convert_ids_to_tokens(last_token_id)
        if last_token=="[SEP]":
            break
        answer += last_token
        input_ids.append(last_token_id)

    return answer



# global thread functions 
 



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

    except ConnectionResetError:
        print("Connection reset by peer")

def recv_msg(sock):
    try:
        sock.setblocking(True)
        msg_header = sock.recv(4).decode('utf-8').strip()

        # 检查消息头是否为空
        if not msg_header:
            print("Connection closed by the server")
            # sock.close()
            return None

        msg_len = int(msg_header)
        # 根据消息头指定的长度接收消息主体
        return sock.recv(msg_len).decode('utf-8')

    except UnicodeDecodeError:
        print("Received message couldn't be decoded using UTF-8")
        return "UTF8ERROR!!!"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "UNKNOWNERROR"


def send_file(sock, file_chunk):
    # 发送文件块大小
    header = f"{len(file_chunk):<4}"
    sock.sendall(header.encode('utf-8'))

    # 发送文件块
    sock.sendall(file_chunk)

def recv_file(sock):
    try:
        # 设置套接字超时为10秒
        sock.settimeout(0.4)

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
        # send_msg(sock,"There is a user with same ID!")
    else: # ok
        cmd = '''
        INSERT INTO user (id,nickname,password,status)
        VALUES (?,?,?,?)
        '''
        cursor.execute(cmd,(input_id,input_nickname,input_password,"offline",))
        db_conn.commit()
        send_msg(sock,"L00+SUCCESS")
        ct1 = dt.datetime.now()
        cmd = '''
            INSERT INTO message (initial, via ,terminal, content, datetime,unreadflag,type)
            VALUES(?,?,?,?,?,?,?)
        '''
        cursor.execute(cmd,(input_id,"activate","Customized GPT","hi",ct1,"activate","chatto"))
        cursor.execute(cmd,(input_id,"activate","Customized GPT","hi",ct1,"activate","chatfrom")) 
        cursor.execute(cmd,(input_id,"activate","Little OP","hi",ct1,"activate","chatto"))
        cursor.execute(cmd,(input_id,"activate","Little OP","hi",ct1,"activate","chatfrom"))
        cursor.execute(cmd,(input_id,"activate","Crazy Dave","hi",ct1,"activate","chatto"))
        cursor.execute(cmd,(input_id,"activate","Crazy Dave","hi",ct1,"activate","chatfrom")) # 插入我说的话
        db_conn.commit()
        # send_msg(sock,"Successfully Sign Up!")



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
    SELECT id 
    FROM user 
    WHERE (nickname LIKE ?) OR (id LIKE ?)
    '''
    cursor.execute(cmd,(pattern,pattern,))
    rows = cursor.fetchall() 
    friendlist = []
    for row in rows :
        friendlist.append(row[0])
    cmd = '''
    SELECT id 
    FROM usergroup 
    WHERE (name LIKE ?) OR (id LIKE ?)
    '''
    cursor.execute(cmd,(pattern,pattern,))
    rows = cursor.fetchall() 
    grouplist = []
    for row in rows :
        grouplist.append(row[0])
    info_dict = {}
    info_dict["friends"] = friendlist
    info_dict["groups"] = grouplist
    send_msg(sock,str(info_dict))
    


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
        # send_msg(sock,"F01+ERROR")
        print("Error!")
        # send_msg(sock,"Cannot find this user!")
    else :
        cmd = '''
        SELECT *
        FROM friendrelation
        WHERE user1 = ? AND user2 = ?
        '''
        cursor.execute(cmd,(userid,add_request,))
        rows = cursor.fetchall() 
        if len(rows) > 0:
            print("You have added the user ")
            # send_msg(sock,"F01+ERROR")
            # send_msg(sock,"You have added this user!")
        else :
            if add_request == userid:
                # send_msg(sock,"F01+ERROR")
                # send_msg(sock,"You cannot add yourself!")
                print("You cannot add yourself")
            else :
                ct = dt.datetime.now()
                cmd = '''
                INSERT INTO message(initial,via,terminal,type,unreadflag,datetime,content)
                VALUES(?,?,?,?,?,?,?)
                '''
                cursor.execute(cmd,(userid,"none",add_request,"friendrq","activate",ct,"friendrq"))
                db_conn.commit() 
                # send_msg(sock,"F01+SUCCESS")
                # send_msg(sock,"Please wait another user to check your request!")


def getpreviousrequest_(cursor,sock,userid):
    current_time = dt.datetime.now()
    current_time = str(current_time)
    cmd = '''
    SELECT initial FROM message
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
        # send_msg(sock,"F03+ERROR")
        # send_msg(sock,"You have not recieved request!")
        return 
    else :
        # send_msg(sock,"F03+SUCCESS")
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
        # send_msg(sock,"F05+ERROR")
        # send_msg(sock,"Request Do not exists!")
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
        # send_msg(sock,"F05+SUCCESS")
        # send_msg(sock,"You accept another user's request!")
        current_time = dt.datetime.now()
        current_time = str(current_time)
        cmd = '''
        INSERT INTO message(initial,via,terminal,type,unreadflag,datetime,content)
        VALUES (?,?,?,?,?,?,?)
        '''
        content = "hi"
        cursor.execute(cmd,(userid,"none",source,"chatfrom","activate",current_time,content))
        cursor.execute(cmd,(userid,"none",source,"chatto","activate",current_time,content))
        db_conn.commit()
        
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
        # send_msg(sock,"F05+SUCCESS")
        # send_msg(sock,"You refuse another user's request!")
    


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
        print("Create Group Error")
        # send_msg(sock,"G00+ERROR")
        # send_msg(sock,"Duplicate Group id!")
    
        #     send_msg(sock,"G00+ERROR")
        #     send_msg(sock,"Some users are not your friend!")
    else :
        print("Start add")
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
        current_time = dt.datetime.now()
        cursor.execute(cmd,(input_id,userid))
        db_conn.commit()
        current_time = str(current_time)
        cmd = '''
            INSERT INTO message(initial,via,terminal,type,unreadflag,datetime,content)
            VALUES(?,?,?,?,?,?,?)
        '''
        for person in members:
            cursor.execute(cmd,(userid,input_id,person,"chat","activate",current_time,"hi"))
            db_conn.commit()

            # send_msg(sock,"G00+SUCCESS")
            # send_msg(sock,"Successfully Create a Group!")

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
        print("C00+ERROR")
        # send_msg(sock,"C00+ERROR")
        # send_msg(sock,"This user isn't your friend!")
    else :
        current_time = dt.datetime.now()
        current_time = str(current_time)
        cmd = '''
        INSERT INTO message(initial,via,terminal,type,unreadflag,datetime,content)
        VALUES (?,?,?,?,?,?,?)
        '''
        cursor.execute(cmd,(userid,"none",target,"chatfrom","activate",current_time,content))
        cursor.execute(cmd,(userid,"none",target,"chatto","activate",current_time,content))
        db_conn.commit()
        # send_msg(sock,"C00+SUCCESS")



def getpreviousmessage_(cursor,sock,userid,source,db_conn,clear = 1):
    current_time = dt.datetime.now()
    current_time = str(current_time)
    cmd = '''
    SELECT initial, via, terminal, content,datetime FROM message
    WHERE 
    (
     type = ?
    AND datetime < ?
    AND initial = ?
    AND terminal = ?)
    OR 
    (
    
    type = ?
    AND datetime < ?
    AND initial = ?
    AND terminal = ?
    )
    ORDER BY datetime ASC
    '''
    cursor.execute(cmd,("chatto",current_time,source,userid,"chatfrom",current_time,userid,source))
    rows = cursor.fetchall()
    if clear == 1 :  # clear unread flag
        cmd = '''
        UPDATE message 
        SET unreadflag = ?
        WHERE 
        (
    type = ?
    AND datetime < ?
    AND initial = ?
    AND terminal = ?)
    OR 
    (
    
    type = ?
    AND datetime < ?
    AND initial = ?
    AND terminal = ?
    )
        '''
        cursor.execute(cmd,("release","chatto",current_time,source,userid,"chatfrom",current_time,userid,source))
    db_conn.commit()
    # res = [] 
    # for row in rows:
    #     res.append(row[0])
    return rows 


def getpreviousmessage(cursor,sock,userid,data,db_conn,N = 1000):
    source = data 
    rows = getpreviousmessage_(cursor,sock,userid,source,db_conn,clear = 1)
    rows = rows[-N:]
    # rows = str(rows)
    # if len(rows) == 0 :
    #     send_msg(sock,"C01+ERROR")
    #     send_msg(sock,"No chat History!")
    # else :
    rows = str(rows)
    # send_msg(sock,"C01+SUCCESS")
    send_msg(sock,str(rows) )



def getnewmessage_(cursor,sock,userid,source,db_conn):
    cmd = '''
    SELECT initial, via, terminal, content, datetime FROM message
    WHERE
    (
     type = ?
    AND unreadflag = ?
    AND initial = ?
    AND terminal = ?)
    OR
    (
     type = ?
    AND unreadflag = ?
    AND initial = ?
    AND terminal = ?
    )
    ORDER BY datetime ASC
    '''
    cursor.execute(cmd,("chatto","activate",source,userid,"chatfrom","activate",userid,source))
    rows = cursor.fetchall()
    cmd =  '''
    UPDATE  message
    SET unreadflag = ?
    WHERE
    (
type = ?
    AND unreadflag = ?
    AND initial = ?
    AND terminal = ?)
    OR
    (
    
type = ?
    AND unreadflag = ?
    AND initial = ?
    AND terminal = ?
    )
    '''
    cursor.execute(cmd,("release","chatto","activate",source,userid,"chatfrom","activate",userid,source))  # release the flag
    db_conn.commit()
    # res = [] 
    # for row in rows:
    #     res.append(row[0])
    return rows  


def getnewmessage(cursor,sock,userid,data,db_conn):
    source = data 
    rows = getnewmessage_(cursor,sock,userid,source,db_conn)
    # if len(rows) == 0 :
    #     send_msg(sock,"C02+ERROR")
    #     send_msg(sock,"No new message!")
    # else :
    rows = str(rows)
        # send_msg(sock,"C02+SUCCESS")
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
        send_msg(sock,str(res) )
    

def setgroupmanager(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    target = data[0] 
    memlist = data[1].strip("[]").split(",")
    memlist.append(userid)
    cmd = '''
    SELECT master FROM usergroup 
    WHERE id = ? 
    '''
    cursor.execute(cmd,(target,))
    res = cursor.fetchall()[0][0] 
    if res != userid:
        send_msg(sock,"G03+ERROR")
        send_msg(sock,"You cannot modifiy group info!")
        return 
    
    all_mem = getgroupmember_(cursor,sock,target)
    if set(memlist).issubset(set(all_mem)) == 0:
        send_msg(sock,"G03+ERROR")
        send_msg(sock,"Some user are not group member!")
        return 

    cmd = '''
    DELETE FROM groupmanager
    WHERE groupid  = ?
    '''
    cursor.execute(cmd,(target,))
    db_conn.commit()
    
    cmd = '''
    INSERT INTO groupmanager(groupid,userid)
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
    WHERE id = ?
    '''
    cursor.execute(cmd,(rq,))
    rows = cursor.fetchall() 
    if len(rows) == 0 :
        # send_msg(sock,"G04+ERROR")
        # send_msg(sock,"Cannot find this group!")
        print("Cannot find the group!")
        return 
    cmd = '''
    INSERT INTO message(initial,via,terminal,type,datetime,unreadflag,content)
    VALUES(?,?,?,?,?,?,?)
    '''
    ct = dt.datetime.now() 
    manager = getgroupmanager_(cursor,sock,rq)
    for person in manager:
        cursor.execute(cmd,(userid,rq,person,"grouprq",ct,"activate","grouprq"))
        db_conn.commit() 
    # send_msg(sock,"G04+SUCCESS")
    # send_msg(sock,"Successfully Send Request!")


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
    SELECT initial,via,unreadflag FROM message
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


def getpreviousgrouprequest(cursor,sock,userid):
    rows = getpreviousgrouprequest_(cursor,sock,userid)
    if len(rows) == 0:
        send_msg(sock,"G10+ERROR")
        send_msg(sock,"No Add Group Request!")
    else :
        send_msg(sock,"G10+SUCCESS")
        send_msg(sock,str(rows))


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
        cursor.execute(cmd,(g,userid,ct,"grouprq","activate"))
        rows = cursor.fetchall()
        for row in rows:
            res.append(row)
    return res 

def getunreadgrouprequest(cursor,sock,userid):
    rows = getpreviousgrouprequest_(cursor,sock,userid)
    if len(rows) == 0:
        send_msg(sock,"G11+ERROR")
        send_msg(sock,"No New Add Group Request!")
    else :
        send_msg(sock,"G11+SUCCESS")
        send_msg(sock,str(rows))


def dealwithgrouprequest(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    group = data[0] 
    user = data[1] 
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
        # send_msg(sock,"G06+ERROR")
        # send_msg(sock,"Cannot find this request!")
        return 
    manager = getgroupmanager_(cursor,sock,group)
    if userid not in manager:
        return 
        # send_msg(sock,"G06+ERROR")
        # send_msg(sock,"You are not the manager of the group!")

    if respose =="Y" or respose == "y":
        cmd = '''
        UPDATE message 
        SET unreadflag = ? 
        WHERE initial = ?
        AND via = ?
        AND type = ?
        AND unreadflag = ?
        '''
        cursor.execute(cmd,("accept",user,group,"grouprq","activate"))
        db_conn.commit() 
        cmd = '''
        INSERT INTO grouprelation(groupid,userid)
        VALUES(?,?)
        '''
        cursor.execute(cmd,(group,user))
        db_conn.commit()

        content = "hi"
        current_time = dt.datetime.now()
        current_time = str(current_time)
        cmd = '''
        INSERT INTO message(initial,via,terminal,type,unreadflag,datetime,content)
        VALUES(?,?,?,?,?,?,?)
        '''
        cursor.execute(cmd,(userid,group,user,"chat","activate",current_time,content))

    else :
        cmd = '''
        UPDATE message 
        SET unreadflag = ? 
        WHERE initial = ?
        AND via = ?
        AND type = ?
        AND unreadflag = ?
        '''
        cursor.execute(cmd,("refuse",user,group,"grouprq","activate"))
        db_conn.commit()



def manageradduser(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    group = data[0] 
    user = data[1] 
    cmd = '''
    SELECT * FROM user
    WHERE id = ?
    '''
    cursor.execute(cmd,(user,))
    res = cursor.fetchall() 
    if len(res) == 0:
        # send_msg(sock,"G07+ERROR")
        # send_msg(sock,"User Not Exist!")
        return 
    
    cmd = '''
    SELECT * FROM usergroup 
    WHERE id = ?
    '''
    cursor.execute(cmd,(group,))
    res = cursor.fetchall() 
    if len(res) == 0:
        # send_msg(sock,"G07+ERROR")
        # send_msg(sock,"Group Not Exist!")
        return 
    
    manager = getgroupmanager_(cursor,sock,group)
    if userid not in manager:
        # send_msg(sock,"G07+ERROR")
        # send_msg(sock,"You are not a manager of the group!")
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
    WHERE id = ?
    '''
    cursor.execute(cmd,(group,))
    rows = cursor.fetchall() 
    if len(rows) == 0:
        # send_msg(sock,"G08+ERROR")
        # send_msg(sock,"Group not Exist!")
        return 
    
    mem = getgroupmember_(cursor,sock,group)
    if user not in mem:
        # send_msg(sock,"G08+ERROR")
        # send_msg(sock,"User not in the group!")
        return 
    
    manager = getgroupmanager_(cursor,sock,group)
    if userid not in manager:
        # send_msg(sock,"G08+ERROR")
        # send_msg(sock,"You are not a manager of the group!")
        return 
    cmd = '''
    DELETE FROM grouprelation
    WHERE groupid = ? AND userid = ?
    '''
    cursor.execute(cmd,(group,user))
    db_conn.commit() 
    # send_msg(sock,"G08+SUCCESS")
    # send_msg(sock,"You removed a user into the group!")
    
    

def sendgroupmessage(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    target = data[0]
    content = data[1] 
    added_groups = askgroup_(cursor,sock,userid)
    if target not in added_groups:
        # send_msg(sock,"C03+ERROR")
        # send_msg(sock,"You have not add this group!")
        print("C03+ERROR")
    else :
        members = getgroupmember_(cursor,sock,target)
        if len(members) == 0 :
            # send_msg(sock,"C03+ERROR")
            # send_msg(sock,"No members in the group!")
            print("C03+ERROR")
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
            # send_msg(sock,"C03+SUCCESS")

    
def getgrouppreviousmessage_(cursor,sock,userid,groupid,db_conn,clear = 1):
    current_time = dt.datetime.now()
    current_time = str(current_time)
    cmd = '''
    SELECT initial,via,terminal,content,datetime FROM message
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
    SELECT initial, via,terminal,content,datetime FROM message
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
    # if len(rows) == 0 :
    #     send_msg(sock,"C05+ERROR")
    #     send_msg(sock,"No new message!")
    # else :
    rows = str(rows)
        # send_msg(sock,"C05+SUCCESS")
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
    ftype = data[2]
    originname = os.path.basename(address)
    savename = str(getfilecount_(cursor)) +"-" + originname 
    savepath = FILE_PATH + savename
    friend = getfriendslist_(cursor,sock,userid)
    
    if target not in friend:
        print("Receive Error")
        while True :
            file_chunk = recv_file(sock)  # recieve a chunk
            if not file_chunk:
                break
            # file.write(file_chunk)
        file_chunk = ""
        # send_msg(sock,"T02+ERROR")
        # send_msg(sock,"This user is not your friend!")
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
            # print("recieving...")

    cmd = '''
    INSERT INTO file(originalname,storagename,initial,via,terminal,type,status,datetime)
    VALUES(?,?,?,?,?,?,?,?)
    '''
    current_time = dt.datetime.now() 
    current_time = str(current_time)
    cursor.execute(cmd,(originname,savename,userid,"none",target,ftype + "to","activate",current_time))
    cursor.execute(cmd,(originname,savename,userid,"none",target,ftype + "from","activate",current_time))
    # cursor.execute(cmd,(originname,savename,target,"none",userid,ftype + "to","activate",current_time))
    # cursor.execute(cmd,(originname,savename,userid,"none",target,ftype + "from","activate",current_time))
    db_conn.commit()
    # send_msg(sock,"T02+SUCCESS")
    # send_msg(sock,"No new message!")


def serverrecievefacefile_(cursor,sock,userid,db_conn,mode = "pattern"):   # 该函数的作用是写一张人脸
    originname = userid + mode
    savename = str(getfilecount_(cursor)) +"-" + originname 
    savepath = FACE_PATH + savename

    with open(savepath,"wb") as file :
        while True :
            file_chunk = recv_file(sock)  # recieve a chunk
            if not file_chunk:
                break
            file.write(file_chunk)
            # print("recieving...")

    cmd = '''
    INSERT INTO file(originalname,storagename,initial,via,terminal,type,status,datetime)
    VALUES(?,?,?,?,?,?,?,?)
    '''
    current_time = dt.datetime.now() 
    current_time = str(current_time)
    if mode  == "pattern" :
        cursor.execute(cmd,(originname,savename,userid,"none","none","facefile","pattern",current_time))
        db_conn.commit()
        # send_msg(sock,"T10+SUCCESS")
    if mode == "check":
        cursor.execute(cmd,(originname,savename,userid,"none","none","facefile","check",current_time))
        db_conn.commit()
        # send_msg(sock,"T10+SUCCESS")


def setpatternface(cursor,sock,userid,data,db_conn):
    # #先覆盖之前的人脸
    # cmd = '''
    # SELECT storagename FROM file 
    # WHERE initial = ?
    # AND via = ?
    # AND terminal = ?
    # AND type = ?
    # AND status = ?
    # '''
    # cursor.execute(cmd,(userid,"none","none","facefile","pattern"))
    

    # rows = cursor.fetchall()
    # res = [] 
    # for row in rows :
    #     res.append(row[0])
    # for name in res:
    #     full_path = os.path.join(FACE_PATH,name)
    #     if os.path.exists(full_path):
    #         try:
    #             os.remove(full_path)
    #         except:
    #             print("Delete Error!")
    
    cmd = '''
    UPDATE file 
    SET status = ? 
    WHERE initial = ?
    AND via = ?
    AND terminal = ?
    AND type = ?
    AND status = ?
    '''
    cursor.execute(cmd,("release",userid,"none","none","facefile","pattern"))
    db_conn.commit() 

    # 接受10张全新的人脸
    for i in range(1):
        serverrecievefacefile_(cursor,sock,userid,db_conn,mode = "pattern")
    # send_msg(sock,"R00+SUCCESS")


def checkfacelogin(cursor,sock,data,db_conn):
    userid = data  
    for i in range(1):
        serverrecievefacefile_(cursor,sock,userid,db_conn,mode = "check")
    cmd = '''
    SELECT storagename FROM file 
    WHERE initial = ?
    AND via = ?
    AND terminal = ?
    AND type = ?
    AND status = ?
    '''
    cursor.execute(cmd,(userid,"none","none","facefile","check"))
    rows = cursor.fetchall() 
    check_res = []
    for row in rows:
        check_res.append(row[0])

    if len(check_res) == 0:
        send_msg(sock,"RECOERR")
        # send_msg(sock,"Upload Failed!")
        return 


    cmd = '''
    SELECT storagename FROM file 
    WHERE via = ?
    AND terminal = ?
    AND type = ?
    AND status = ?
    '''
    cursor.execute(cmd,("none","none","facefile","pattern"))
    rows = cursor.fetchall() 
    pattern_res = []
    for row in rows:
        pattern_res.append(row[0])

    cmd = '''
    SELECT storagename FROM file 
    WHERE initial = ? AND via = ?
    AND terminal = ?
    AND type = ?
    AND status = ?
    '''
    cursor.execute(cmd,(userid,"none","none","facefile","pattern"))
    rows = cursor.fetchall() 
    your_pattern_res = []
    for row in rows:
        your_pattern_res.append(row[0])


    cmd = '''
    UPDATE FILE 
    SET status = ?
    WHERE initial = ?
    AND via = ?
    AND terminal = ?
    AND type = ?
    AND status = ?
    '''
    cursor.execute(cmd,("release",userid,"none","none","facefile","check"))
    db_conn.commit()

    
    if len(pattern_res) == 0:
        send_msg(sock,"RECOERR")
        # send_msg(sock,"You Have Not Upload Pattern Faces!")
        return 
    
    if len(your_pattern_res) == 0:
        send_msg(sock,"RECOERR")
        return 

    print(pattern_res)
    # train_encode=[]
    imageMatrix = []
    count = 0
    for item in pattern_res:
        full_path = os.path.join(FACE_PATH,item)
        # print(full_path)
        img = cv2.imread(full_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


        count += 1
        # img = cv2.imread(imgpath, cv2.IMREAD_GRAYSCALE)
        # 灰度图矩阵
        mats = np.array(img)
        print(mats.shape)
        # 将灰度矩阵转换为向量
        imageMatrix.append(mats.ravel())
 
    imageMatrix = np.array(imageMatrix)# imageMatrix是图片矩阵；n X 40000 ,n为图片个数
    print(imageMatrix.shape)
    from PIL import Image
    # 矩阵转置后每一列都是一个图像，40000 X n，对行求均值
    imageMatrix = np.transpose(imageMatrix)
    imageMatrix = np.mat(imageMatrix)
    # 原始矩阵的行均值
    mean_img = np.mean(imageMatrix, axis=1)
    #得到平均脸
    mean_img1 = np.reshape(mean_img,(200,200))
    im = Image.fromarray(np.uint8(mean_img1))
    # 均值中心化
    imageMatrix = imageMatrix - mean_img

    # W是特征向量， V是特征向量组 
    imag_mat = (imageMatrix.T * imageMatrix) / float(count)
    W, V = np.linalg.eig(imag_mat)
    # V_img是协方差矩阵的特征向量组
    V_img = imageMatrix * V
    # 降序排序后的索引值
    axis = W.argsort()[::-1]
    V_img = V_img[:, axis]

    # 取前15个最大特征值对应的特征向量，组成映射矩阵
    V_img_finall = V_img[:, :15]

    sim_list = [] 
    for i in range(1):
        full_path = os.path.join(FACE_PATH,your_pattern_res[i])
        # print(full_path)
        img1 = cv2.imread(full_path)
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        mats1 = np.array(img1)
        # 将灰度矩阵转换为向量
        sample_mats = mats1.ravel()
        sample =  sample_mats  * V_img_finall

        full_path = os.path.join(FACE_PATH,check_res[i])
        # print(full_path)
        img2 = cv2.imread(full_path)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        mats2 = np.array(img2)
    # 将灰度矩阵转换为向量
        var_mats = mats2.ravel()
        var =   var_mats  * V_img_finall
        sim_list.append(np.linalg.norm(sample - var))
    sim_list = np.array(sim_list)
    mean_sim = np.mean(sim_list)
    if mean_sim <  100000000:
        send_msg(sock,"RECOSUCCESS")
        return userid
    else :
        send_msg(sock,"RECOFAIL")
        return None




def getallfile_(cursor,userid,):
    cmd = '''
    SELECT storagename FROM file 
    WHERE terminal = ?
    '''
    cursor.execute(cmd,(userid,))
    rows = cursor.fetchall() 
    res = [] 
    for row in rows:
        res.append(row[0])
    return res 


def serversendfile(cursor,sock,userid,data,db_conn):
    # data = data.split("||-||")
    strname = data
    # ftype = data[1]
    all_file = getallfile_(cursor,userid)
    # if strname not in all_file:
        # send_msg(sock,"T03+ERROR")
        # send_msg(sock,"You cannot recieve this file!")
    
    savepath = FILE_PATH +  strname 
    if not os.path.exists(savepath):
        send_msg(sock,"T03+ERROR")
            # send_msg(sock,"File not Exist!")
        print(f"File {savepath} does not exist!")  # client checks the file is or not exist 
        return
    else:
    # pause_event.clear()
        # send_msg(sock,"T03+CONTINUE")
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
                # print("sending...")
        time.sleep(0.15)
        # send_msg(sock,"T03+SUCCESS")
        # send_msg(sock,"Successfully Send the file!")


def serversendaudiofile(cursor,sock,userid,data,db_conn):
    # def serversendfile(cursor,sock,userid,data,db_conn):
    # data = data.split("||-||")
    strname = data
    # ftype = data[1]
    all_file = getallfile_(cursor,userid)
    if strname not in all_file:
        send_msg(sock,"T08+ERROR")
        send_msg(sock,"You cannot recieve this file!")
    else :
        savepath = FILE_PATH +  strname 
        if not os.path.exists(savepath):
            send_msg(sock,"T08+ERROR")
            send_msg(sock,"File not Exist!")
            print(f"File {savepath} does not exist!")  # client checks the file is or not exist 
            return


        msg_to_send = "T08+"+strname
        send_msg(sock,msg_to_send)

        with open(savepath,"rb") as file :
    
            file_chunk = file.read(4096*2)
            while file_chunk:
                send_file(sock,file_chunk)
                file_chunk = file.read(4096*2) 
                print("sending...")
        time.sleep(0.15)



def getpreviousfile_(cursor,sock,userid,source,ftype,db_conn,clear = 1):
    ct = dt.datetime.now()
    ct = str(ct)
    cmd = '''
    SELECT initial, via,terminal,storagename, datetime FROM file
    WHERE (initial = ?
    AND via = ?
    AND terminal = ?
    AND type = ?
    AND datetime < ?)
    OR
    (initial = ?
    AND via = ?
    AND terminal = ?
    AND type = ?
    AND datetime < ?)
    '''
    cursor.execute(cmd,(source,"none",userid,ftype+"to",ct,userid,"none",source,ftype+"from",ct))
    rows = cursor.fetchall() 
    if clear == 1:
        cmd = '''
        UPDATE file SET status = ?
        WHERE (initial = ?
        AND via = ?
        AND terminal = ?
        AND type = ?
        AND status = ?)
        OR
        (initial = ?
        AND via = ?
        AND terminal = ?
        AND type = ?
        AND status = ?)
        '''
        cursor.execute(cmd,("release",source,"none",userid,ftype+"to","activate",userid,"none",source,ftype+"from","activate"))
        db_conn.commit()
    return rows 



def getpreviousfile(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    source = data[0] 
    ftype = data[1]
    rows = getpreviousfile_(cursor,sock,userid,source,ftype,db_conn)
    # if len(rows) == 0:
    #     send_msg(sock,"T00+ERROR")
    #     send_msg(sock,"Cannot find previous files!")
    # else :
        # send_msg(sock,"T00+SUCCESS")
    send_msg(sock,str(rows))

    

def getnewfile_(cursor,sock,userid,source,ftype,db_conn):
    cmd = '''
    SELECT initial, via, terminal, storagename, datetime
    FROM file 
    WHERE (initial = ?
    AND via = ?
    AND terminal = ?
    AND type = ?
    AND status = ?)
    OR
    (
        initial = ?
    AND via = ?
    AND terminal = ?
    AND type = ?
    AND status = ?
    )
    ORDER BY datetime ASC
    '''
    cursor.execute(cmd,(source,"none",userid,ftype + "to","activate",userid,"none",source,ftype + "from","activate"))
    rows = cursor.fetchall() 
    cmd = '''
    UPDATE file SET status = ? 
    WHERE (initial = ?
    AND via = ?
    AND terminal = ?
    AND type = ?
    AND status = ?)
    OR
     (initial = ?
    AND via = ?
    AND terminal = ?
    AND type = ?
    AND status = ?)
    '''
    cursor.execute(cmd,("release",source,"none",userid,ftype + "to","activate",userid,"none",source,ftype + "from","activate"))
    db_conn.commit() 
    return rows 



def getnewfile(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    source = data[0] 
    ftype = data[1]
    rows = getnewfile_(cursor,sock,userid,source,ftype,db_conn)
    # if len(rows) == 0:
    #     send_msg(sock,"T01+ERROR")
    #     send_msg(sock,"Cannot find previous files!")
    # else :
        # send_msg(sock,"T01+SUCCESS")
    send_msg(sock,str(rows))



def serverrecievegroupfile(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    target = data[0] 
    address = data[1]
    ftype = data[2]
    originname = os.path.basename(address)
    savename = str(getfilecount_(cursor)) +"-" + originname 
    savepath = FILE_PATH + savename
    # friend = getfriendslist_(cursor,sock,userid)
    added_groups = askgroup_(cursor,sock,userid)
    if target not in added_groups:
        # send_msg(sock,"T04+ERROR")
        # send_msg(sock,"You have not add this group!")
        while True :
            file_chunk = recv_file(sock)  # recieve a chunk
            if not file_chunk:
                break
    else :
        members = getgroupmember_(cursor,sock,target)
        if len(members) == 0 :
            # send_msg(sock,"T04+ERROR")
            # send_msg(sock,"No members in the group!")
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
            VALUES(?,?,?,?,?,?,?,?)
            '''
            for person in members:
                cursor.execute(cmd,(userid,target,person,ftype,"activate",current_time,originname,savename))
                db_conn.commit()
            # send_msg(sock,"T04+SUCCESS")
    # else :
        # send_msg(sock,"T01+CONTINUE")
    # cnt = 0 
    


def getpreiviousgroupfile_(cursor,sock,userid,source,ftype,db_conn,clear = 1):
    ct = dt.datetime.now()
    ct = str(ct)
    cmd = '''
    SELECT initial,via,terminal,storagename,datetime FROM file
    WHERE via = ?
    AND terminal = ?
    AND type = ?
    AND datetime < ?
    '''
    cursor.execute(cmd,(source,userid,ftype,ct))
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
        cursor.execute(cmd,("release",source,userid,ftype,"activate"))
        db_conn.commit()
    return rows 

def getpreviousgroupfile(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    source = data[0] 
    ftype = data[1]
    rows = getpreiviousgroupfile_(cursor,sock,userid,source,ftype,db_conn)
    if len(rows) == 0:
        send_msg(sock,"T05+ERROR")
        send_msg(sock,"Cannot find previous group files!")
    else :
        send_msg(sock,"T05+SUCCESS")
        send_msg(sock,str(rows))


def getnewgroupfile_(cursor,sock,userid,source,ftype,db_conn):
    cmd = '''
    SELECT initial, via , terminal, storagename, datetime
    FROM file 
    WHERE 
    via = ?
    AND terminal = ?
    AND type = ?
    AND status = ?
    '''
    cursor.execute(cmd,(source,userid,ftype,"activate"))
    rows = cursor.fetchall() 
    cmd = '''
    UPDATE file SET status = ? 
    WHERE 
    via = ?
    AND terminal = ?
    AND type = ?
    AND status = ?
    '''
    cursor.execute(cmd,("release",source,userid,ftype,"activate"))
    db_conn.commit() 
    return rows 


def getnewgroupfile(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    source = data[0] 
    ftype = data[1]
    rows = getnewgroupfile_(cursor,sock,userid,source,ftype,db_conn)
    if len(rows) == 0:
        send_msg(sock,"T06+ERROR")
        send_msg(sock,"Cannot find new group files!")
    else :
        send_msg(sock,"T06+SUCCESS")
        send_msg(sock,str(rows))


def changeGPTpersona(cursor,sock,data,userid,db_conn):
    content = data 
    myfilename = str(userid) + "||-||" + "GPTpersona.txt"
    fullpath = GPT_PERSONA_PATH + myfilename 
    with open(fullpath , "w" , encoding ="utf-8") as file :
        file.write(content)
    ct = dt.datetime.now() 
    # 需要清除GPT之前留存的所有聊天记录
    cmd = '''
    UPDATE message 
    SET via = ?
    WHERE initial = ? 
    AND terminal = ?
    AND datetime < ?
    '''
    cursor.execute(cmd,("release","Customized GPT",userid,ct))
    db_conn.commit() 
    cursor.execute(cmd,("release",userid,"Customized GPT",ct))
    db_conn.commit() 
    # send_msg(sock,"A00+SUCCESS")
    # send_msg(sock,"You changed GPT's persona! All the history were cleared!")


def readGPTpersona_(userid):
    myfilename = str(userid) + "||-||" + "GPTpersona.txt"
    fullpath = GPT_PERSONA_PATH + myfilename 
    res = None 
    if not os.path.exists(fullpath):
        return None 
    with open(fullpath,"r", encoding = "utf-8") as file:
        res = file.read()
        if len(res) == 0:
            return None 
        else:
            return res 


def readGPTpersona(sock,userid):
    res = readGPTpersona_(userid)
    if res is None:
        send_msg(sock,"A01+ERROR")
        send_msg(sock,"Your GPT does not have a persona!")
        return 
    send_msg(sock,"A01+SUCCESS")
    send_msg(sock,res)


def sendGPTmessage(cursor,sock,data,userid,db_conn,myGPT):
    data = data.split("||-||")
    target = data[0] 
    content = data[1] 

    if target == "Customized GPT":
        # 清空GPT的消息库
        ct1 = dt.datetime.now()
        cmd = '''
            INSERT INTO message (initial, via ,terminal, content, datetime,unreadflag,type)
            VALUES(?,?,?,?,?,?,?)
            '''
        cursor.execute(cmd,(userid,"activate","Customized GPT",content,ct1,"activate","chatto"))
        cursor.execute(cmd,(userid,"activate","Customized GPT",content,ct1,"activate","chatfrom"))  # 插入我说的话
        # cursor.execute(cmd,("Customized GPT","activate",userid,content,ct1,"activate","AIchatfrom"))
        db_conn.commit() 

        myGPT.clear_messages() 
        mypersona = readGPTpersona_(userid)
        print(mypersona)
        
        cmd = '''
        SELECT initial, content from message
        WHERE ((initial = ? AND terminal = ?) OR (initial = ? AND terminal = ?))
        AND via = ? AND type = ?
        ORDER BY datetime ASC 
        '''
        
        cursor.execute(cmd,(userid,"Customized GPT","Customized GPT",userid,"activate","chatfrom")) 
        
        rows = cursor.fetchall() # 获取过往的所有聊天记录
        # print(rows)
        for row in rows:
            if row[0] == "Customized GPT" :
                myGPT.add_message("assistant", row[1])
            elif row[0] == userid :
                myGPT.add_message("user",row[1])
        myGPT.set_persona(persona = mypersona)
        print(myGPT.messages)
        res = myGPT.get_response()
        if res[0:6] == "AITLE" or res[0:8] == "AIERROR":
            # send_msg(sock,"A02+ERROR")
            # send_msg(sock,"Time Limit Exceed or other error!")
            return 
        else :
            ct2 = dt.datetime.now()
            cmd = '''
            INSERT INTO message (initial, via ,terminal, content, datetime,unreadflag,type)
            VALUES(?,?,?,?,?,?,?)
            '''
            cursor.execute(cmd,("Customized GPT","activate",userid,res,ct2,"activate","chatto"))
            cursor.execute(cmd,("Customized GPT","activate",userid,res,ct2,"activate","chatfrom"))
            # cursor.execute(cmd,(userid,"activate","Customized GPT",res,ct2,"activate","AIchatto")) 
            db_conn.commit() 
            # send_msg(sock,"A02+SUCCESS")
            # send_msg(sock,"You have send a message to GPT3.5!")


    elif target == "Little OP":
        ct1 = dt.datetime.now()
        cmd = '''
            INSERT INTO message (initial, via ,terminal, content, datetime,unreadflag,type)
            VALUES(?,?,?,?,?,?,?)
            '''
        cursor.execute(cmd,(userid,"activate","Little OP",content,ct1,"activate","chatto"))
        cursor.execute(cmd,(userid,"activate","Little OP",content,ct1,"activate","chatfrom"))
        db_conn.commit() 

        commu_list = [] 
        cmd = '''
        SELECT initial, content from message
        WHERE ((initial = ? AND terminal = ?) OR (initial = ? AND terminal = ?))
        AND via = ? AND type = ?
        ORDER BY datetime ASC 
        '''
        
        cursor.execute(cmd,(userid,"Little OP","Little OP",userid,"activate","chatfrom")) 
        rows = cursor.fetchall() # 获取过往的所有聊天记录
        for row in rows :
            commu_list.append(row[1])
        while len(commu_list) > 20:
            commu_list.pop(0)
        merged_sentence =  '[SEP]'.join(commu_list)
        res = answer(merged_sentence, model1, tokenizer)
        ct2 = dt.datetime.now()
        cmd = '''
        INSERT INTO message (initial, via ,terminal, content, datetime,unreadflag,type)
        VALUES(?,?,?,?,?,?,?)
        '''
        cursor.execute(cmd,("Little OP","activate",userid,res,ct2,"activate","chatto"))
        cursor.execute(cmd,("Little OP","activate",userid,res,ct2,"activate","chatfrom"))
        db_conn.commit() 
        # send_msg(sock,"A02+SUCCESS")
        # send_msg(sock,"You have send a message to DIY1-AI!")


    elif target == "Crazy Dave":
        ct1 = dt.datetime.now()
        cmd = '''
            INSERT INTO message (initial, via ,terminal, content, datetime,unreadflag,type)
            VALUES(?,?,?,?,?,?,?)
            '''
        cursor.execute(cmd,(userid,"activate","Crazy Dave",content,ct1,"activate","chatto"))
        cursor.execute(cmd,(userid,"activate","Crazy Dave",content,ct1,"activate","chatfrom"))
        db_conn.commit() 

        commu_list = [] 
        cmd = '''
        SELECT initial, content from message
        WHERE ((initial = ? AND terminal = ?) OR (initial = ? AND terminal = ?))
        AND via = ? AND type = ?
        ORDER BY datetime ASC 
        '''
        
        cursor.execute(cmd,(userid,"Crazy Dave","Crazy Dave",userid,"activate","chatfrom")) 
        rows = cursor.fetchall() # 获取过往的所有聊天记录
        for row in rows :
            commu_list.append(row[1])
        while len(commu_list) > 20:
            commu_list.pop(0)
        merged_sentence =  '[SEP]'.join(commu_list)
        res = answer(merged_sentence, model2, tokenizer)
        ct2 = dt.datetime.now()
        cmd = '''
        INSERT INTO message (initial, via ,terminal, content, datetime,unreadflag,type)
        VALUES(?,?,?,?,?,?,?)
        '''
        cursor.execute(cmd,("Crazy Dave","activate",userid,res,ct2,"activate","chatto"))
        cursor.execute(cmd,("Crazy Dave","activate",userid,res,ct2,"activate","chatfrom"))
        db_conn.commit() 
        # send_msg(sock,"A02+SUCCESS")
        # send_msg(sock,"You have send a message to DIY2-AI!")

    



def getpreviousGPTmessage_(cursor,sock,userid,source,db_conn,clear = 1):
    ct = dt.datetime.now()
    cmd = '''
    SELECT via, content FROM message 
    WHERE initial = ? AND terminal = ? AND type = ?
    AND datetime < ?   '''
    cursor.execute(cmd,(source,userid,"AIchat",ct))
    rows = cursor.fetchall() 
    if clear == 1:
        cmd = '''
        UPDATE message 
        SET unreadflag = ? 
        WHERE initial = ?
        AND terminal = ?
        AND type = ?
        AND datetime < ?
        '''
        cursor.execute(cmd,("release",source,userid,"AIchat",ct,))
        db_conn.commit() 
    return rows




def getpreviousGPTmessage(cursor,sock,userid,data,db_conn):
    source = data 
    rows = getpreviousGPTmessage_(cursor,sock,userid,source,db_conn)
    if len(rows) == 0:
        send_msg(sock,"A03+ERROR")
        send_msg(sock,"No Exist Message!")
    else :
        send_msg(sock,"A03+SUCCESS")
        send_msg(sock,str(rows))




def getunreadGPTmessage_(cursor,sock,userid,source,db_conn):
    cmd = '''
    SELECT via, content FROM message 
    WHERE initial = ? AND terminal = ?
    AND type = ?
    AND unreadflag = ?
    '''
    cursor.execute(cmd,(source,userid,"AIchat","activate",))
    rows = cursor.fetchall() 
    cmd = '''
    UPDATE message
    SET unreadflag = ?
    WHERE initial = ? AND terminal = ? AND type =?
    AND unreadflag = ?
    '''
    cursor.execute(cmd,("release",source,userid,"AIchat","activate",))
    db_conn.commit()
    return rows 




def getunreadGPTmessage(cursor,sock,userid,data,db_conn):
    source = data 
    rows = getunreadGPTmessage_(cursor,sock,userid,source,db_conn)
    if len(rows) == 0:
        send_msg(sock,"A04+ERROR")
        send_msg(sock,"No Unread Message!")
    else :
        send_msg(sock,"A04+SUCCESS")
        send_msg(sock,str(rows))




def clearGPThistory(cursor,sock,userid,data,db_conn):
    source = data
    ct = dt.datetime.now() 
    # 需要清除GPT之前留存的所有聊天记录
    cmd = '''
    UPDATE message 
    SET via = ?
    WHERE initial = ? 
    AND terminal = ?
    AND datetime < ?
    '''
    cursor.execute(cmd,("release",source,userid,ct))
    db_conn.commit() 
    cursor.execute(cmd,("release",userid,source,ct))
    db_conn.commit() 
    send_msg(sock,"A05+SUCCESS")
    send_msg(sock,"You cleared the chat history!")




def findclientsockbyuserid_(user_id, current_online):
    result = next((info_dict["client_sock"] for info_dict in current_online if info_dict["user_id"] == user_id), None)
    if result:
        return result
    else:
        print(f"User with user_id {user_id} not found")
        return None



def servertransferaudio(sock,userid,data):
    target = data 
    target_sock = findclientsockbyuserid_(target,current_online)
    if target_sock is None:
        send_msg(sock,"VC2+ERROR")
        return 

    send_msg(sock,"VC2+START") # start !
    while True:
        msg = recv_msg_unblock(sock)
        if msg is None :
            continue 
        if msg[0:4] == "VC3+":
            break 
    msg = msg + "||-||" + userid
    send_msg(target_sock,msg)

    sock_id , _ = sock.getpeername() 
    targetid , _ = target_sock.getpeername() 
    msg1 = "IPST" + str(sock_id)
    msg2 = "IPST" + str(targetid)
    time.sleep(0.2)
    print(msg2)
    send_msg(sock,msg2)
    print(msg1)
    send_msg(target_sock,msg1)


def sendip(sock):
    ip_dict = {}
    for item in current_online:
        ip_dict[item["user_id"]] = item["client_sock"].getpeername()[0] 
        # print(ip_dict)
    send_msg(sock,str(ip_dict))

def loaduserinfo(cursor,sock,userid):
    # userid = data 
    cmd = '''
    SELECT id, nickname, password 
    FROM user
    WHERE id  = ?
    '''
    cursor.execute(cmd,(userid,))
    rows = cursor.fetchall() 
    send_msg(sock,str(rows))
    return 

def getalllist(cursor,sock,userid):
    friends = getfriendslist_(cursor,sock,userid)
    groups = askgroup_(cursor,sock,userid)
    res_dict = {"friends":friends,"groups":groups}
    send_msg(sock,str(res_dict))
    return len(res_dict["friends"]), len(res_dict["groups"])

def getalllist_(cursor,sock,userid):
    friends = getfriendslist_(cursor,sock,userid)
    groups = askgroup_(cursor,sock,userid)
    res_dict = {"friends":friends,"groups":groups}
    # send_msg(sock,str(res_dict))
    return  res_dict

def friendupdatedetector(cursor,sock,userid,friendcount,groupcount):
    friends = getfriendslist_(cursor,sock,userid)
    groups = askgroup_(cursor,sock,userid)
    if len(friends) != friendcount:
        send_msg(sock,"F30+UPDATE")
        return len(friends), len(groups)
    if len(groups) != groupcount:
        send_msg(sock,"F30+UPDATE")
        return len(friends), len(groups)
    send_msg(sock,"F30+STAY")
    return len(friends), len(groups)


def pullallfriendinfo(cursor,sock,userid,data,db_conn):
    source = data # 查询一个人的所有历史信息，文件也被认为所信息，用于在登录时更新人的信息
    chat_info = getpreviousmessage_(cursor,sock,userid,source,db_conn)
    chat_info = [t + ("False",) for t in chat_info]
    file_info = getpreviousfile_(cursor,sock,userid,source,"chatfile",db_conn)
    file_info = [t + ("True",) for t in file_info]
    audio_info = getpreviousfile_(cursor,sock,userid,source,"audiofile",db_conn)
    audio_info = [t + ("True",) for t in audio_info]
    res = chat_info + file_info + audio_info 
    sorted_res = sorted(res, key=lambda x: x[4], reverse=True)
    print(sorted_res)
    send_msg(sock,str(sorted_res))


def pullallgroupinfo(cursor,sock,userid,data,db_conn):
    source = data 
    chat_info = getgrouppreviousmessage_(cursor,sock,userid,source,db_conn,)
    chat_info = [t + ("False",) for t in chat_info]
    file_info = getpreiviousgroupfile_(cursor,sock,userid,source,"groupchatfile",db_conn)
    file_info = [t + ("True",) for t in file_info]
    audio_info = getpreiviousgroupfile_(cursor,sock,userid,source,"groupaudiofile",db_conn)
    audio_info = [t + ("True",) for t in audio_info]
    res = chat_info + file_info + audio_info 
    sorted_res = sorted(res, key=lambda x: x[4], reverse=True)
    send_msg(sock,str(sorted_res))
    # send_msg(sock,str(sorted_res))



def updatedetector(cursor,sock,userid):
    friend_group_dict = getalllist_(cursor,sock,userid) 
    print(friend_group_dict)
    update_list1 = []
    friend_list = friend_group_dict["friends"] + ["Customized GPT","Little OP","Crazy Dave"] 
    group_list = friend_group_dict["groups"]
    for item in friend_list:
        cmd = '''
        SELECT initial, via, terminal, content, datetime FROM message
        WHERE
        (
        type = ?
        AND unreadflag = ?
        AND initial = ?
        AND terminal = ?)
        OR
        
        (type = ?
        AND unreadflag = ?
        AND initial = ?
        AND terminal = ?
        )
        ORDER BY datetime ASC
        '''
        cursor.execute(cmd,("chatto","activate",item,userid,"chatfrom","activate",userid,item))
        rows = cursor.fetchall()
        l1 = len(rows)
        cmd = '''
        SELECT originalname,storagename
        FROM file 
        WHERE (initial = ?
        AND via = ?
        AND terminal = ?
        AND type LIKE  ?
        AND status = ?)
        OR
        (
        initial = ?
        AND via = ?
        AND terminal = ?
        AND type LIKE  ?
        AND status = ?
        )
        '''
        cursor.execute(cmd,(item,"none",userid,"%to","activate",userid,"none",item,"%from","activate"))
        rows = cursor.fetchall() 
        l2 = len(rows)
        if l1 >0 or l2 > 0 :
            update_list1.append(item)
        
    update_list2 = []
    for item in group_list:
        cmd = '''
        SELECT initial, content FROM message
        WHERE
        via = ?
        AND type = ?
        AND unreadflag = ?
        AND terminal = ?
        '''
        cursor.execute(cmd,(item,"chat","activate",userid))
        rows = cursor.fetchall()
        print(rows)
        l1 = len(rows)
        cmd = '''
        SELECT originalname,storagename
        FROM file 
        WHERE 
        via = ?
        AND terminal = ?
        AND status = ?

        '''
        cursor.execute(cmd,(item,userid,"activate"))
        rows = cursor.fetchall() 
        l2 = len(rows)
        if l1 >0 or l2 >0 :
            update_list2.append(item)
    info_dict = {"friends":update_list1,"groups":update_list2}
    send_msg(sock,str(info_dict))
    return 

def pullnewfriendinfo(cursor,sock,userid,data,db_conn):
    source = data # 查询一个人的所有历史信息，文件也被认为所信息，用于在登录时更新人的信息
    chat_info = getnewmessage_(cursor,sock,userid,source,db_conn)
    chat_info = [t + ("False",) for t in chat_info]
    file_info = getnewfile_(cursor,sock,userid,source,"chatfile",db_conn)
    file_info = [t + ("True",) for t in file_info]
    audio_info = getnewfile_(cursor,sock,userid,source,"audiofile",db_conn)
    audio_info = [t + ("True",) for t in audio_info]
    res = chat_info + file_info + audio_info 
    sorted_res = sorted(res, key=lambda x: x[4], reverse=True)
    print(sorted_res)
    send_msg(sock,str(sorted_res))

def pullnewgroupinfo(cursor,sock,userid,data,db_conn):
    source = data 
    chat_info = getgroupnewmessage_(cursor,sock,userid,source,db_conn,)
    chat_info = [t + ("False",) for t in chat_info]
    file_info = getnewgroupfile_(cursor,sock,userid,source,"groupchatfile",db_conn)
    file_info = [t + ("True",) for t in file_info]
    audio_info = getnewgroupfile_(cursor,sock,userid,source,"groupaudiofile",db_conn)
    audio_info = [t + ("True",) for t in audio_info]
    res = chat_info + file_info + audio_info 
    sorted_res = sorted(res, key=lambda x: x[4], reverse=True)
    send_msg(sock,str(sorted_res))


# def pullallgroupinfo():

def deletefriend(cursor,sock,userid,data,db_conn):
    target = data 
    cmd = '''
    SELECT * FROM friendrelation 
    WHERE (user1 = ? AND user2 = ?) OR
    (user2 = ? AND user1 = ?)
    '''
    cursor.execute(cmd,(userid,target,userid,target))
    rows = cursor.fetchall() 
    if len(rows) == 0:
        # send_msg(sock,"F06+ERROR")
        return 
    cmd = '''
    DELETE FROM friendrelation
    WHERE (user1 = ? AND user2 = ?) OR 
    (user2 = ? AND user1 = ?)
    '''
    cursor.execute(cmd,(userid,target,userid,target))
    db_conn.commit() 


def leavegroup(cursor,sock,userid,data,db_conn):
    target = data 
    cmd = '''
    SELECT * FROM grouprelation
    WHERE groupid = ? AND userid = ?
    '''
    cursor.execute(cmd,(target,userid))
    rows = cursor.fetchall() 
    if len(rows) == 0:
        return 
    cmd = '''
    DELETE FROM grouprelation
    WHERE groupid = ? AND userid = ?
    '''
    cursor.execute(cmd,(target,userid))
    print(target,userid)
    db_conn.commit() 
    # print("LEAVED")


def serverrecieveAvatar(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    target = data[0] 
    address = data[1]
    ftype = data[2]
    originname = os.path.basename(address)
    savename = str(getfilecount_(cursor)) +"-" + originname 
    savepath = FILE_PATH + savename

        # send_msg(sock,"T01+CONTINUE")
    # cnt = 0 

    current_time = dt.datetime.now() 
    current_time = str(current_time)
    
    cmd ='''
        UPDATE file
        SET status = ? 
        WHERE terminal = ?
        AND type = ?
        AND datetime < ?
    '''
    cursor.execute(cmd,('release',userid,"avatar",current_time))
    db_conn.commit()
    
    with open(savepath,"wb") as file :
        while True :
            file_chunk = recv_file(sock)  # recieve a chunk
            if not file_chunk:
                break
            file.write(file_chunk)
            # print("recieving...")

    cmd = '''
    INSERT INTO file(originalname,storagename,initial,via,terminal,type,status,datetime)
    VALUES(?,?,?,?,?,?,?,?)
    '''
    current_time = dt.datetime.now() 
    current_time = str(current_time)
    cursor.execute(cmd,(originname,savename,"none","none",userid,ftype,"activate",current_time)) 
    db_conn.commit()    
    # send_msg(sock,"T20+SUCCESS")

def askavatar(cursor,sock):
    cmd = '''
    SELECT id FROM user
    '''
    cursor.execute(cmd)
    rows = cursor.fetchall() 
    res = [] 
    for row in rows :
        res.append(row[0])
    cmd = '''
    SELECT id FROM usergroup 
    '''    
    rows = cursor.fetchall() 
    # res = [] 
    for row in rows :
        res.append(row[0])
    
    avatar_dic = {}
    for item in res :
        cmd = '''
        SELECT storagename FROM file 
        WHERE initial = ? AND via = ? AND terminal = ? AND type = ? AND status = ?
        '''
        cursor.execute(cmd,("none","none",item,"avatar","activate",))

        res = cursor.fetchall()
        if len(res) > 0:
            avatar_dic[item] = res 
        # else :
            # avatar_dic["item"] = "none"

    send_msg(sock,str(avatar_dic))


def modifyinfo(cursor,sock,userid,data,db_conn):
    data = data.split("||-||")
    oldpass = data[0] 
    cmd = '''
    SELECT password FROM user 
    WHERE id = ?
    '''
    cursor.execute(cmd,(userid,))
    res = cursor.fetchall()[0][0]
    if oldpass != res:
        send_msg(sock,"U10+ERROR")
        return 
    nickname = data[1] 
    password = data[2] 
    cmd = '''
    UPDATE user
    SET nickname = ?, password = ?
    WHERE id = ?
    '''
    cursor.execute(cmd,(nickname,password,userid))
    db_conn.commit() 
    send_msg(sock,"U10+SUCCESS")


def getformatgroupinfo(cursor,sock,userid,data,db_conn):
    group = data 
    cmd = '''
    SELECT master FROM usergroup 
    WHERE id = ? 
    '''
    cursor.execute(cmd,(group,))
    master = cursor.fetchall()[0][0] 
    managers = getgroupmanager_(cursor,sock,group)
    members = getgroupmember_(cursor,sock,group)
    info_list = [] 
    for member in members:
        info_dict = {}
        if member == master:
            info_dict["isBoss"] = True 
        else :
            info_dict["isBoss"] = False 

        if member in managers:
            info_dict["isManager"] = True
        else :
            info_dict["isManager"] = False 
        
        info_dict["name"] = member 
        info_list.append(info_dict)
    # send_msg(sock,master)
    # time.sleep(0.1)
    # send_msg(sock,managers)
    # time.sleep(0.1)
    send_msg(sock,str(info_list))

    
def getformatgrouprequest(cursor,sock,userid,data,db_conn):
    group = data 
    ct = dt.datetime.now()
    ct = str(ct)
    cmd = '''
    SELECT initial,via,unreadflag,datetime FROM message
    WHERE via = ?
    AND terminal = ?
    AND datetime < ?
    AND type = ?
    '''
    cursor.execute(cmd,(group,userid,ct,"grouprq"))
    rows = cursor.fetchall() 
    info_list = [] 
    for row in rows :
        info_dict = {} 
        info_dict["name"] = row[0] 
        info_dict["dateTime"] = row[3]
        if row[2] == "activate":
            info_dict["isSolved"] = False 
        else :
            info_dict["isSolved"] = True 
        
        if row[2] == "accept":
            info_dict["isAccepted"] =  True
        else :
            info_dict["isAccepted"] = False 

        info_list.append(info_dict)
    send_msg(sock,str(info_list))


def addgroupmanager(cursor,sock,data,db_conn):
    data = data.split("||-||")
    group = data[0] 
    user = data[1] 
    cmd = '''
    INSERT INTO groupmanager (groupid,userid)
    VALUES(?,?)
    '''
    cursor.execute(cmd,(group,user))
    db_conn.commit() 


def deletegroupmanager(cursor,sock,data,db_conn):
    data = data.split("||-||")
    group = data[0] 
    user = data[1] 
    cmd = '''
    DELETE FROM groupmanager 
    WHERE groupid = ? AND userid = ?  
    '''
    cursor.execute(cmd,(group,user))
    db_conn.commit() 


def invitefriendintogroup(cursor,sock,data,db_conn):
    data = data.split("||-||")
    group = data[0] 
    user = data[1] 
    cmd = '''
    INSERT INTO grouprelation (groupid,userid)
    VALUES(?,?)
    '''
    cursor.execute(cmd,(group,user,))
    db_conn.commit() 


def get_all(cursor,sock):
    cmd = '''
    SELECT id FROM user
    '''
    cursor.execute(cmd)
    rows = cursor.fetchall() 
    user_list = [] 
    for row in rows:
        user_list.append(row[0])
    cmd = '''
    SELECT id FROM usergroup
    '''
    cursor.execute(cmd)
    rows = cursor.fetchall() 
    group_list = [] 
    for row in rows:
        group_list.append(row[0])
        info_dict = {}
    info_dict["friends"] = user_list
    info_dict["groups"] = group_list 
    send_msg(sock,str(info_dict))




def handle_client(client_sock): # callback function, all functions of our app should start from here 
    
    user_id = None
    print("Start a new thread!")

    global current_online

    myGPT = ChatManager(api_key=openai.api_key,persona= None)

    db_conn = sqlite3.connect(DB_PATH,timeout = 20)
    
    cursor = db_conn.cursor()
    # cursor.execute("PRAGMA journal_mode=WAL")

    
    FriendCount = 0 
    GroupCount = 0

    while True:
        data = recv_msg(client_sock)
        print(data)

        

        if data is None:  # 如果data为None，说明客户端已经关闭，退出循环
            print("Client has closed the connection.")

            # global users_data
            # print(user_key)
            # print(users_data)
            # index_to_update = users_data[users_data["key"] == user_key].index[0]
            # if index_to_update >= 0:
            #     users_data.loc[index_to_update, "status"] = "offline"

            # global current_online
            current_online = [d for d in current_online if d.get('user_key') != user_id]
            # send_msg(client_sock, "LOGIN Success!")
            # print(users_data)
            # users_data.to_csv("users.csv", index=False)
            break

        flag_bits = data[0:4]
        data = data[4:]
        


        if flag_bits == "L00+": #signup 
            signup(cursor,client_sock,data,db_conn)

        elif flag_bits == "L01+": #login
            user_id = login(cursor,client_sock,data,db_conn)
            info_dict = {"user_id":user_id,"client_sock":client_sock}
            current_online.append(info_dict)
        
        elif flag_bits == "R01+":
            user_id = checkfacelogin(cursor,client_sock,data,db_conn)
            info_dict = {"user_id":user_id,"client_sock":client_sock}
            current_online.append(info_dict)

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
            
            if flag_bits == "G03+":
                setgroupmanager(cursor,client_sock,user_id,data,db_conn)
            
            if flag_bits == "G07+":
                manageradduser(cursor,client_sock,user_id,data,db_conn)
            
            if flag_bits == "G08+":
                managerremoveuser(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "G04+":
                addgrouprequest(cursor,client_sock,user_id,data,db_conn)
            
            if flag_bits == "G06+":
                dealwithgrouprequest(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "G10+":
                getpreviousgrouprequest(cursor,client_sock,user_id)

            if flag_bits == "G11+":
                getunreadgrouprequest(cursor,client_sock,user_id)

            if flag_bits == "T04+":
                serverrecievegroupfile(cursor,client_sock,user_id,data,db_conn)
            
            if flag_bits == "T05+":
                getpreviousgroupfile(cursor,client_sock,user_id,data,db_conn)
            
            if flag_bits == "T06+":
                getnewgroupfile(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "A00+":
                changeGPTpersona(cursor,client_sock,data,user_id,db_conn)

            if flag_bits == "A01+":
                readGPTpersona(client_sock,user_id)
            
            if flag_bits == "A02+":
                sendGPTmessage(cursor,client_sock,data,user_id,db_conn,myGPT)
            
            if flag_bits == "A03+":
                getpreviousGPTmessage(cursor,client_sock,user_id,data,db_conn)
            
            if flag_bits == "A04+":
                getunreadGPTmessage(cursor,client_sock,user_id,data,db_conn)
            
            if flag_bits == "A05+":
                clearGPThistory(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "R00+":
                setpatternface(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "T08+":
                serversendaudiofile(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "VC2+" :
                servertransferaudio(client_sock,user_id,data)

            if flag_bits == "U00+":
                loaduserinfo(cursor,client_sock,user_id)
            
            if flag_bits == "U01+":
                FriendCount, GroupCount = getalllist(cursor,client_sock,user_id)

            if flag_bits == "U02+":
                pullallfriendinfo(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "U03+":
                pullallgroupinfo(cursor,client_sock,user_id,data,db_conn)
            
            if flag_bits == "U04+":
                updatedetector(cursor,client_sock,user_id)

            if flag_bits == "U05+":
                pullnewfriendinfo(cursor,client_sock,user_id,data,db_conn)
            
            if flag_bits == "U06+":
                pullnewgroupinfo(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "F06+":
                deletefriend(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "G41+":
                leavegroup(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "T20+":
                serverrecieveAvatar(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "T21+":
                askavatar(cursor,client_sock)

            if flag_bits == "U10+":
                modifyinfo(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "F30+":
                FriendCount, GroupCount = friendupdatedetector(cursor,client_sock,user_id,FriendCount,GroupCount)

            if flag_bits == "G20+":
                getformatgroupinfo(cursor,client_sock,user_id,data,db_conn)
            
            if flag_bits == "G21+":
                getformatgrouprequest(cursor,client_sock,user_id,data,db_conn)

            if flag_bits == "U99+":
                get_all(cursor,client_sock)

            if flag_bits == "G22+":
                addgroupmanager(cursor,client_sock,data,db_conn)
            
            if flag_bits == "G23+":
                deletegroupmanager(cursor,client_sock,data,db_conn)

            if flag_bits == "G24+":
                invitefriendintogroup(cursor,client_sock,data,db_conn)

            if flag_bits == "IPGT":
                sendip(client_sock)


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



        


        db_conn.commit()
        time.sleep(0.01)

    client_sock.close()



def main():

    # detect_thread = threading.Thread(target=message_update_detector, args=(0,))
    # detect_thread.daemon = True
    # detect_thread.start()


    SERVER_IP = "0.0.0.0"
    SERVER_PORT = 12345

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
