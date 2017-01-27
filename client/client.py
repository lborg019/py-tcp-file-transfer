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
  sentence = raw_input('>') # input for windows / raw_input for unix

  # split string to check for meaningful commands
  _check = sentence.split(" ", 1)

  #-------------------commands processed locally:
  # user calls !help
  if(sentence=="!help"):
    print ("Available commands:\n"+
           "!help         : list available commands\n"+
           "ls-local      : list local files\n"+
           "ls-remote     : list remote files\n"+
           "get 'filename': download remote file to local\n"+
           "put 'filename': upload local file to remote\n"+
           "exit          : terminates program")

  # user calls ls-local
  elif(sentence=="ls-local"):
    # refresh file list
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    print("local files:")
    for f in files:
      fileSize = os.path.getsize(f)
      print("-> "+f+"\t%d bytes" % fileSize)

  # user calls exit
  elif(sentence=="exit"):
    break

  # user calls ls-remote
  elif(sentence=="ls-remote"):
    clientSocket.sendto(sentence.encode(),(serverName, serverPort))
    modifiedSentence = clientSocket.recv(1024)
    print(modifiedSentence)

  #-------------------commands processed remotely:
  elif(len(_check)==2):
    if(_check[0].lower()=="get" or _check[0].lower()=="put"):
      #----PUT----#
      '''
       send file
       (wait) receive ACK signaling that server caught the file

       upload complete
      '''
      # for PUT we check that file exists in local directory
      if(_check[0]=='put'):
        _found = False # flag in case not found
        # refresh file list
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        for f in files:
          if(f == _check[1]):
            _found = True
            print("File found, sending request to server...")
            # send PUT 'filename to server'
            clientSocket.sendto(sentence.encode(),(serverName, serverPort))

            # receive ACK signaling that server caught file name
            modifiedSentence = clientSocket.recv(1024)
            print("ACK: "+modifiedSentence)

            # send file size to the server
            fileSize = os.path.getsize(f)
            clientSocket.sendto(str(fileSize).encode(),(serverName, serverPort))

            # receive ACK signaling that server caught file size
            modifiedSentence = clientSocket.recv(1024)
            print("ACK2 :"+modifiedSentence)

            # send file
            f = open((path+f), "rb") # read bytes flag is passed
            buffRead = 0
            bytesRemaining = int(fileSize)

            while bytesRemaining != 0:
              if(bytesRemaining >= 1024): # slab >= than 1024 buffer
                buffRead = f.read(1024)
                sizeofSlabRead = len(buffRead)
                print('remaining: %d' % bytesRemaining)
                print('read: %d'%sizeofSlabRead)
                # send slab to server:
                clientSocket.sendto(buffRead,(serverName, serverPort))
                #conn.sendall(buffRead)
                bytesRemaining = bytesRemaining - int(sizeofSlabRead)
              else: # slab smaller than 1024 buffer
                buffRead = f.read(bytesRemaining) # read 1024 bytes at a time
                sizeofSlabRead = len(buffRead)
                print('remaining: %d'%bytesRemaining)
                print('read: %d'%sizeofSlabRead)
                # send slab to server
                clientSocket.sendto(buffRead,(serverName, serverPort))
                # conn.sendall(buffRead)
                bytesRemaining = bytesRemaining - int(sizeofSlabRead)
            print("Read file completely")

        #--- file requested not found ---#
        if(_found == False):
          print('File requested not available in dir.')

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

        elif(modifiedSentence == 'False'): # file not found
          print(modifiedSentence)
          print('File requested not available in remote dir.')

      #clientSocket.sendto(sentence.encode(),(serverName, serverPort))
      #modifiedSentence = clientSocket.recv(1024)
      #print(modifiedSentence)
    else:
      # multiple invalid strings
      print("[invalid command]")
  else:
    # single invalid string
    print("[invalid command]")

# close the TCP connection
clientSocket.close()

