
from socket import socket
import threading #run movazi
from extra import *
from datetime import datetime
import json
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib



print("\nThe server was successfully activated.\n")

#Server information

ip = '192.168.1.107'
port = 14200

#-------------------------------connection-------------------------------------------------------
class Socket:
    size = 4096 #Size of information sent and received
    user_info = ""

    def __init__(self, host="192.168.1.107", port=14200): #first run
        self.socket = socket() #socket.socket()
        self.socket.bind((host, port))
        self.socket.listen(1) #Open the port and wait for the new user

        while True:          # trade two function            #connect to client
            threading.Thread(target=self._wait_recv, args=self.socket.accept()).start() #2ta khorji conn,addr ghabli

    def _wait_recv(self, conn: socket, addr):#waiting for new messege or conect or diconnect
        data = b''#byte format
        while True:#wait for new message
            # try:
            d = conn.recv(self.size)
            data += d
            if len(d) < self.size:#for biger bytes
                if data:
                    d = data.split(b'\0')#get meeseges \0 hi ali\0 hello\0
                    for i in range(len(d) - 1):
                        self._recive_data(conn, decrypt(d[i]))#client,messeg sended
                    data = d[-1]#ali\0mohammad\0 bade \0 akhari ham mide msln bara kamel bodn payam
                else:
                    conn.close()#if client leave
            # except:
            #     del online_users[conn]
            #     print(online_users)


    #addres karbar = client 
    def _on_connect(self, client: socket):

        print(client,"start working with server")


    def _on_disconnect(self, client: socket):
        print(client,"disconnected")


    #dade haye daryafti ro bgir va client= yani ki in dade haro ferestade dar haghighat hamun 
    #conn hast
    def _recive_data(self, client: socket, data: bytes):
        x=(json.loads(data.decode()))
        print('done')
        task=x[0]
        work[f"{task}"](client,x[1:])
        
    # def send(client,ssdata):
    #     ssdata = json.dumps(ssdata)
    #     self.socket.send((ssdata.encode() + b'\0'))


    #client.send(#x["1"]())
    #close server
    def close(self):
        self.socket.close()

#---------------END----------------connection---------------------------END----------------------------




#-------------------------------FUNCTIONS------------------------------------------------------------------
#vaghti ye nafar sabte nam mikone bayad motmaeen beshim
#ghablan inja account nadashe age dash behesh begim ghablan sabte nam kardi ! 
def login_chek(s:socket,data):
    user_id=data[0]  #id_user khune 0 dade ersali ast 
    sock=s
    #peyda kardan karbar dar db
    connection = sqlite3.connect("./users.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    r = cursor.fetchall()
    connection.close()
    if r==[]:
        print("login_chek")
        send_email(s,data)
        print("login_chek")
    else:
        #sock.send(sock,"in data base ghablan vojud dashte")
        pass


#ersal mail baraye kasi ke faramush kade pass ash ra 
#ya baraye user jadid
def send_email(s:socket,data:list):
    print(data)
    emialaddress=data[2]
    
# setup the parameters of the message
    password = [97, 109, 105, 110, 109, 104, 102, 97]
    password=''.join(chr(i) for i in password)
    msg = MIMEMultipart()
    msg['From'] = "messenger.verify.py@gmail.com"
    #message
    msg['To'] = emialaddress
    msg['Subject'] = "Subscription"
    import random
    random_number=(random.randint(100000,1000000))
    
    message = (f"\nHi Dear {emialaddress}.\n\n\n welcome to pychat! your verify code is : {random_number} .")
    # add in the message body
    msg.attach(MIMEText(message, 'plain'))
    #create server
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    # Login Credentials for sending the mail
    server.login(msg['From'], password)
    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    data.append(random_number)
    
    #client_chek_mail(s,random_number)
    client_chek_mail(s,data)

    
#baad az ersal mail bayad be client khabr dade shavad ta 
#mail khod ra chek konad 

def client_chek_mail(s:socket,data):
    data=[int(500)]+data #email_verify
    data = json.dumps(data) #etelaat daryafti avalie + code random 
    s.send((data.encode() + b'\0'))




def add_new_user(s:socket,data: list):
    #ghab in tabe tabe chek kardan username farakhani mishavad 
    #agar chek kardan user name sahih bud in farakhani shavad 
    connection = sqlite3.connect("./users.db")
    cur = connection.cursor()
    cur.execute("INSERT INTO users VALUES (?,?,?,?)", (data[0], data[1], data[2], data[3]))
    connection.commit()
    connection.close()
    data1=[int(502),"welcome to pychat!"]
    data1 = json.dumps(data1)
    s.send((data1.encode() + b'\0'))
    print("new_user_added")


#darkhast karbar baraye sign in amsde ast
def sign_in_request(s:socket,data:list):
    user_id=data[0]
    print(user_id)
    
    connection = sqlite3.connect("./users.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    r = cursor.fetchall()
    connection.close()
    print(r)
    print(data[1])
    if r[0][0]==data[0] and r[0][3]==data[1]:
        data1=[int(502),"welcome to pychat!"]
        data1 = json.dumps(data1)
        s.send((data1.encode() + b'\0'))

    else :
        data1=[int(502),"oh! usernme/password is not correct "]
        data1 = json.dumps(data1)
        s.send((data1.encode() + b'\0'))



#ezafe kardan yek karbar jadid be afrad online va ferastan payam hayie
#ke dar zaman ofline budan shakhs digari baraye vey ersal karde

def adding_new_client_to_online(s:socket,data:list):
    #-------add to online------------------------------------------------------
    print('ye nafar jadid online shod')
    online=data[0]
    online_users.update({s:data[0]})
    print(online_users)
    #-----------start sending pm that recived when he/she was ofline------------

    connection = sqlite3.connect("./unsend.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM unsend WHERE reciver=?", (online,))
    r = cursor.fetchall()
    connection.close()
    if r!=[]:
        data=[int(503)]+r
        print("start sending unsend pm to user")
        data = json.dumps(data)
        s.send((data.encode() + b'\0'))
        print("sending pm finished")
    else:
        pass

def sending_messages(s:socket,data:list):
    print(data)
    for key, value in online_users.items(): 
        if data[0] == value: 
            data1=[int(503),(data[0],data[1],data[2],data[3],data[4])]
            data1 = json.dumps(data1)
            key.send((data1.encode() + b'\0'))
            connection = sqlite3.connect("./sent.db")
            cur = connection.cursor()
            cur.execute("INSERT INTO sent VALUES (?,?,?,?,?)", (data[0], data[1], data[2], data[3],data[4]))
            connection.commit()
            connection.close()
        else:
            connection = sqlite3.connect("./unsend.db")
            cur = connection.cursor()
            cur.execute("INSERT INTO unsend VALUES (?,?,?,?,?)", (data[0], data[1], data[2], data[3],data[4]))
            connection.commit()
            connection.close()







#-----------------------------------------END FUNC ------------------------------------------------------------





work={'100':login_chek,'101':send_email,'102':add_new_user,'103':sign_in_request,'105':adding_new_client_to_online,'106':sending_messages}
online_users={}
s=Socket(ip, port)#run socket init make object from socket

#s.send