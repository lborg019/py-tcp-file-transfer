##########################################################################
""" TCPServer.py                                     
Use the better name for this module:   MakeUpperCaseServerUsingTCP   
  
[STUDENTS FILL IN THE ITEMS BELOW]  
  STUDENT NAME                                 
  COURSE NAME and SEMESTER                    
  DATE                                         
  This module will <blah, blah, blah>              
"""

from socket import *
import os
import select

_help = "help"
_lsremote = "ls-remote"
_get = "get "
_put = "put "
_quit = "/quit"
_exit = "/exit"

path = ("./")
files = [f for f in os.listdir('.') if os.path.isfile(f)]
fileList = []
remoteList = "remote files:"

# STUDENTS: randomize this port number (use same one that client uses!)
serverPort = 12000

# create TCP welcoming socket
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(("",serverPort))

# server begins listening for incoming TCP requests
serverSocket.listen(5)

# output to console that server is listening 
print ("The Make Upper Case Server running over TCP is ready to receive ... ")

# server waits for incoming requests; new socket created on return
connectionSocket, addr = serverSocket.accept()
print(addr)

while 1:
    # read a sentence of bytes from socket sent by the client
    sentence = connectionSocket.recv(1024)

    # output to console the sentence received from the client 
    print ("Received From Client: ", sentence)

    # check what message was sent, process accordingly
    if sentence == _help.lower():
      print ("received help");
    elif sentence == _lsremote.lower():
      # concatenate file list in string and send:
      for f in files:
        remoteList += ("\n"+f)
      connectionSocket.send(remoteList)
    elif sentence == _get:
      print ("received a get");
    else:
      print ("received some bs command");
	 
    # convert the sentence to upper case
    capitalizedSentence = sentence.upper()
	 
    # send back modified sentence over the TCP connection
    connectionSocket.send(capitalizedSentence)

    # output to console the sentence sent back to the client 
    print ("Sent back to Client: ", capitalizedSentence)

# close the TCP connection; the welcoming socket continues
connectionSocket.close()
	 
##########################################################################

