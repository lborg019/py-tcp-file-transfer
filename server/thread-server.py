import socket
import sys
import os
import select
import re
from thread import *

path = ("./")
# fileList = []
_lsremote = "ls-remote"
files = [f for f in os.listdir('.') if os.path.isfile(f)]
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'
 
#Start listening on socket
s.listen(10)
print 'Socket now listening'
 
#Function for handling connections. This will be used to create threads
def clientthread(conn):
    #Sending message to connected client
    # conn.send('Connected, type !help for command list:\n') #send only takes string
     
    #infinite loop so that function do not terminate and thread do not end.
    while True:
         
        #Receiving from client
        data = conn.recv(1024)

        # telnet sends dirty strings, t = data.isalnum() to check. clean if using telnet

        # we split data at the first white space. first word is opcode, second is file
        _data = data.split(" ", 1)

        #----ls-remote----#
        if(data == _lsremote):
            print('User: '+addr[0]+':'+str(addr[1])+' requested ls-remote')
            remoteList = 'remote files:'
            for f in files:
                fileSize = os.path.getsize(f)
                remoteList += ("\n-> "+f+"\t%d bytes" % fileSize)
            conn.sendall(remoteList)

        #----GET----#
        elif(_data[0] == 'get'):
            _found = False
            print('User: '+addr[0]+':'+str(addr[1])+' requested a GET for: %s' % _data[1])
            for f in files:
                if(f == _data[1]): # if file requested if found
                    _found = True
                    print('File found. Sending file size to user:')
                    # send file size, read file bytes into a buffer, send buffer
                    reply = 'File found, preparing to download...'
                    conn.sendall(reply)

            #--- file requested not found ---#
            if(_found == False):
                print('File requested not available in dir.')
                reply = 'File not found.'
                conn.sendall(reply)

            #reply = 'OK...' + data
            #conn.sendall(reply)
            #break
        else:
            print(data)
            reply = 'OK...' + data
            conn.sendall(reply)

        if not data: 
            break
        # conn.sendall(reply)
     
    #came out of loop
    print 'User: '+addr[0]+':'+str(addr[1])+' disconnected'
    conn.close()
 
#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread ,(conn,))
 
s.close()