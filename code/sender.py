#coding=utf-8
import json
import struct
import os
import socket
import time
import sys
import dataSolver
import receiver
import threading

dataMaxSize = 1024
RTT = 0.5

recentAckNum = 0
Mss = 1024
flowControlWindowSize = 200 * Mss 
Threshold = 1000 * Mss
congWin = 1 * Mss
timeLimit = 6 * RTT
sameTimeOutCount = 0

def initGlobalVariable():
    global recentAckNum , flowControlWindowSize ,  Threshold  , congWin , sameTimeOutCount 
    recentAckNum = 0
    flowControlWindowSize = 150 * Mss 
    Threshold = 1000 * Mss
    congWin = 1 * Mss
    sameTimeOutCount = 0


def sendFile(sk , addr , mylargefile , flieSize):
    global recentAckNum , Threshold ,  congWin  , RTT , sameTimeOutCount , flowControlWindowSize
    initGlobalVariable()
    flie = open(mylargefile,'rb')
    getAckThread = threading.Thread(target=getAckMessage,args=[sk,flieSize])
    getAckThread.daemon = True
    getAckThread.start()
    while recentAckNum < flieSize and sameTimeOutCount < 2:
        seqNum = recentAckNum
        #阻塞避免
        if congWin >= Threshold:
            congWin += 1 * Mss
        #print
        sendPackNum = max(1 , min(congWin , flowControlWindowSize) / Mss)
        print 'RTT is' , RTT , 'congWin is' , congWin , 'sendPackNum '\
        , sendPackNum , 'flowControlWindowSize' , flowControlWindowSize , 'recentAckNum' , recentAckNum
        ackContentArr = []
        for i in range (0, sendPackNum):
            if seqNum >= flieSize:
                break 
            head = dataSolver.getSendSeqHeader(seqNum)
            ackContent = dataSolver.packTheHeader(head)
            dataSize = getSendDataSize(ackContent) 
            flie.seek(seqNum)
            #没有一次性读完，选择一个个读取字符，可以知道文件结尾在哪
            if seqNum + dataSize >= flieSize:
                for j in range(0 , dataSize):
                    if seqNum >= flieSize:
                        break 
                    ackContent = ackContent + struct.pack("1s"  , flie.read(1) )
                    seqNum += 1
            else:
                packStr = str(dataSize) + 's'
                ackContent = ackContent + struct.pack(packStr  , flie.read(dataSize) )
                seqNum += dataSize
            ackContentArr.append(ackContent)
        
        for i in range (0, len(ackContentArr)):
            sk.sendto(ackContentArr[i] , addr)
            time.sleep( RTT / sendPackNum)
    flie.close
    if recentAckNum < flieSize:
        print 'timeout too much , stop send'
    else:
        print 'send file succesfully'

def getAckMessage(sk,flieSize):
    global recentAckNum , congWin , Threshold , sameTimeOutCount , flowControlWindowSize
    sameAckRepateTime = 0
    sk.settimeout(timeLimit)
    while recentAckNum < flieSize and sameTimeOutCount < 2:
        try:
            data , addr = sk.recvfrom(dataMaxSize)
        except:
            #time out
            Threshold = congWin / 2
            congWin = 1 * Mss
            print 'get ack pack timeout!!!!!'
            sameTimeOutCount += 1
            continue
        sameTimeOutCount = 0
        recvDataHead , recvDataContent = dataSolver.splitData(data)
        #重复ack
        if recentAckNum == recvDataHead['ackNum']:
            sameAckRepateTime += 1
            print 'same ack pack ' , recentAckNum
            #丢包
            if sameAckRepateTime == 2:
                Threshold = congWin / 2 + 3 * Mss
                congWin = Threshold
                print 'loss pack!!!!!!' 
        elif recentAckNum < recvDataHead['ackNum']: 
            sameAckRepateTime = 0
            recentAckNum = recvDataHead['ackNum']
            #慢启动
            if congWin < Threshold:
                congWin += 1 * Mss
        flowControlWindowSize = recvDataHead['cwdWindow']
    if sameTimeOutCount >= 2:
        print 'connect time out , stop sending'

    

def getSendDataSize(head):
    return dataMaxSize - len(head)
   