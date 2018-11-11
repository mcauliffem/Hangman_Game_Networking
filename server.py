import selectors
import socket
import random
import sys
import types

# words
word_bank = ['cat', 'dog', 'fish', 'bull', 'koala', 'otter', 'zebra', 'snakes',
             'hippos', 'parrot', 'giraffe', 'penguin', 'tortoise', 'anaconda',
             'mosquito']

def choose_word():
    return random.choice(word_bank)

def parse_word(word):
    chars = list(word)
    return chars

def make_blanks(letters):
    blanks = ['_'] * len(letters)
    return blanks
class Server:
    num_games = 0


# create and register new connection
def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

# deal with data from preexisting connections
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data_len = recv_data[0]
            in_data = recv_data[1]
            letters = game_states[sock][1]
            correct = False
            for i in range(len(letters)):
                if letters[i] == in_data:
                    game_states[sock][2][i] = in_data
                    correct = True
            if correct == False:
                game_states[3] += 1
                if game_states[3] >= 6:
                    #game over
                    msg_flag = '8'
                    data.outb += (msg_flag + b'YOU LOSE')
                    data.outb += (msg_flag + b'GAMEOVER')

            else:
                all_correct = True
                for i in range(len(letters)):
                    if game_states[sock][2][i] != letters[i]:
                        all_correct = False
                if all_correct == True:
                    msg_flag = '8'
                    data.outb += (msg_flag + b'YOU WIN!')
                    data.outb += (msg_flag + b'GAMEOVER')
                else:
                    msg_flag = '0'
                    word_size = game_states[sock][0].to_bytes(1, byteorder='big', signed=True)
                    num_incorrect = game_states[sock][3].to_bytes(1, byteorder='big', signed=True)
                    guesses = game_states[sock][2].to_bytes(1, byteorder='big', signed=True)
                    data.outb += (msg_flag + word_size + num_incorrect + guesses)
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
            Server.num_games -= 1
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


if __name__ == '__main__':
    host = '127.0.0.1'  # The server's hostname or IP address
    port = int(sys.argv[1])        # The port used by the server

    sel = selectors.DefaultSelector()
    game_states = {}



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
                if Server.num_games < 3:
                    accept_wrapper(key.fileobj)
                    Server.num_games += 1
                    letters = parse_word(choose_word())
                    blanks = make_blanks(letters)
                    #                       {numletters, full word, partial, incorret_num}
                    game_states[key.fileobj] = [len(letters), letters, blanks, 0]
                else:
                    key.fileobj.close()
            else:
                service_connection(key, mask)










