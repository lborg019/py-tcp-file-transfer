# FTP Client Luz Adriana Aguilar
# ********************************************************************************
# **                   **
# ** References                                                                 **
# ** http://www.slacksite.com/other/ftp.html#active                             **
# ** https://www.ietf.org/rfc/rfc959.txt                                        **
# ** Computer-Networking Top-Down Approach 6th Edition by Kurose and Ross       **
# ** computer ftp client                                                        **
# **                                                                            **
# ** Tested with inet.cis.fiu.edu  -- FIXED Port 21                             **
# ** Commands are not case sensitive                                            **
# **                                                                            **
# ** Built for Python 2.7.x. FTP Client Active Mode Only                        **
# ** Usage: Python ftp.py hostname [username] [password]                        **
# ** username and password are optional when invoking ftp.py                    **
# ** if not supplied, use command LOGIN                                         **
# ** Inside of ftp client, you can type HELP for more information               **
# ********************************************************************************

#import necessary packages.
import os
import os.path
import sys
from socket import *

#Global constants
USAGE = "usage: Python ftp hostname [username] [password]"


RECV_BUFFER = 1024
FTP_PORT = 21
CMD_QUIT = "QUIT"
CMD_HELP = "HELP"
CMD_LOGIN = "LOGIN"
CMD_LOGOUT = "LOGOUT"
CMD_LS = "LS"
CMD_PWD = "PWD"
CMD_PORT = "PORT"
CMD_DELETE = "DELETE"
CMD_PUT = "PUT"
CMD_GET = "GET"

#The data port starts at high number (to avoid privileges port 1-1024)
#the ports ranges from MIN to MAX
DATA_PORT_MAX = 61000
DATA_PORT_MIN = 60020
#data back log for listening.
DATA_PORT_BACKLOG = 1

#global variables
#store the next_data_port use in a formula to obtain
#a port between DATA_POR_MIN and DATA_PORT_MAX
next_data_port = 1

#entry point main()
def main():
    # hostname = "inet.cis.fiu.edu"
    hostname = "localhost"
    username = ""
    password = ""

    logged_on = False
    logon_ready = False
    print("FTP Client v1.0")
    if (len(sys.argv) < 2):
         print(USAGE)
    if (len(sys.argv) == 2):
        hostname = sys.argv[1]
    if (len(sys.argv) == 4):
        username = sys.argv[2]
        password = sys.argv[3]
        logon_ready = True


    print("********************************************************************")
    print("**                        ACTIVE MODE ONLY                        **")
    print("********************************************************************")
    print("You will be connected to host:" + hostname)
    print("Type HELP for more information")
    print("Commands are NOT case sensitive\n")


    ftp_socket = ftp_connecthost(hostname)
    ftp_recv = ftp_socket.recv(RECV_BUFFER)
    ftp_code = ftp_recv[:3]
    #
    #note that in the program there are many .strip('\n')
    #this is to avoid an extra line from the message
    #received from the ftp server.
    #an alternative is to use sys.stdout.write
    print(ftp_recv.strip('\n'))
    #
    #this is the only time that login is called
    #without relogin
    #otherwise, relogin must be called, which included prompts
    #for username
    #
    if (logon_ready):
        logged_on = login(username,password,ftp_socket)

    keep_running = True

    while keep_running:
        rinput = raw_input("FTP>")
        tokens = rinput.split()
        #just in case a user types lowercase
        #the command (for example login is converted to LOGIN)
        cmd = tokens[0].upper()
        if (cmd == CMD_QUIT):
            quit_ftp(logged_on,ftp_socket)
        if (cmd == CMD_HELP):
            help_ftp()
        if (cmd == CMD_PWD):
            pwd_ftp(ftp_socket)
        if (cmd == CMD_LS):
            #FTP must create a channel to received data before
            #executing ls.
            #also makes sure that data_socket is valid
            #in other words, not None
            data_socket = ftp_new_dataport(ftp_socket)
            if (data_socket is not None):
                ls_ftp(tokens,ftp_socket,data_socket)
            else:
                print("[LS] Failed to get data port. Try again.")
        if (cmd == CMD_LOGIN):
            username, password, logged_on, ftp_socket \
                = relogin(username, password, logged_on, tokens, hostname, ftp_socket)
        if (cmd == CMD_LOGOUT):
            logged_on,ftp_socket = logout(logged_on,ftp_socket)
        if (cmd == CMD_DELETE):
            delete_ftp(tokens,ftp_socket)
        if (cmd == CMD_PUT):
            # FTP must create a channel to received data before
            # executing put.
            # also makes sure that data_socket is valid
            # in other words, not None
            data_socket = ftp_new_dataport(ftp_socket)
            if (data_socket is not None):
                put_ftp(tokens,ftp_socket,data_socket)
            else:
                print("[PUT] Failed to get data port. Try again.")
        if (cmd == CMD_GET):
            # FTP must create a channel to received data before
            # executing get.
            # also makes sure that data_socket is valid
            # in other words, not None
            data_socket = ftp_new_dataport(ftp_socket)
            if (data_socket is not None):
                get_ftp(tokens, ftp_socket, data_socket)
            else:
                print("[GET] Failed to get data port. Try again.")


    #print ftp_recv
    ftp_socket.close()
    print("Thank you for using FTP 1.0")
    sys.exit()

def ftp_connecthost(hostname):

    ftp_socket = socket(AF_INET, SOCK_STREAM)
    #to reuse socket faster. It has very little consequence for ftp client.
    ftp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    ftp_socket.connect((hostname, FTP_PORT))

    return ftp_socket

def ftp_new_dataport(ftp_socket):
    global next_data_port
    dport = next_data_port
    host = gethostname()
    host_address = gethostbyname(host)
    next_data_port = next_data_port + 1 #for next next
    dport = (DATA_PORT_MIN + dport) % DATA_PORT_MAX

    print("Preparing Data Port: " + host + " " + host_address + " " + str(dport))
    data_socket = socket(AF_INET, SOCK_STREAM)
    # reuse port
    data_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    data_socket.bind((host_address, dport))
    data_socket.listen(DATA_PORT_BACKLOG)

    #the port requires the following
    #PORT IP PORT
    #however, it must be transmitted like this.
    #PORT 192,168,1,2,17,24
    #where the first four octet are the ip and the last two form a port number.
    host_address_split = host_address.split('.')
    high_dport = str(dport // 256) #get high part
    low_dport = str(dport % 256) #similar to dport << 8 (left shift)
    port_argument_list = host_address_split + [high_dport,low_dport]
    port_arguments = ','.join(port_argument_list)
    print(CMD_PORT + ' ' + port_arguments)


    try:
        ftp_socket.send(CMD_PORT + ' ' + port_arguments + '\r\n')
    except socket.timeout:
        print("Socket timeout. Port may have been used recently. wait and try again!")
        return None
    except socket.error:
        print("Socket error. Try again")
        return None
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg.strip('\n'))
    return data_socket

def pwd_ftp(ftp_socket):
    ftp_socket.send("PWD\n")
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg.strip('\n'))


def get_ftp(tokens, ftp_socket, data_socket):
    if (len(tokens) < 2):
        print("put [filename]. Please specify filename")
        return

    remote_filename = tokens[1]
    if (len(tokens) == 3):
        filename = tokens[2]
    else:
        filename = remote_filename

    ftp_socket.send("RETR " + remote_filename + "\n")

    print("Attempting to write file. Remote: " + remote_filename + " - Local:" + filename)

    msg = ftp_socket.recv(RECV_BUFFER)
    tokens = msg.split()
    if (tokens[0] != "150"):
        print("Unable to retrieve file. Check that file exists (ls) or that you have permissions")
        return

    print(msg.strip('\n'))

    data_connection, data_host = data_socket.accept()
    file_bin = open(filename, "wb")  # read and binary modes

    size_recv = 0
    sys.stdout.write("|")
    while True:
        sys.stdout.write("*")
        data = data_connection.recv(RECV_BUFFER)

        if (not data or data == '' or len(data) <= 0):
            file_bin.close()
            break
        else:
            file_bin.write(data)
            size_recv += len(data)

    sys.stdout.write("|")
    sys.stdout.write("\n")
    data_connection.close()

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg.strip('\n'))


### put_ftp
def put_ftp(tokens,ftp_socket,data_socket):

    if (len(tokens) < 2):
        print("put [filename]. Please specify filename")
        return

    local_filename = tokens[1]
    if (len(tokens) == 3):
        filename = tokens[2]
    else:
        filename = local_filename

    if (os.path.isfile(local_filename) == False):
        print("Filename does not exisit on this client. Filename: " + filename + " -- Check file name and path")
        return
    filestat = os.stat(local_filename)
    filesize = filestat.st_size

    ftp_socket.send("STOR " + filename + "\n")
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg.strip('\n'))

    print("Attempting to send file. Local: " + local_filename + " - Remote:" + filename + " - Size:" + str(filesize))

    data_connection, data_host = data_socket.accept()
    file_bin = open(filename,"rb") #read and binary modes

    size_sent = 0
    #use write so it doesn't produce a new line (like print)
    sys.stdout.write("|")
    while True:
        sys.stdout.write("*")
        data = file_bin.read(RECV_BUFFER)
        if (not data or data == '' or len(data) <= 0):
            file_bin.close()
            break
        else:
            data_connection.send(data)
            size_sent += len(data)

    sys.stdout.write("|")
    sys.stdout.write("\n")
    data_connection.close()

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg.strip('\n'))



def ls_ftp(tokens,ftp_socket,data_socket):

    if (len(tokens) > 1):
        ftp_socket.send("LIST " + tokens[1] + "\n")
    else:
        ftp_socket.send("LIST\n")

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg.strip('\n'))

    data_connection, data_host = data_socket.accept()

    msg = data_connection.recv(RECV_BUFFER)
    while (len(msg) > 0):
        print(msg.strip('\n'))
        msg = data_connection.recv(RECV_BUFFER)

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg.strip('\n'))
    data_connection.close()

def delete_ftp(tokens, ftp_socket):

    if (len(tokens) < 2):
        print("You must specify a file to delete")
    else:
        print("Attempting to delete " + tokens[1])
        ftp_socket.send("DELE " + tokens[1] + "\n")

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg.strip('\n'))

def logout(lin, ftp_socket):
    if (ftp_socket is None):
        print("Your connection was already terminated.")
        return False, ftp_socket

    if (lin == False):
        print("You are not logged in. Logout command will be send anyways")

    print("Attempting to logged out")
    msg = ""
    try:
        ftp_socket.send("QUIT\n")
        msg = ftp_socket.recv(RECV_BUFFER)
    except socket.error:
        print ("Problems logging out. Try logout again. Do not login if you haven't logged out!")
        return False
    print(msg.strip('\n'))
    ftp_socket = None
    return False, ftp_socket #it should only be true if logged in and not able to logout

def quit_ftp(lin,ftp_socket):
    print ("Quitting...")
    logged_on, ftp_socket = logout(lin,ftp_socket)
    print("Thank you for using FTP")
    try:
        if (ftp_socket is not None):
            ftp_socket.close()
    except socket.error:
        print ("Socket was not able to be close. It may have been closed already")
    sys.exit()


def relogin(username,password,logged_on,tokens,hostname,ftp_socket):
    if (len(tokens) < 3):
        print("LOGIN requires more arguments. LOGIN [username] [password]")
        print("You will be prompted for username and password now")
        username = raw_input("User:")
        password = raw_input("Pass:")
    else:
        username = tokens[1]
        password = tokens[2]

    if (ftp_socket is None):
        ftp_socket = ftp_connecthost(hostname)
        ftp_recv = ftp_socket.recv(RECV_BUFFER)
        print (ftp_recv.strip('\n'))

    logged_on = login(username, password, ftp_socket)
    return username, password, logged_on, ftp_socket


def help_ftp():
    print("FTP Help")
    print("Commands are not case sensitive")
    print("")
    print(CMD_QUIT + "\t\t Exits ftp and attempts to logout")
    print(CMD_LOGIN + "\t\t Logins. It expects username and password. LOGIN [username] [password]")
    print(CMD_LOGOUT + "\t\t Logout from ftp but not client")
    print(CMD_LS + "\t\t prints out remote directory content")
    print(CMD_PWD + "\t\t prints current (remote) working directory")
    print(CMD_GET + "\t\t gets remote file. GET remote_file [name_in_local_system]")
    print(CMD_PUT + "\t\t sends local file. PUT local_file [name_in_remote_system]")
    print(CMD_DELETE + "\t\t deletes remote file. DELETE [remote_file]")
    print(CMD_HELP + "\t\t prints help FTP Client")


def login(user, passw, ftp_socket):
    if (user == None or user.strip() == ""):
        print("Username is blank. Try again")
        return False;


    print("Attempting to login user " + user)
    #send command user
    ftp_socket.send("USER " + user + "\n")
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg.strip('\n'))
    ftp_socket.send("PASS " + passw + "\n")
    msg = ftp_socket.recv(RECV_BUFFER)
    tokens = msg.split()
    print(msg.strip('\n'))
    if (len(tokens) > 0 and tokens[0] != "230"):
        print("Not able to login. Please check your username or password. Try again!")
        return False
    else:
        return True

#Calls main function.
main()
