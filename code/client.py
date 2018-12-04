#coding=utf-8
import datetime
import sys
import sender
import socket
import dataSolver
import os
import struct
import receiver

send_port = 13001
dataMaxSize = 1024

    
def requestSend(addr , mylargefile , sk):
    #三次握手开始
    try:
        fileSize = os.path.getsize(mylargefile)
    except:
        print 'the send file is not exit , stop sending'
        return 
    fileSizeStr = struct.pack('i', fileSize)
    #send syn
    synHead = dataSolver.getSendSynHeader()
    synContent = dataSolver.packTheHeader(synHead)
    sk.sendto(synContent + fileSizeStr + mylargefile , addr)
    while(True):
        data , addr = sk.recvfrom(dataMaxSize)
        recvDataHead , recvDataContent = dataSolver.splitData(data)
        #get syn ack
        if recvDataHead['syn'] and recvDataHead['ack'] :
            newPort = struct.unpack('i' , recvDataContent)[0]
            addr = (sys.argv[2] , newPort)
            if newPort < 0:
                print 'no port available , stop'
                return 
            print 'new addr ' ,  addr
            #send ack
            ackHead = dataSolver.getSendAckHeader()
            ackContent = dataSolver.packTheHeader(ackHead)
            sk.sendto(ackContent , addr)
            break 
    #三次握手结束 ， 发送文件
    sender.sendFile( sk , addr , mylargefile , fileSize)

def requestGet(addr , mylargefile , sk):
    #三次握手开始
    #send syn
    synHead = dataSolver.getRecvSynHeader()
    synContent = dataSolver.packTheHeader(synHead)
    sk.sendto(synContent + mylargefile , addr)
    while(True):
        data , addr = sk.recvfrom(dataMaxSize)
        recvDataHead , recvDataContent = dataSolver.splitData(data)
        #get syn ack
        if recvDataHead['syn'] and recvDataHead['ack'] :
            portAndFileSize = struct.unpack('ii' , recvDataContent)
            newPort = portAndFileSize[0]
            fileSize = portAndFileSize[1]
            if newPort < 0:
                print 'no port available , stop'
                return 
            if fileSize < 0:
                print 'the file you want to get is not exit , stop requesting'
                return 
            addr = (sys.argv[2] , newPort)
            #send ack
            ackHead = dataSolver.getRecvAckHeader()
            ackContent = dataSolver.packTheHeader(ackHead)
            sk.sendto(ackContent , addr)
            break 
    #三次握手结束 ， 接受文件
    receiver.recvSendFile(sk , addr , mylargefile , fileSize)

if __name__ == "__main__":
    print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if len(sys.argv) != 4:
        print "the number of arguments must be 3, lget|lsend  myserver mylargefile"
    else:
        addr = (sys.argv[2] , send_port)
        mylargefile = sys.argv[3]
        sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        if sys.argv[1] == "lsend":
            requestSend(addr , mylargefile , sk)
        elif sys.argv[1] == "lget":
            requestGet(addr , mylargefile , sk)
        else:
            print 'first argument must be lget or lsend'
    print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')