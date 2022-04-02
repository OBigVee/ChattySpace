import socket
import select
import errno
import sys



HEADER_LEN = 10
IP = "127.0.0.1"
PORT = 1234

myUsername = input("Username : ")
client_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_Socket.connect((IP, PORT))
client_Socket.setblocking(False)


username = myUsername.encode('utf-8')
username_header = f"{len(username):<{HEADER_LEN}}".encode("utf-8")
client_Socket.send(username_header + username)


while True:
    message = input(f"{myUsername} > ")
    if message:
        message = message.encode("utf-8")
        message_header = f"{len(message) :< {HEADER_LEN}}".encode("utf-8")
        client_Socket.send(message_header + message)

    try:
        while True:
            username_header = client_Socket.recv(HEADER_LEN)
            if not len(username_header):
                print(":: Connection closed by the server  ::")
                sys.exit()
            
            username_len = int(username_header.decode("utf-8").strip())
            username = client_Socket.recv(username_len).decode("utf-8")
            

            message_header = client_Socket.recv(HEADER_LEN)
            message_len = int(message_header.decode("utf-8").strip())
            message = client_Socket.recv(message_len).decode("utf-8")

            print(f"{username} > {message} ")

    except IOError as E:
        if E.errno != errno.EAGAIN and E.errno != errno.EWOULDBLOCK:
            print(":: Reading error", str(E))
            sys.exit()
        continue

    except Exception as E:
        print(":: General Error",str(E))
        sys.exit()