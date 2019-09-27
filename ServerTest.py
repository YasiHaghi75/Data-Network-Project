import socket
import ast
import math
import time
import random

DrpMsg = 0
class NeighbourMsg:
    def __init__(self,msgType,Reply,SrcUid,DestUid):
        self.msgType = msgType
        self.Reply = Reply
        self.SrcUid = SrcUid
        self.DestUid= DestUid

class NodeReg:
    def __init__(self,msgType,nodereg):
        self.msgType = msgType
        self.nodereg = nodereg

class DropMsg:
    def __init__(self,msgType):
        self.msgType = msgType


def Sendposibility(x1,y1,x2,y2,d):
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
     if dist>d:
         return 0
     else:
         return 1

def Dist(SrcUid,DestUid,mylist,d):
    for i in mylist:
        if i['Uid'] == SrcUid :
            x1 = i['LocX']
            y1 = i['LocY']
        elif i['Uid'] == DestUid :
            x2 = i['LocX']
            y2 = i['LocY']
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    if dist>d:
        return 0
    else:
        return 1




def FindAddr(uid,mylist):
    for i in mylist:
        if i['Uid'] == uid :
            return i['address']

def send(SSock,msg,desAdd):
    Messagee =str(msg)
    SSock.sendto(str.encode(Messagee), desAdd)

node_data = []
ip   = '127.0.0.1'
port = 6789
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSock.bind((ip , port))
da, addr =  serverSock.recvfrom(2048*128)
d = int(da.decode())

while True:
    data, addr = serverSock.recvfrom(2048*128)
    mydata = ast.literal_eval(data.decode('utf-8'))
    if mydata['msgType'] == 'reg':
        wait = 0
        del mydata['msgType']
        mydata.update([('address', addr)])
        node_data.append(mydata)
        Src_Uid = mydata['Uid']
        Src_x = mydata['LocX']
        Src_y = mydata['LocY']
        for i in node_data:
            if Sendposibility(Src_x,Src_y,i['LocX'],i['LocY'],d) :
                if Src_Uid != i['Uid']:
                    mymessage = NeighbourMsg('neighbour',1,Src_Uid,i['address'])
                    wait = wait+i['Delay']
                    send(serverSock,mymessage.__dict__,i['address'])

        time.sleep(wait)
        send(serverSock,"1",('127.0.0.6',1234))
    elif mydata['msgType'] == 'ChgLoc':
        node_data=[]
    else:

        P = random.uniform(0,1)
        thresh = 0

        if Dist(mydata['SrcUid'],mydata['DestUid'],node_data,d) :
            if mydata['msgType'] != 'neighbour':
                if P > thresh :
                    send(serverSock,mydata,FindAddr(mydata['DestUid'],node_data))

                else:
                    DrpMsg = DrpMsg + 1
                    dmsg = DropMsg('msgDrop')
                    send(serverSock,dmsg.__dict__,FindAddr(mydata['SrcUid'],node_data))

            else:
                send(serverSock,mydata,FindAddr(mydata['DestUid'],node_data))





