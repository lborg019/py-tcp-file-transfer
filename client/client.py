##########################################################################
"""  TCPClient.py                                     
Use the better name for this module:   MakeUpperCaseClientUsingTCP   
  
[STUDENTS FILL IN THE ITEMS BELOW]  
  STUDENT NAME                                 
  COURSE NAME and SEMESTER                    
  DATE                                         
  This module will <blah, blah, blah>              
"""

from socket import *
import os
# STUDENTS - replace your server machine's name 
serverName = "localhost"

# STUDENTS - you should randomize your port number.         
# This port number in practice is often a "Well Known Number"  
serverPort = 8888

# create TCP socket on client to use for connecting to remote
# server.  Indicate the server's remote listening port
# Error in textbook?   socket(socket.AF_INET, socket.SOCK_STREAM)  Amer 4-2013 
clientSocket = socket(AF_INET, SOCK_STREAM)

# open the TCP connection
clientSocket.connect((serverName,serverPort))

print("Connected. Type !help for command list:\n")
path = ("./")
files = [f for f in os.listdir('.') if os.path.isfile(f)]

while 1:
  # interactively get user's line to be converted to upper case
  # authors' use of raw_input changed to input for Python 3  Amer 4-2013
  sentence = raw_input('>') # input for windows / raw_input for unix

  # split string to check for meaningful commands
  _check = sentence.split(" ", 1)

  # commands processed locally:
  # user calls !help
  if(sentence=="!help"):
    print ("Available commands:\n"+
           "!help         : list available commands\n"+
           "ls-local      : list local files\n"+
           "ls-remote     : list remote files\n"+
           "get 'filename': download remote file to local\n"+
           "put 'filename': upload local file to remote\n"+
           "exit          : terminates program")
    continue

  # user calls ls-local
  if(sentence=="ls-local"):
    print("local files:")
    for f in files:
      print("-> "+f)
    continue

  # user calls exit
  if(sentence=="exit"):
    break

  # commands processed by the server
  # user calls ls-remote
  if(sentence=="ls-remote"):

    # send the user's line over the TCP connection
    # No need to specify server name, port
    # sentence casted to bytes for Python 3  Amer 4-2013

    # To run on windows:
    # clientSocket.send(sentence)
    clientSocket.sendto(sentence.encode(),(serverName, serverPort))

    #output to console what is sent to the server
    # print ("Sent to Make Upper Case Server: ", sentence)

    # get user's line back from server having been modified by the server
    modifiedSentence = clientSocket.recv(1024)

    # output the modified user's line 
    # print ("Received from Make Upper Case Server: ", modifiedSentence)
    print(modifiedSentence)
    continue
  if(len(_check)!= 2):
    print("[improper command]")
    continue
  if(_check[1] and (_check[0].lower()=="get" or _check[0].lower()=="put")):
    # for put we check that file exists in local directory
    if(_check[0].lower=="put")


    # for get we send the string and wait for server's response

    clientSocket.sendto(sentence.encode(),(serverName, serverPort))
    modifiedSentence = clientSocket.recv(1024)
    print(modifiedSentence)
  else:
    print("[improper command]")

# close the TCP connection
clientSocket.close()

