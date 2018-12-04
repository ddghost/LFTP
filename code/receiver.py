#coding=utf-8
import socket 
import struct
import dataSolver
import Queue
import threading


Mss = 1024
qMaxSize = 150 * Mss
cache = Queue.Queue(qMaxSize)
recvContinue = True
mutex = threading.Lock()

def initGlobalVariable():
    global cache , recvContinue
    cache = Queue.Queue(qMaxSize)
    recvContinue = True

def recvSendFile(recvSk , addr , fileName , fileSize):
    global cache  , recvContinue , mutex
    print 'begin to recv file ' , fileName , ' size is ' , fileSize
    initGlobalVariable()
    
    nowAckNum = 0
    writeThread = threading.Thread(target=writeData,args=[fileName,fileSize,])
    #writeThread.daemon = True
    writeThread.start()
    recvSk.settimeout(5)
    while nowAckNum < fileSize:
        try:
            data,addr = recvSk.recvfrom( Mss )
        except:
            #time out
            break
        recvDataHead , recvDataContent = dataSolver.splitData(data)
        if recvDataHead['seqNum'] < nowAckNum:
           # don't send data
            continue
        elif recvDataHead['seqNum'] == nowAckNum:
            putDataIntoCache(recvDataContent)
            nowAckNum += len(recvDataContent)
        else:
            #debug
            print 'seqNum ' , recvDataHead['seqNum']  , ' != ackNum ' , nowAckNum
        cwdWindow = cache.maxsize - cache.qsize()
        ackHead = dataSolver.getSendAckHeader(nowAckNum , cwdWindow)
        ackContend = dataSolver.packTheHeader(ackHead)
        recvSk.sendto(ackContend , addr)  
        
    if nowAckNum < fileSize:
        print 'recieve 0 file pack in last 5 second , timeout , stop receiving'
    else:
        print 'file has already recieved succesfully' 
        while not cache.empty():
            pass
        print 'file has already written in the disk'
    recvContinue = False
    recvSk.close()

def putDataIntoCache(recvDataContent):
    global cache 
    while cache.full():
        pass 
    while True:  
        if mutex.acquire(1):
            for index in range(0 , len(recvDataContent) ):
                cache.put(recvDataContent[index] ) 
            mutex.release()
            break 
        

def writeData(fileName,fileSize):
    global cache , recvContinue , mutex
    file = open(fileName, 'wb')
    writePos = 0
    oneTimeWriteChars = 128
    while writePos < fileSize and recvContinue:
        if not cache.empty() and mutex.acquire(1):
            writeCharsNum =  min(cache.qsize() , oneTimeWriteChars)
            writeStr = ''
            for i in range(0 , writeCharsNum):
                writeStr += cache.get() 
            file.write(writeStr)
            writePos += writeCharsNum
            mutex.release()
    file.close()
