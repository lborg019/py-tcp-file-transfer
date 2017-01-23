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
serverPort = 12000

# create TCP socket on client to use for connecting to remote
# server.  Indicate the server's remote listening port
# Error in textbook?   socket(socket.AF_INET, socket.SOCK_STREAM)  Amer 4-2013 
clientSocket = socket(AF_INET, SOCK_STREAM)

# open the TCP connection
clientSocket.connect((serverName,serverPort))

print ("Available commands:\n"+
       "help: list available commands\n"+
       "ls-local: list local files\n"+
       "ls-remote: list remote files\n"+
       "get 'filename': download remote file to local\n"+
       "put 'filename': upload local file to remote\n"+
       "/quit or /exit: terminates program")
path = ("./")
files = [f for f in os.listdir('.') if os.path.isfile(f)]

while 1:
  # interactively get user's line to be converted to upper case
  # authors' use of raw_input changed to input for Python 3  Amer 4-2013
  sentence = raw_input('command:') # input for windows / raw_input for unix

  if(sentence=="ls-local"):
    print("local files:")
    for f in files:
      print(f)

  if(sentence=="exit"):
    break

  # send the user's line over the TCP connection
  # No need to specify server name, port
  # sentence casted to bytes for Python 3  Amer 4-2013

  # modified to run on windows:
  # clientSocket.send(sentence)
  clientSocket.sendto(sentence.encode(),(serverName, serverPort))

  #output to console what is sent to the server
  print ("Sent to Make Upper Case Server: ", sentence)

  # get user's line back from server having been modified by the server
  modifiedSentence = clientSocket.recv(1024)

  # output the modified user's line 
  # print ("Received from Make Upper Case Server: ", modifiedSentence)
  print(modifiedSentence)

# close the TCP connection
clientSocket.close()

