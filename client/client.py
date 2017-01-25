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

  '''''''''''''''''''''''''''''''''
  commands processed locally:
  '''''''''''''''''''''''''''''''''
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
      fileSize = os.path.getsize(f)
      print("-> "+f+"\t%d bytes" % fileSize)
    continue

  # user calls exit
  if(sentence=="exit"):
    break

  '''''''''''''''''''''''''''''''''
  commands processed by the server
  '''''''''''''''''''''''''''''''''
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
    print("[invalid command]")
    continue
  if(_check[1] and (_check[0].lower()=="get" or _check[0].lower()=="put")):

    #----PUT----#
    # for PUT we check that file exists in local directory
    if(_check[0]=='put'):
      for f in files:
        if(f == _check[1]):
          print("File found, sending request to server...")
          clientSocket.sendto(sentence.encode(),(serverName, serverPort))
          modifiedSentence = clientSocket.recv(1024)
          print(modifiedSentence)
          break
        else:
          print("File not found in local dir")
          break

    #----GET----#
    # for GET we send the string and wait for server's response
    elif(_check[0]=='get'):
      clientSocket.sendto(sentence.encode(),(serverName, serverPort))
      modifiedSentence = clientSocket.recv(1024)

      # check server's response
      if(modifiedSentence == 'True'): # file found
        print('File found, preparing download...')

        # receive file size
        reqFileSize = clientSocket.recv(1024)
        print("file size: "+reqFileSize)

        # send file size ACK to server
        fSizeACK = str(reqFileSize)
        clientSocket.sendto(fSizeACK.encode(),(serverName, serverPort))

        # receive file in slices of 1024 bytes
        # open a file in write byte mode:
        f = open((path+_check[1]), "wb") # write bytes flag is passed
        buffWrote = 0
        bytesRemaining = int(reqFileSize)

        while bytesRemaining != 0:
          if(bytesRemaining >= 1024): # slab >= than 1024 buffer
            # receive slab from server
            slab = clientSocket.recv(1024)
            f.write(slab)
            sizeofSlabReceived = len(slab)
            print("wrote %d bytes" % len(slab))

            bytesRemaining = bytesRemaining - int(sizeofSlabReceived)
          else:
            # receive slab from server
            slab = clientSocket.recv(bytesRemaining) # or 1024
            f.write(slab)
            sizeofSlabReceived = len(slab)
            print("wrote %d bytes" % len(slab))
            bytesRemaining = bytesRemaining - int(sizeofSlabReceived)

            '''
            sizeofSlab = len(slab)
            f.write(slab)
            bytesRemaining = bytesRemaining - int(sizeofSlab)
          else:
            # receive slab from server
            slab = clientSocket.recv(1024)
            sizeofSlab = len(slab)
            '''



      elif(modifiedSentence == 'False'): # file not found
        print(modifiedSentence)
        print('File requested not available in remote dir.')

    #clientSocket.sendto(sentence.encode(),(serverName, serverPort))
    #modifiedSentence = clientSocket.recv(1024)
    #print(modifiedSentence)
  else:
    print("[invalid command]")

# close the TCP connection
clientSocket.close()

