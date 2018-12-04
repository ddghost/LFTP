#coding=utf-8
import socket 
import struct
import receiver
import sender
import dataSolver
import os
import time

from multiprocessing import Process , Queue

dataMaxSize = 1024
recv_port = 13001
supportPortNum = 2
avialablePort = Queue()


def getNewPort():
    global avialablePort
    if avialablePort.empty():
        print 'there is no avialablePort'
        return -1
    else:
        return avialablePort.get()

def solveSendCommand(avialablePort , newPort , addr , fileName , fileSize):
    sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
    sk.bind(("" , newPort)) 
    #sk.settimeout(5)
    data,addr = sk.recvfrom(dataMaxSize) 
    recvDataHead , recvDataContent = dataSolver.splitData(data)
    if recvDataHead['ack']:
        receiver.recvSendFile(sk , addr , fileName , fileSize)
    sk.close()
    avialablePort.put(newPort)

def solveGetCommand(avialablePort , newPort , addr , fileName , fileSize):
    sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
    sk.bind(("",newPort)) 
    #sk.settimeout(5)
    data,addr = sk.recvfrom(dataMaxSize) 
    recvDataHead , recvDataContent = dataSolver.splitData(data)
    if recvDataHead['ack']:
        sender.sendFile( sk , addr , fileName , fileSize)
    sk.close()
    avialablePort.put(newPort)

if __name__ == "__main__":
    #13002 13003
    for i in range(1,supportPortNum+1):
        avialablePort.put(recv_port + i)
    recvSk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
    #从给定的端口，从任何发送者，接收UDP数据报 
    recvSk.bind(("",recv_port)) 
    print 'waiting on port:',recv_port
    while True:
        #接收一个数据报(最大到1024字节) 
        
        data,addr = recvSk.recvfrom(dataMaxSize) 
        print 'addr ' , addr

        recvDataHead , recvDataContent = dataSolver.splitData(data)

        if recvDataHead['send'] == True and recvDataHead['syn'] == True: 
            fileSize , fileName  = dataSolver.unPackFileNameAndSize(recvDataContent)
            print 'command is send , file is ' , fileName , ' size is ' , fileSize
            synAckContent = dataSolver.packTheHeader(dataSolver.getSendSynAckHeader() )
            newPort = getNewPort()
            if newPort != -1:
                newProcess = Process(target=solveSendCommand, 
                                            args=(avialablePort,newPort,addr,fileName,fileSize,) )
                newProcess.start() 
                time.sleep(0.5)
            newPortStr = struct.pack('i' , newPort)
            recvSk.sendto(synAckContent + newPortStr, addr)

        elif recvDataHead['send'] != True and recvDataHead['syn'] == True: 
            fileName = recvDataContent 
            try:
                fileSize = os.path.getsize(fileName)
            except:
                fileSize = -1
                print 'file not exit , stop to send file'

            print 'command is get , file is ' , fileName 
            synAckContent = dataSolver.packTheHeader(dataSolver.getRecvSynAckHeader() )
            newPort = getNewPort()
            if newPort != -1: 
                #this file is not exit
                if fileSize >= 0:
                    newProcess = Process(target=solveGetCommand, 
                                                args=(avialablePort,newPort,addr,fileName,fileSize,) )
                    newProcess.start()
                    time.sleep(0.5)
                else:
                    avialablePort.put(newPort)
            newPortStr = struct.pack('ii' , newPort , fileSize)
            recvSk.sendto(synAckContent + newPortStr, addr)
        else:
            print 'the pack is not the send command or get command'
