import selectors
import socket
import random
import sys
import types

######################## Server.py ########################################
# Contributors: Matt McAuliffe and Kyle Suter                             #
# CS 3251: Networking, Programming Project 2, Fall 2018                   #
###########################################################################

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
    games = []
    multigame_clients = []

class Game:
    def __init__(self):
        clients = []
        game_states = dict()
    multiplayer = False
    clients = []
    game_states = dict()

def add_client_to_game(socket, multi):
    if Server.num_games == 0 or multi == False:
        new_game = Game()
        new_game.multiplayer = multi
        new_game.clients.append(socket)
        Server.games.append(new_game)
        Server.num_games += 1
        print("Sucessfully created game")
        return new_game
    else:
        added = False
        for i in range(0, len(Server.games)):
            if added == False and Server.games[i].multiplayer == True and len((Server.games)[i].clients) < 2:
                added = True
                Server.games[i].clients.append(socket)
                for client in Server.games[i].clients:
                    Server.multigame_clients.append(client)
                print("sucessfully added client")
                return Server.games[i]

def remove_client_from_game(socket):
    adjust = 0
    for i in range(0, len(Server.games)):
        if socket in Server.games[i - adjust].clients:
            Server.games[i - adjust].clients.remove(socket)
            adjust += 1
            if len(Server.games[i - adjust].clients) == 0:
                del(Server.games[i - adjust])
                Server.num_games -= 1

def close_matching_sock(sock):
    for i in range(0, len(Server.games)):
        if socket in Server.games[i].clients:
            for j in range(0, len(Server.games[i].clients)):
                if Server.games[i].clients[j] != socket:
                    remove_client_from_game(Server.games[i].clients[j])
                    Server.games[i].clients[j].close()

def send_message_to_fellow_socks(socket, message):
    for i in range(0, len(Server.games)):
        if socket in Server.games[i].clients:
            for j in range(0, len(Server.games[i].clients)):
                if Server.games[i].clients[j] != socket:
                    msg_len = chr(len(message)).encode('UTF-8')
                    msg_converted = message.encode('UTF-8')
                    final_msg = b''.join([msg_len, msg_converted])
                    Server.games[i].clients[j].send(final_msg)
                    print("echoing " + message + " to " + str(Server.games[i].clients[j]))

def send_data_to_fellow_socks(socket, message):
    for i in range(0, len(Server.games)):
        if socket in Server.games[i].clients:
            for j in range(0, len(Server.games[i].clients)):
                if Server.games[i].clients[j] != socket:
                    final_msg = message.encode('UTF-8')
                    Server.games[i].clients[j].send(final_msg)
                    print("echoing " + message + " to " + str(Server.games[i].clients[j]))

# create and register new connection
def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    if Server.num_games > 2:
        print('closing connection to', addr)
        conn.send(bytes(chr(17) + "server-overloaded", 'utf-8'))
        conn.close()
        return
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
    conn.send(bytes(chr(12) + "Game Started", 'utf-8'))



    letters = parse_word(choose_word())
    blanks = make_blanks(letters)
    #                       {numletters, full word, partial, incorret_num}
    Game.game_states[addr] = [len(letters), letters, blanks, 0, True, [], False, None]


# deal with data from preexisting connections
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        #if recv_data == b'':
            #return
        if len(recv_data) > 0:
            if recv_data == b'10':
                print('non-multi')
                add_client_to_game(sock, False)
                msg_flag = chr(0)
                word_size = Game.game_states[sock.getpeername()][0]
                num_incorrect = Game.game_states[sock.getpeername()][3]
                guesses = Game.game_states[sock.getpeername()][2]
                data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses))).encode('UTF-8')
            elif recv_data == b'12':
                print("multi")
                game = add_client_to_game(sock, True)
                if len(game.clients) < 2:
                    Game.game_states[sock.getpeername()][7] = key
                    data.outb += bytes(chr(27) + 'Waiting for another player!', 'utf-8')
                else:
                    for client in game.clients:
                        Game.game_states[client.getpeername()] = Game.game_states[sock.getpeername()]

                    data.outb += bytes(chr(16) + 'Players Matched!', 'utf-8')

                    msg_flag = chr(0)
                    word_size = Game.game_states[sock.getpeername()][0]
                    num_incorrect = Game.game_states[sock.getpeername()][3]
                    guesses = Game.game_states[sock.getpeername()][2]
                    data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses))).encode('UTF-8')
                    send_message_to_fellow_socks(sock, "waiting for other player to guess")
            else:
                if sock not in Server.multigame_clients:
                    data_len = int(recv_data[0])
                    in_data = chr(int(recv_data[1]))
                    letters = Game.game_states[sock.getpeername()][1]
                    correct = False
                    for i in range(len(letters)):
                        if letters[i] == in_data:
                            Game.game_states[sock.getpeername()][2][i] = letters[i]
                            correct = True
                    if correct == False:
                        Game.game_states[sock.getpeername()][5].append(in_data)
                        Game.game_states[sock.getpeername()][3] += 1
                        if Game.game_states[sock.getpeername()][3] >= 6:
                            #game over
                            data.outb += bytes(chr(9) + 'YOU LOSE!', 'utf-8')
                            data.outb += bytes( chr(10) + 'GAME OVER!', 'utf-8')
                            Game.game_states[sock.getpeername()][4] = False;
                            remove_client_from_game(sock)
                            return
                        msg_flag = chr(0)
                        word_size = Game.game_states[sock.getpeername()][0]
                        num_incorrect = Game.game_states[sock.getpeername()][3]
                        guesses = Game.game_states[sock.getpeername()][2]
                        incorrect = str(''.join(Game.game_states[sock.getpeername()][5]))
                        data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect).encode('UTF-8')

                    else:
                        all_correct = True
                        for i in range(len(letters)):
                            if Game.game_states[sock.getpeername()][2][i] != letters[i]:
                                all_correct = False
                        if all_correct == True:
                            data.outb += bytes(chr(8) + 'YOU WIN!', 'utf-8')
                            data.outb += bytes(chr(10) + 'GAME OVER!', 'utf-8')
                            Game.game_states[sock.getpeername()][4] = False;
                            remove_client_from_game(sock)
                        else:
                            msg_flag = chr(0)
                            word_size = Game.game_states[sock.getpeername()][0]
                            num_incorrect = Game.game_states[sock.getpeername()][3]
                            guesses = Game.game_states[sock.getpeername()][2]
                            incorrect = str(''.join(Game.game_states[sock.getpeername()][5]))
                            data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect).encode('UTF-8')
                else:
                    data_len = int(recv_data[0])
                    in_data = chr(int(recv_data[1]))
                    letters = Game.game_states[sock.getpeername()][1]
                    correct = False
                    for i in range(len(letters)):
                        if letters[i] == in_data:
                            Game.game_states[sock.getpeername()][2][i] = letters[i]
                            correct = True
                    data.outb += bytes((chr(8)+"Correct!") if correct else (chr(12) + "Incorrect :(") , 'utf-8')
                    data.outb += bytes(chr(21) + "Other players turn..." , 'utf-8')

                    if correct == False:
                        Game.game_states[sock.getpeername()][5].append(in_data)
                        Game.game_states[sock.getpeername()][3] += 1
                        if Game.game_states[sock.getpeername()][3] >= 6:
                            #game over
                            data.outb += bytes(chr(9) + 'YOU LOSE!', 'utf-8')
                            data.outb += bytes( chr(10) + 'GAME OVER!', 'utf-8')
                            Game.game_states[sock.getpeername()][4] = False;
                            send_message_to_fellow_socks(sock, 'YOU LOSE!')
                            send_message_to_fellow_socks(sock, 'GAME OVER!')
                            close_matching_sock(sock)
                            remove_client_from_game(sock)
                            return
                        msg_flag = chr(0)
                        word_size = Game.game_states[sock.getpeername()][0]
                        num_incorrect = Game.game_states[sock.getpeername()][3]
                        guesses = Game.game_states[sock.getpeername()][2]
                        incorrect = str(''.join(Game.game_states[sock.getpeername()][5]))
                        send_data_to_fellow_socks(sock, str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect)

                    else:
                        all_correct = True
                        for i in range(len(letters)):
                            if Game.game_states[sock.getpeername()][2][i] != letters[i]:
                                all_correct = False
                        if all_correct == True:
                            data.outb += bytes(chr(8) + 'YOU WIN!', 'utf-8')
                            data.outb += bytes(chr(10) + 'GAME OVER!', 'utf-8')
                            Game.game_states[sock.getpeername()][4] = False;
                            send_message_to_fellow_socks(sock, 'YOU WIN!')
                            send_message_to_fellow_socks(sock, 'GAME OVER!')
                            close_matching_sock(sock)
                            remove_client_from_game(sock)
                        else:
                            msg_flag = chr(0)
                            word_size = Game.game_states[sock.getpeername()][0]
                            num_incorrect = Game.game_states[sock.getpeername()][3]
                            guesses = Game.game_states[sock.getpeername()][2]
                            incorrect = str(''.join(Game.game_states[sock.getpeername()][5]))
                            send_data_to_fellow_socks(sock, str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect)

        else:
            print('closing connection to', data.addr)
            remove_client_from_game(sock)
            Game.game_states.pop(sock.getpeername())
            sel.unregister(sock)
            sock.close()


    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]
            if Game.game_states[sock.getpeername()][7] != None and Game.game_states[sock.getpeername()][7].data.outb:
                print('echoing', repr(Game.game_states[sock.getpeername()][7].data.outb), 'to', Game.game_states[sock.getpeername()][7].data.addr)
                sent = Game.game_states[sock.getpeername()][7].fileobj.send(Game.game_states[sock.getpeername()][7].data.outb)
                Game.game_states[sock.getpeername()][7].data.outb = Game.game_states[sock.getpeername()][7].data.outb[sent:]
            if Game.game_states[sock.getpeername()][4] == False:
                print('closing connection to', data.addr)
                Game.game_states.pop(sock.getpeername())
                sel.unregister(sock)
                sock.close()



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
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)










