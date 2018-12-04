#coding=utf-8
import socket 
import struct

def getSendSeqHeader(seqNum = 0, cwdWindow = 0):
    head = {
        'syn': False,
        'ack': False,
        'send':True,
        'seqNum': seqNum ,
        'ackNum': 0 ,
        'cwdWindow': cwdWindow 
    }
 
    return head

def getSendSynHeader():
    head = {
        'syn': True,
        'ack': False,
        'send':True,
        'seqNum': 0 ,
        'ackNum': 0 ,
        'cwdWindow': 0 
    }
    return head

def getSendAckHeader(ackNum = 0, cwdWindow = 0):
    head = {
        'syn': False,
        'ack': True,
        'send':True,
        'seqNum': 0 ,
        'ackNum': ackNum ,
        'cwdWindow': cwdWindow 
    }
    return head

def getSendSynAckHeader():
    head = {
        'syn': True,
        'ack': True,
        'send':True,
        'seqNum': 0 ,
        'ackNum': 0 ,
        'cwdWindow': 0 
    }
    return head

def getRecvSynHeader():
    head = {
        'syn': True,
        'ack': False,
        'send':False,
        'seqNum': 0 ,
        'ackNum': 0 ,
        'cwdWindow': 0 
    }
    return head

def getRecvSynAckHeader():
    head = {
        'syn': True,
        'ack': True,
        'send':False,
        'seqNum': 0 ,
        'ackNum': 0 ,
        'cwdWindow': 0 
    }
    return head

def getRecvAckHeader(ackNum = 0, cwdWindow = 0):
    head = {
        'syn': False,
        'ack': True,
        'send':False,
        'seqNum': 0 ,
        'ackNum': ackNum ,
        'cwdWindow': cwdWindow 
    }
    return head

def unPackFileNameAndSize(recvDataContent):
    fileSize = struct.unpack("i" , recvDataContent[:4] )[0]
    return fileSize , recvDataContent[4:]

def splitData( data ):
    dataHead = {
        'syn': None,
        'ack': None,
        'send':None,
        'seqNum': None,
        'ackNum': None ,
        'cwdWindow': None 
    }
    head = struct.unpack('???iii' , data[:16])
    dataHead['syn'] = head[0]
    dataHead['ack'] = head[1]
    dataHead['send'] = head[2]
    dataHead['seqNum']  = head[3]
    dataHead['ackNum']  = head[4]
    dataHead['cwdWindow']  = head[5]
    return dataHead , data[16:]

def packTheHeader(dataHead):
    return struct.pack('???iii', dataHead['syn'] , dataHead['ack'] , dataHead['send'] 
                    , dataHead['seqNum'] , dataHead['ackNum'] , dataHead['cwdWindow'] )