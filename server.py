import selectors
import socket

host = '127.0.0.1'  # The server's hostname or IP address
port = 65432        # The port used by the server
sel = selectors.DefaultSelector()


lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print('listening on', (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)

def service_connection(key, mask):
    #deal with data received by the mask process