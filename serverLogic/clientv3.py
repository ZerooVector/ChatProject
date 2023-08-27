import socket
import time
import threading  # 导入线程模块
import os 
# pause_event = threading.Event()
FILE_PATH = "./filerecieving/"



def send_msg(sock, msg):
    # 将消息编码为字节流
    msg = msg.encode('utf-8')
    # 创建固定长度的消息头，例如4个字节，包含消息长度
    msg_header = f"{len(msg):<4}".encode('utf-8')
    # 发送消息头和消息主体
    sock.sendall(msg_header + msg)


def recv_msg(sock):
    sock.setblocking(True)
    msg_header = sock.recv(4).decode('utf-8').strip()
    
    # 检查消息头是否为空
    if not msg_header:
        print("Connection closed by the server")
        sock.close()
        return None

    
    msg_len = int(msg_header)
    # 根据消息头指定的长度接收消息主体
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


def receive_messages(client_sock):
    while True:
        # event.wait()
        server_reply = recv_msg(client_sock)
        print(server_reply)
        flag_bit = server_reply[0:4]
        if flag_bit =="T03+" and server_reply != "T03+ERROR" and server_reply !="T03+SUCCESS":
            clientrecievefile(client_sock,server_reply)

        # elif  server_reply is not None and len(server_reply)>0:
            
        #     print(server_reply)

def send_messages(client_sock):
    while True:
        msg_to_send = input()
        flag_bit = msg_to_send[0:4]

        if msg_to_send:
            if flag_bit == "T02+":
                clientsendfile(client_sock,msg_to_send)
            elif flag_bit == "T04+":
                clientsendfile(client_sock,msg_to_send)
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



def main():
    SERVER_IP = "127.0.0.1" 
    SERVER_PORT = 10020
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


    while True:
        # 此处可以处理其他与用户交互的任务，如发送消息等
            
        pass  # 仅作为示例，不执行任何操作

    client_sock.close()

if __name__ == "__main__":
    main()
