from email import message
from http import client
import socket
import select

HEADER_LEN = 10
IP = "127.0.0.1"
PORT = 1234
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()
socket_list = [server_socket]
clients = {}

print(f" ::: Listening for connections on {IP}:{PORT} ...")

# handle recieved messages
def recieve_mssg(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LEN)
        # if a client closes a conn, socket.close() will be auto called
        # there will be no header
        if not len(message_header):
            # no message_header
            return False
        message_len = int (message_header.decode("utf_8").strip())
        return{"header":message_header, "data":client_socket.recv(message_len)}

    except:
        return False

# infinte loop  recieves messages for all client sockets.
# sends all the messages out to available clients connected to the server
while True:
    # select.select (OS-level i/o) takes prams(Read,write,error lists respectively)

    read_socs, _, exception_socs = select.select(socket_list, [] ,socket_list)
    for notify_soc in read_socs:
        # if notified socket is server socket, it means 
        # a new connection is established and then handle it
        if notify_soc == server_socket:
            client_soc, client_addr = server_socket.accept()

            user = recieve_mssg(client_soc)
            if user is False:
                continue
            socket_list.append(client_soc)
            clients[client_soc] = user
            #print(f"Accepted new connection from {client_addr[0]}:{client_addr[1]} username:{user["data"].decode("utf-8")}")
            print(f"::: Accepted new connection from {client_addr[0]}:{client_addr[1]} username:{user['data'].decode('utf-8')}")

        else:
            message= recieve_mssg(notify_soc)
            if message is False:
                print(f"!:: Close connection from {clients[notify_soc]['data'].decode('utf-8')}")
                socket_list.remove(notify_soc)
                del clients[notify_soc]
                continue 
            user = clients[notify_soc]
            print(f"!::Recieved message from {user['data'].decode('utf-8')}:{message['data'].decode('utf-8')}")
            # iterate ovet the connected clients and broadcast message

            for client_soc in clients:
                if client_soc != notify_soc:
                    client_soc.send(user['header'] + user['data']+message['header']+message['data'])
    for notify_soc in exception_socs:
        socket_list.remove(notify_soc)
        del clients[notify_soc]