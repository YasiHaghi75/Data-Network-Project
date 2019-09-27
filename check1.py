import threading
import socket
import time
import ast
id   = 0
ip   = '127.0.0.6'
port = 1234
mySock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mySock.bind((ip , port))

class vehicle(threading.Thread):

    def __init__(self,uid,ip,port,location_x,location_y,Delay,clientSock,neighbour,routeTable,lastMsg):
        threading.Thread.__init__(self)
        self.uid = uid
        self.ip = ip
        self.port = port
        self.location_x = location_x
        self.location_y = location_y
        self.Delay = Delay
        self.clientSock = clientSock
        self.neighbour = neighbour
        self.routeTabel = routeTable
        self.lastMsg = lastMsg

    def Send_Data(self , msg):
        UDP_IP_ADDRESS = '127.0.0.1'
        UDP_PORT_NO = 6789
        Messagee =str(msg)
        self.lastMsg = msg
        time.sleep(self.Delay)
        print("send %(uid)d %(msgType)s"% {"uid": self.uid, "msgType":msg['msgType']})
        self.clientSock.sendto(str.encode(Messagee), (UDP_IP_ADDRESS, UDP_PORT_NO))

    def Receive_Data(self):
        while True:
            data, addr = self.clientSock.recvfrom(1024*128)
            msg = ast.literal_eval(data.decode('utf-8'))
            print("recieve %(uid)d %(msgType)s"% {"uid": self.uid, "msgType":msg['msgType']})
            if msg['msgType'] == 'neighbour':
                self.neighbour.append(msg['SrcUid'])
                print("update %(uid)d NeighbourTabel"% {"uid": self.uid})
                if msg['Reply']:
                    mymessage = NeighbourMsg('neighbour',0,self.uid,msg['SrcUid'])
                    self.Send_Data(mymessage.__dict__)
            elif msg['msgType'] == 'myMsg':
                if self.uid == msg['realDestUid']:
                    print("Message Is Resvd" )
                else:
                    msg['DestUid'] = self.FindRoute(msg)
                    msg['SrcUid'] = self.uid
                    self.Send_Data(msg)
            elif msg['msgType'] == 'RRQ':
                msgdiscard = 1
                for i in self.routeTabel:
                    if msg['id'] == i['Id'] :
                        msgdiscard = 0

                if msgdiscard:
                    newroute = {'DestUid':msg['realSrcUid'] , 'NxHop':msg['SrcUid'] , 'Id':msg['id']}
                    self.routeTabel.append(newroute)
                    print("update %(uid)d RouteTabel"% {"uid": self.uid})
                    if self.FindRoute(msg):
                        newmsg = RouteMsg('RRP',msg['realDestUid'],msg['realSrcUid'],self.uid,None,msg['id'] + 50)
                        newmsg.DestUid=self.FindRoute(newmsg.__dict__)
                        self.Send_Data(newmsg.__dict__)
                    elif self.uid == msg['realDestUid']:
                        newmsg = RouteMsg('RRP',msg['realDestUid'],msg['realSrcUid'],self.uid,None,msg['id']+ 50)
                        newmsg.DestUid=self.FindRoute(newmsg.__dict__)
                        self.Send_Data(newmsg.__dict__)
                    else:
                        self.SendRRQ(msg,msg['id'])
            elif msg['msgType'] == 'RRP':
                newroute = {'DestUid':msg['realSrcUid'] , 'NxHop':msg['SrcUid'] , 'Id':msg['id']}
                self.routeTabel.append(newroute)
                print("update %(uid)d RouteTabel"% {"uid": self.uid})
                if self.uid == msg['realDestUid']:
                    self.clientSock.sendto(str.encode("1"), ('127.0.0.6',1234))
                else:
                    newmsg = RouteMsg('RRP',msg['realSrcUid'],msg['realDestUid'],self.uid,self.FindRoute(msg),msg['id'] + 50)
                    self.Send_Data(newmsg.__dict__)
            elif msg['msgType'] == 'msgDrop':
                    self.Send_Data(self.lastMsg)

    def FindRoute(self,msg):
        for i in self.routeTabel:
            if msg['realDestUid'] == i['DestUid'] :
                return i['NxHop']
        return 0

    def SendRRQ(self,msg,id):
        msgIsSent = 1
        if len(self.neighbour)==0:
            return
        newmsg = RouteMsg('RRQ',msg['realSrcUid'],msg['realDestUid'],self.uid,None,id)
        for i in self.neighbour:
            if msg['realDestUid'] == i:
                newmsg.DestUid= i
                self.Send_Data(newmsg.__dict__)
                msgIsSent = 0
                break
        if msgIsSent:
            for i in self.neighbour:
                newmsg.DestUid= i
                self.Send_Data(newmsg.__dict__)


    def set_func(self):
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientSock.bind((self.ip , self.port))
        threading.Thread(target=self.Receive_Data,args=()).start()


class RegMsg:
    def __init__(self,msgType,Uid,LocX,LocY,Delay):
        self.msgType = msgType
        self.Uid = Uid
        self.LocX = LocX
        self.LocY = LocY
        self.Delay = Delay

class NeighbourMsg:
    def __init__(self,msgType,Reply,SrcUid,DestUid):
        self.msgType = msgType
        self.Reply = Reply
        self.SrcUid = SrcUid
        self.DestUid = DestUid

class myMsg:
    def __init__(self,msgType,realSrcUid,realDestUid,SrcUid,DestUid):
        self.msgType = msgType
        self.realSrcUid = realSrcUid
        self.realDestUid = realDestUid
        self.SrcUid = SrcUid
        self.DestUid = DestUid

class RouteMsg:
    def __init__(self,msgType,realSrcUid,realDestUid,SrcUid,DestUid,id):
        self.msgType = msgType
        self.realSrcUid = realSrcUid
        self.realDestUid = realDestUid
        self.SrcUid = SrcUid
        self.DestUid = DestUid
        self.id = id

class ChgLocMsg:
    def __init__(self,msgType):
        self.msgType = msgType

def sendMessage(wait,node,Mid):
    id =Mid
    tBegin = time.time()
    while(time.time() - tBegin < wait):

        myipt = input("Enter Message To Send: SrcUid-message-DestUid ").split()
        ipt =myipt[1].split('-')
        mymessage = myMsg('myMsg',int(ipt[0]),int(ipt[2]),int(ipt[0]),None)
        if node[int(ipt[0])-1].FindRoute(mymessage.__dict__):
            mymessage.DestUid = node[int(ipt[0])-1].FindRoute(mymessage.__dict__)
            node[int(ipt[0])-1].Send_Data(mymessage.__dict__)
        else:
            id = id+1
            newroute = {'DestUid':0 , 'NxHop':0 , 'Id':id}
            node[int(ipt[0])-1].routeTabel.append(newroute)
            node[int(ipt[0])-1].SendRRQ(mymessage.__dict__,id)
            while True:
                data, addr = mySock.recvfrom(1024)
                break
            mymessage.DestUid = node[int(ipt[0])-1].FindRoute(mymessage.__dict__)
            node[int(ipt[0])-1].Send_Data(mymessage.__dict__)
    return 1

d = int(input("Enter Diameter : "))
mySock.sendto(str.encode(str(d)), ('127.0.0.1', 6789))
x = int(input("Enter Length Of Field : "))
y = int(input("Enter Width Of Field : "))
n = int(input("Enter Number Of Vehicles : "))
Nodes = []
#start_time = time.time()
for i in range(0 ,n ):
    UID,IP,Port,Location_X,Location_Y,Delay=input(" UID IP Port Location_X Location_Y Delay").split()
    myvehicle = vehicle(i+1,IP,int(Port),int(Location_X),int(Location_Y),float(Delay),None,[],[],None)
    Nodes.append(myvehicle)
    Nodes[i].start()
    Nodes[i].set_func()
    initMsg = RegMsg('reg',i+1,int(Location_X),int(Location_Y),float(Delay))
    Nodes[i].Send_Data(initMsg.__dict__)
    while True:
        data, addr = mySock.recvfrom(1024)
        break

wait =int(input("Enter Time To Wait: "))
while 1:
    if (sendMessage(wait,Nodes,id)):
        chgloc = input("Change Loc: " ).split()
        for i in range (1,len(chgloc)):
            newloc = chgloc[i].split('-')
            Nodes[int(newloc[0])-1].location_x = int(newloc[1])
            Nodes[int(newloc[0])-1].location_y = int(newloc[2])
        for i in range(0 ,n ):
            Nodes[i].neighbour = []
            Nodes[i].routeTabel= []
        chgmes = ChgLocMsg('ChgLoc')
        Messageloc =str(chgmes.__dict__)
        mySock.sendto(str.encode(Messageloc), ('127.0.0.1',6789))
        for i in range(0 ,n ):
            initMsg = RegMsg('reg',i+1,Nodes[i].location_x,Nodes[i].location_y,Nodes[i].location_y)
            Nodes[i].Send_Data(initMsg.__dict__)
            while True:
                data, addr = mySock.recvfrom(1024)
                break




