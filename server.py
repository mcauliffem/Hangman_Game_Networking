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
    game_states = dict()
    games = []

class Game:
    def __init__(multi):
        multiplayer = multi
        clients = []

def add_client_to_game(socket, multi):
    if Server.num_games == 0 or multi == False:
        new_game = Game()
        new_game.multiplayer = multi
        new_game.clients.append(socket)
        Server.games.append(new_game)
        Server.num_games += 1
    else:
        added = False
        for i in range(0, len(Server.games)):
            if added == False and Server.games[i].multiplayer == True and len((Server.games)[i].clients) < 2:
                added = True
                Server.games[i].clients.append(socket)

def remove_client_from_game(socket):
    for i in range(0, len(Server.games)):
        if socket in Server.games[i].clients:
            Server.games[i].clients.remove(socket)
            if len(Server.games[i].clients) == 0:
                del(Server.games[i])
                Server.num_games -= 1

# create and register new connection
def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)

    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

    if len(Server.games) <= 3:
        if len(Server.games) == 0:
            game = Game()
            Server.games.append(game)
        #else:


    Server.num_games += 1
    letters = parse_word(choose_word())
    blanks = make_blanks(letters)
    #                       {numletters, full word, partial, incorret_num}
    Server.game_states[addr] = [len(letters), letters, blanks, 0, True, [], False, None]


# deal with data from preexisting connections
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data == b'':
            return
        if len(recv_data) > 0:
            if recv_data == b'10':
                msg_flag = chr(0)
                word_size = Server.game_states[sock.getpeername()][0]
                num_incorrect = Server.game_states[sock.getpeername()][3]
                guesses = Server.game_states[sock.getpeername()][2]
                data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses))).encode('UTF-8')
            elif recv_data == b'12':
                found = False
                for state_key in list(Server.game_states.keys()):
                    print(state_key)
                    if Server.game_states[state_key][6] == False and Server.game_states[state_key] != Server.game_states[sock.getpeername()] and found == False:
                        Server.game_states[state_key][6] = True
                        Server.game_states[sock.getpeername()] = Server.game_states[state_key]
                        Server.game_states[state_key][7] = key
                        found = True
                        data.outb += bytes(chr(16) + 'Players Matched!', 'utf-8')

                        msg_flag = chr(0)
                        word_size = Server.game_states[sock.getpeername()][0]
                        num_incorrect = Server.game_states[sock.getpeername()][3]
                        guesses = Server.game_states[sock.getpeername()][2]
                        data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses))).encode('UTF-8')
                        Server.game_states[sock.getpeername()][7].data.outb += bytes(chr(36) + 'Waiting for other player to guess...', 'utf-8')
                    print(Server.game_states[state_key][6])
                if found == False:
                    Server.num_games -= 1
                    Server.game_states[sock.getpeername()][7] = key
                    data.outb += bytes(chr(27) + 'Waiting for another player!', 'utf-8')
            else:
                data_len = int(recv_data[0])
                in_data = chr(int(recv_data[1]))
                letters = Server.game_states[sock.getpeername()][1]
                correct = False
                for i in range(len(letters)):
                    if letters[i] == in_data:
                        Server.game_states[sock.getpeername()][2][i] = letters[i]
                        correct = True
                if correct == False:
                    Server.game_states[sock.getpeername()][5].append(in_data)
                    Server.game_states[sock.getpeername()][3] += 1
                    if Server.game_states[sock.getpeername()][3] >= 6:
                        #game over
                        data.outb += bytes(chr(9) + 'YOU LOSE!', 'utf-8')
                        data.outb += bytes( chr(10) + 'GAME OVER!', 'utf-8')
                        Server.game_states[sock.getpeername()][4] = False;
                        return
                    msg_flag = chr(0)
                    word_size = Server.game_states[sock.getpeername()][0]
                    num_incorrect = Server.game_states[sock.getpeername()][3]
                    guesses = Server.game_states[sock.getpeername()][2]
                    incorrect = str(''.join(Server.game_states[sock.getpeername()][5]))
                    data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect).encode('UTF-8')

                else:
                    all_correct = True
                    for i in range(len(letters)):
                        if Server.game_states[sock.getpeername()][2][i] != letters[i]:
                            all_correct = False
                    if all_correct == True:
                        data.outb += bytes(chr(8) + 'YOU WIN!', 'utf-8')
                        data.outb += bytes(chr(10) + 'GAME OVER!', 'utf-8')
                        Server.game_states[sock.getpeername()][4] = False;
                    else:
                        msg_flag = chr(0)
                        word_size = Server.game_states[sock.getpeername()][0]
                        num_incorrect = Server.game_states[sock.getpeername()][3]
                        guesses = Server.game_states[sock.getpeername()][2]
                        incorrect = str(''.join(Server.game_states[sock.getpeername()][5]))
                        data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect).encode('UTF-8')
        else:
            print('closing connection to', data.addr)
            Server.game_states.pop(sock.getpeername())
            sel.unregister(sock)
            sock.close()
            Server.num_games -= 1


    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]
            if Server.game_states[sock.getpeername()][7] != None and Server.game_states[sock.getpeername()][7].data.outb:
                print('echoing', repr(Server.game_states[sock.getpeername()][7].data.outb), 'to', Server.game_states[sock.getpeername()][7].data.addr)
                sent = Server.game_states[sock.getpeername()][7].fileobj.send(Server.game_states[sock.getpeername()][7].data.outb)
                Server.game_states[sock.getpeername()][7].data.outb = Server.game_states[sock.getpeername()][7].data.outb[sent:]
            if Server.game_states[sock.getpeername()][4] == False:
                print('closing connection to', data.addr)
                Server.game_states.pop(sock.getpeername())
                sel.unregister(sock)
                sock.close()
                Server.num_games -= 1



if __name__ == '__main__':
    host = '127.0.0.1'  # The server's hostname or IP address
    port = int(sys.argv[1])        # The port used by the server

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
                if Server.num_games < 3:
                    accept_wrapper(key.fileobj)
                else:
                    key.fileobj.send(bytes(chr(16) + "server-overloaded", 'utf-8'))
                    key.fileobj.close()
            else:
                service_connection(key, mask)










