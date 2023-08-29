import socket
import time
import threading  # 导入线程模块
import os 
import cv2 
import sounddevice as sd
import soundfile as sf
import keyboard
import time
import numpy as np 
import speech_recognition as sr
import pyaudio 


pause_event = threading.Event()
FILE_PATH = "./filerecieving/"
FACE_PATH = "E:/2023-2024 # 1(now)/test/test/"
FACE_UPLOAD_FLAG = 0
REAL_TIME_FLAG = 0
SEND_IP = ""




def send_msg(sock, msg):
    # 将消息编码为字节流
    msg = msg.encode('utf-8')
    # 创建固定长度的消息头，例如4个字节，包含消息长度
    msg_header = f"{len(msg):<4}".encode('utf-8')
    # 发送消息头和消息主体
    sock.sendall(msg_header + msg)


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
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



def send_file(sock, file_chunk):
    # 发送文件块大小
    header = f"{len(file_chunk):<4}"
    sock.sendall(header.encode('utf-8'))

    # 发送文件块
    sock.sendall(file_chunk)

def recv_file(sock):
    try:
        # 设置套接字超时为10秒
        sock.settimeout(0.2)

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



def receive_messages(client_sock):
    global FACE_UPLOAD_FLAG
    global REAL_TIME_FLAG
    global SEND_IP
    while True:
        # event.wait()  # 使得我们可以打断这个进程
        server_reply = recv_msg(client_sock)
        print(server_reply)
        if server_reply == None :
            continue 
        flag_bit = server_reply[0:4]
        
        if flag_bit =="T03+" and server_reply != "T03+ERROR" and server_reply !="T03+SUCCESS":
            clientrecievefile(client_sock,server_reply)
            
        if flag_bit =="T08+" and server_reply != "T08+ERROR" and server_reply !="T08+SUCCESS":
            clientrecieveaudio(client_sock,server_reply)
            
        elif server_reply == "T10+SUCCESS":
            FACE_UPLOAD_FLAG = 0
        
        elif server_reply == "VC2+START":
            REAL_TIME_FLAG = 1
        
        elif server_reply == "VC2+ERROR":
            REAL_TIME_FLAG = -1
        
        elif flag_bit == "VC3+":
            voicerealtime_terminal(client_sock,server_reply)
            # print("hihihi")
            # audio_thread = threading.Thread(target=voicerealtime_terminal, args=(client_sock,server_reply))
            # audio_thread.start()
        
        elif flag_bit == "VC4+":
            REAL_TIME_FLAG = 0  # 停止语音
            
        elif flag_bit == "IPST":
            SEND_IP = str(server_reply[4:])
            print(SEND_IP)
                        


def send_messages(client_sock):
    while True:
        msg_to_send = input()
        flag_bit = msg_to_send[0:4]

        if msg_to_send:
            if flag_bit == "T02+":
                clientsendfile(client_sock,msg_to_send)
            elif flag_bit == "T04+":
                clientsendfile(client_sock,msg_to_send)
            elif flag_bit == "R01+":
                checkfacepattern(client_sock,msg_to_send)
            elif flag_bit == "R00+":
                uploadfacepattern(client_sock,msg_to_send)
            elif flag_bit == "VC0+":
                voice2wordchat(client_sock,msg_to_send)
            elif flag_bit == "VG0+":
                voice2wordgroupchat(client_sock,msg_to_send)
            elif flag_bit == "VC1+" or flag_bit == "VG1+":
                voicechat(client_sock,msg_to_send)
            elif flag_bit == "VC2+":
                voicerealtime_initial(client_sock,msg_to_send)  # 主动唤起语音通话
                
            
            else :
                send_msg(client_sock, msg_to_send)






def clientsendfile(client_sock,msg_to_send):
    msg = msg_to_send[4:]
    msg = msg.split("||-||")
    target = msg[0] 
    address = msg[1]
    
    if not os.path.exists(address):
        print(f"File {address} does not exist!")  # client checks the file is or not exist 
        return
    # pause_event.clear()
    
    
    send_msg(client_sock,msg_to_send)

    with open(address,"rb") as file :
    
        file_chunk = file.read(4096*2)
        while file_chunk:
            send_file(client_sock,file_chunk)
            file_chunk = file.read(4096*2)
    # pause_event.set()
    
    

def clientsendface(client_sock,address):
    if not os.path.exists(address):
        print(f"File {address} does not exist!")  # client checks the file is or not exist 
        return

    with open(address,"rb") as file :
    
        file_chunk = file.read(4096*2)
        while file_chunk:
            send_file(client_sock,file_chunk)
            file_chunk = file.read(4096*2)
            # print("sending...")
    # pause_event.set()
    


def clientrecievefile(client_sock,data):
    data = data[4:]
    name = data 
    savepath = FILE_PATH 
    if not os.path.exists(savepath):
        while True :
            file_chunk = recv_file(client_sock)  # recieve a chunk
            if not file_chunk:
                file_chunk = ""
                break
        print(f"File {savepath} does not exist!")  # client checks the file is or not exist 
        return
    savepath = FILE_PATH + name 
    with open(savepath,"wb") as file :
        while True :
            file_chunk = recv_file(client_sock)  # recieve a chunk
            if not file_chunk:
                break
            file.write(file_chunk)
            # print("recieving...")
    print("Finish recieve file!")

def clientrecieveaudio(client_sock,data):
    data = data[4:]
    name = data 
    savepath = FILE_PATH 
    if not os.path.exists(savepath):
        while True :
            file_chunk = recv_file(client_sock)  # recieve a chunk
            if not file_chunk:
                file_chunk = ""
                break
        print(f"File {savepath} does not exist!")  # client checks the file is or not exist 
        return
    savepath = FILE_PATH + name 
    with open(savepath,"wb") as file :
        while True :
            file_chunk = recv_file(client_sock)  # recieve a chunk
            if not file_chunk:
                break
            file.write(file_chunk)



def CatchUsbVideo(window_name, camera_idx,userid,type,frames = 100):
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(camera_idx)
    while cap.isOpened():

    # 截取保存这一帧
        for i in range(frames):
        # 持续读取新帧
            ret, frame = cap.read()
        # 显示新帧 
            cv2.imshow(window_name, frame)
            cv2.waitKey(5)
            if (i+1)%10 == 0:
                img_name = userid + str(type)+ "-{}.jpg".format(int((i-9)/10))
                cv2.imwrite(os.path.join(FACE_PATH, img_name), frame)

        break
        


def uploadfacepattern(sock,data):
    # userid = data  # 待验证的用户ID ]
    
    # 读取相机的信息
    camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    ret, frame = camera.read()
    
    CatchUsbVideo("camera", 0,"pattern","facepattern")
    # 2秒后关闭窗口   
    camera.release()
    cv2.destroyAllWindows() 
    
    global FACE_UPLOAD_FLAG
    FACE_UPLOAD_FLAG = 0
    send_msg(sock,data)
    all_facefile_list = os.listdir(FACE_PATH)
    for item in all_facefile_list:
        while FACE_UPLOAD_FLAG == 1:
            pass # 直到标记消失，则上传另一张图
        if FACE_UPLOAD_FLAG == 0:
            FACE_UPLOAD_FLAG = 1
            clientsendface(sock,FACE_PATH + str(item))
    
    for item in all_facefile_list:
        full_path = os.path.join(FACE_PATH,item)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except:
                print("Delete Error!")
            
        

def checkfacepattern(sock,data):
    camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    ret, frame = camera.read()
    
    CatchUsbVideo("camera", 0,"check","facecheck")
    # 2秒后关闭窗口   
    camera.release()
    cv2.destroyAllWindows() 
    
    global FACE_UPLOAD_FLAG
    FACE_UPLOAD_FLAG = 0
    send_msg(sock,data)
    all_facefile_list = os.listdir(FACE_PATH)
    for item in all_facefile_list:
        while FACE_UPLOAD_FLAG == 1:
            pass # 直到标记消失，则上传另一张图
        if FACE_UPLOAD_FLAG == 0:
            FACE_UPLOAD_FLAG = 1
            clientsendface(sock,FACE_PATH + str(item))
            
            
    for item in all_facefile_list:
        full_path = os.path.join(FACE_PATH,item)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except:
                print("Delete Error!")
            
            

def voice2wordchat(sock,msg):
    target = msg[4:]

    sample_rate = 44100
    is_recording = False
    audio_data = []
    def callback(indata, frames, time, status):
        nonlocal audio_data
        audio_data.append(indata.copy())
    is_recording = True
    stream = sd.InputStream(callback=callback, channels=1, samplerate=sample_rate)
    stream.start()
    print("Press \"S\" Key to stop recording!")
    while True:
        user_input = input()
        if user_input == 'S':
            break
    is_recording = False
    stream.stop()
    stream.close()
    file_name = 'test.wav'
    audio_data = [data.flatten() for data in audio_data]
    audio_data = np.concatenate(audio_data)
    sf.write(file_name, audio_data, sample_rate)
    
    recognizer = sr.Recognizer()
    file_path = "test.wav"  # 音频文件路径
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)  # 从音频文件中读取音频数据
        try:
            text = recognizer.recognize_google(audio,language='zh-CN')  # 将语言设置为中文
            print("Text from audio: {}".format(text))
            str = "C00+"+target + "||-||" + text 
            send_msg(sock,str)
        except sr.UnknownValueError:
            print("Unable to recognize speech")
        except sr.RequestError as e:
            print("Error: {}".format(e))
    
    
    
def voice2wordgroupchat(sock,msg):
    target = msg[4:]

    sample_rate = 44100
    is_recording = False
    audio_data = []
    def callback(indata, frames, time, status):
        nonlocal audio_data
        audio_data.append(indata.copy())
    is_recording = True
    stream = sd.InputStream(callback=callback, channels=1, samplerate=sample_rate)
    stream.start()
    print("Press \"S\" Key to stop recording!")
    while True:
        user_input = input()
        if user_input == 'S':
            break
    is_recording = False
    stream.stop()
    stream.close()
    file_name = 'test.wav'
    audio_data = [data.flatten() for data in audio_data]
    audio_data = np.concatenate(audio_data)
    sf.write(file_name, audio_data, sample_rate)
    
    recognizer = sr.Recognizer()
    file_path = "test.wav"  # 音频文件路径
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)  # 从音频文件中读取音频数据
        try:
            text = recognizer.recognize_google(audio,language='zh-CN')  # 将语言设置为中文
            print("Text from audio: {}".format(text))
            str = "C03+"+target + "||-||" + text 
            send_msg(sock,str)
        except sr.UnknownValueError:
            print("Unable to recognize speech")
        except sr.RequestError as e:
            print("Error: {}".format(e))


    
def voicechat(client_sock,msg_to_send):
    target = msg_to_send[4:]

    sample_rate = 44100
    is_recording = False
    audio_data = []
    def callback(indata, frames, time, status):
        nonlocal audio_data
        audio_data.append(indata.copy())
    is_recording = True
    stream = sd.InputStream(callback=callback, channels=1, samplerate=sample_rate)
    stream.start()
    print("Press \"S\" Key to stop recording!")
    while True:
        user_input = input()
        if user_input == 'S':
            break
    is_recording = False
    stream.stop()
    stream.close()
    file_name = 'voiceaudio.wav'
    audio_data = [data.flatten() for data in audio_data]
    audio_data = np.concatenate(audio_data)
    sf.write(file_name, audio_data, sample_rate)
    
    if msg_to_send[0:4] == "VC1+":
        msg_str = "T02+" + target + "||-||" +"./voiceaudio.wav" + "||-||"+ "audiofile"
        clientsendfile(client_sock,msg_str)
    elif msg_to_send[0:4] == "VG1+":
        msg_str = "T04+" + target + "||-||" +"./voiceaudio.wav" + "||-||"+ "audiofile"
        clientsendfile(client_sock,msg_str)
    

         

def voicerealtime_initial(client_sock,msg_to_send):
    global REAL_TIME_FLAG 
    REAL_TIME_FLAG = 0
    send_msg(client_sock,msg_to_send)
    while REAL_TIME_FLAG == 0:
        pass 
    
    if REAL_TIME_FLAG == -1 :
        return 
    
    
    IP_ADD = "0.0.0.0"
    udp_socket_outgoing = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket_incoming = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    send_msg(client_sock,msg_to_send)  # 先说要语音通信
    
    udp_socket_outgoing.bind(("0.0.0.0", 0))
    udp_socket_incoming.bind(("0.0.0.0", 0))

    SEND_PORT = udp_socket_outgoing.getsockname()[1]
    RECV_PORT = udp_socket_incoming.getsockname()[1]  
    
    print(SEND_PORT,RECV_PORT)  
    
    STR = "VC3+" + str(SEND_PORT) + "||-||" + str(RECV_PORT)
    send_msg(client_sock,STR)
    
    # hostname = socket.gethostname()
    # local_ip = socket.gethostbyname(hostname)
    # send_msg(client_sock,"SETIP"+str(local_ip))
    
    chunk_size = 512
    audio_format = pyaudio.paInt16
    channels = 1
    rate = 10000
    p = pyaudio.PyAudio()
    playing_stream = p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                          frames_per_buffer=chunk_size)
    recording_stream = p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                            frames_per_buffer=chunk_size)
    
    run_flag = 1
    
    time.sleep(1)
    print(SEND_IP)
    
    # 发送音频数据
    def send_audio():
        while run_flag and REAL_TIME_FLAG:
            data = recording_stream.read(chunk_size)
            udp_socket_outgoing.sendto(data, (SEND_IP, SEND_PORT+200))
            # print(data)


    # 接收音频数据
    # print(run_flag,REAL_TIME_FLAG)
    def receive_audio():
        while True:
            # print("hi")
            data, addr = udp_socket_incoming.recvfrom(4096)
            # print(RECV_PORT,addr[1])
            if addr[1] == RECV_PORT + 100 :
                playing_stream.write(data)
                # print(data)
            if run_flag == 0:
                # print("stop")
                break 
                return 
                
    send_thread = threading.Thread(target=send_audio,)
    receive_thread = threading.Thread(target=receive_audio, )
    
    send_thread.start() 
    receive_thread.start() 
    
    
    while True :
        
        s = input() 
        if s == "S":
            run_flag = 0
            REAL_TIME_FLAG = 0 
            break
        if run_flag == 0:
            break 
    
    REAL_TIME_FLAG = 0
    send_msg(client_sock,"STOP")
    print("STOP Chatting!")
    
    
    
def voicerealtime_terminal(client_sock,msg):
    global REAL_TIME_FLAG
    lock = threading.Lock()
    REAL_TIME_FLAG = 1 
    print(msg)
    msg = msg[4:]
    msg = msg.split("||-||")
    SEND_PORT = int(msg[0]) 
    RECV_PORT = int(msg[1]) 
    print(SEND_PORT,RECV_PORT)
    
    udp_socket_outgoing = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket_incoming = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    
    udp_socket_outgoing.bind(("0.0.0.0", RECV_PORT + 100))  # 发送在比对方高100
    udp_socket_incoming.bind(("0.0.0.0", SEND_PORT + 200))  #接受在比对方高200
    
    # hostname = socket.gethostname()
    # local_ip = socket.gethostbyname(hostname)
    # send_msg(client_sock,"SETIP"+str(local_ip))
    
    
    chunk_size = 512
    audio_format = pyaudio.paInt16
    channels = 1
    rate = 10000
    p = pyaudio.PyAudio()
    playing_stream = p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                          frames_per_buffer=chunk_size)
    recording_stream = p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                            frames_per_buffer=chunk_size)
    

    
    time.sleep(1)
    global SEND_IP 
    SEND_IP = recv_msg(client_sock)[4:]
    print(SEND_IP)
    run_flag = 1
    
    def send_audio():
        while run_flag and REAL_TIME_FLAG:
            data = recording_stream.read(chunk_size)
            udp_socket_outgoing.sendto(data, (SEND_IP, RECV_PORT))
            # print(SEND_IP)
            # print(data)


    # 接收音频数据
    # print(run_flag,REAL_TIME_FLAG)
    def receive_audio(): 
        while True:
            # print("hi")
            data, addr = udp_socket_incoming.recvfrom(4096)
            if addr[1] == SEND_PORT :
                playing_stream.write(data)
                # print(data)
            if run_flag == 0:
                # print("st/op")
                break 
                return 
                
    send_thread = threading.Thread(target=send_audio,)
    receive_thread = threading.Thread(target=receive_audio, )
    
    send_thread.start() 
    receive_thread.start() 
    
    # time.sleep(10)
    # run_flag = 0 
    
    while True :
        
        s = input() 
        if s == "S":
            run_flag = 0
            REAL_TIME_FLAG = 0 
            break
        if run_flag == 0:
            break 
        
    # send_thread.join() 
    # receive_thread.join() 
    
    REAL_TIME_FLAG = 0
    
    send_msg(client_sock,"STOP")

    
    print("STOP Chatting!")
    

    
def main():
    SERVER_IP = "192.168.43.4" 
    SERVER_PORT = 12345
    BUFFER_SIZE = 1024

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_sock.connect((SERVER_IP, SERVER_PORT))
    except socket.error as e:
        print("Connection failed! Error:", str(e))
        client_sock.close()
        exit()

    # 创建并启动一个线程来接收服务端消息
    
    # pause_event.set()
    recv_thread = threading.Thread(target=receive_messages, args=(client_sock,))
    recv_thread.daemon = True  # 设置为守护线程，这样当主线程退出时，接收线程也会退出
    recv_thread.start()

    send_thread = threading.Thread(target=send_messages, args=(client_sock,))
    send_thread.daemon = True
    send_thread.start()
    # pause_event.set() 

    while True:
        # 此处可以处理其他与用户交互的任务，如发送消息等
            
        pass  # 仅作为示例，不执行任何操作

    client_sock.close()

if __name__ == "__main__":
    main()
