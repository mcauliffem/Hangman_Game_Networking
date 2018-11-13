import selectors2 as selectors
import socket
import random
import sys
import types

######################## Server.py ########################################
# Contributors: Matt McAuliffe and Kyle Suter                             #
# CS 3251: Networking, Programming Project 2, Fall 2018                   #
###########################################################################

# Words to choose from
word_bank = ['cat', 'dog', 'fish', 'bull', 'koala', 'otter', 'zebra', 'snakes',
             'hippos', 'parrot', 'giraffe', 'penguin', 'tortoise', 'anaconda',
             'mosquito']

#Picks a word from the bank randomly
def choose_word():
    return random.choice(word_bank)

#Splits the word up into a list of letters
def parse_word(word):
    chars = list(word)
    return chars

#Makes a list of blanks in equal number to the number of letters in word
def make_blanks(letters):
    blanks = ['_'] * len(letters)
    return blanks

#Contains class variables for which access is necessary throughout server code
class Server:
    num_games = 0
    games = []
    multigame_clients = []

#Maintains the state of each individual game as well as the clients in it
class Game:
    def __init__(self):
        self.clients = []
        self.game_states = dict()
        self.multiplayer = False
    clients = []
    multiplayer = False
    game_states = dict()

#Created in the conversion to python 2 to replace types.SimpleNameSpace()
class Data:
    def __init__(self, address):
        self.addr = address
        self.inb = b''
        self.outb = b''

#Add a client into a game either by creating a game if it is single player
#or searching for an open multiplayer game to insert the player into.
#if a game isn't found for the multiplayer user a new one is created
def add_client_to_game(socket, multi):
    print(str(socket))
    #single player
    if  multi == False:
        new_game = Game()
        new_game.multiplayer = multi
        new_game.clients.append(socket)
        Server.games.append(new_game)
        Server.num_games += 1
        print("Sucessfully created game")
        return new_game
    #multi player
    else:
        added = False
        # check for open multiplayer game
        for i in range(0, len(Server.games)):
            if added == False and Server.games[i].multiplayer == True and len((Server.games)[i].clients) < 2:
                added = True
                Server.games[i].clients.append(socket)
                for client in Server.games[i].clients:
                    Server.multigame_clients.append(client)
                print("sucessfully added client")
                Server.num_games += 1
                print(str(Server.games[i]))
                return Server.games[i]
        #no open game found, create a new one
        if added == False:
            game = Game()
            game.multiplayer = multi
            game.clients.append(socket)
            Server.games.append(game)
            print("Sucessfully created game")
            print(game)
            return game

#Before a connection is closed when a user is finished or quits, this removes
#them from their game and checks to see if the game is empty, if it is the
#game is removed so that more users can enter
def remove_client_from_game(socket):
    adjust = 0
    for i in range(len(Server.games)):
        if socket in Server.games[i - adjust].clients:
            print(str(Server.games[i - adjust]))
            print(str(Server.games[i - adjust].clients))
            Server.games[i - adjust].clients.remove(socket)
            if len(Server.games[i - adjust].clients) == 0:
                del(Server.games[i - adjust])
                adjust += 1
                Server.num_games -= 1
                print('decremented')
#Finds socket associated with multiplayer game user who finished the
#game so that they are removed as well
def close_matching_sock(sock):
    for i in range(0, len(Server.games)):
        if socket in Server.games[i].clients:
            for j in range(0, len(Server.games[i].clients)):
                if Server.games[i].clients[j] != socket:
                    remove_client_from_game(Server.games[i].clients[j])
                    Server.games[i].clients[j].close()

#Allows the server to send messages to a socket which was not the one to
#cause the event. This helps turns to alternate
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

#Allows the server to send data to a socket which was not the one to
#cause the event. This helps turns to alternate
def send_data_to_fellow_socks(socket, message):
    for i in range(0, len(Server.games)):
        if socket in Server.games[i].clients:
            for j in range(0, len(Server.games[i].clients)):
                if Server.games[i].clients[j] != socket:
                    final_msg = message.encode('UTF-8')
                    Server.games[i].clients[j].send(final_msg)
                    print("echoing " + message + " to " + str(Server.games[i].clients[j]))

# Create and register new connection
def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    #Don't allow a fourth person to enter a gameit there are three
    #it is 2 instead of 3 because after this a game is created to be the third
    if Server.num_games > 2:
        print('closing connection to', addr)
        conn.send(bytes(chr(17) + "server-overloaded"))
        conn.close()
        return
    data = Data(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    #register socket so that events are monitored
    sel.register(conn, events, data=data)
    conn.send(bytes(chr(12) + "Game Started"))


    #prepare and set the state of the game
    letters = parse_word(choose_word())
    blanks = make_blanks(letters)
    #{numletters, full word, partial, incorret_num, playing, incorrect letters,
    #    matched, matched_sock}
    Game.game_states[addr] = [len(letters), letters, blanks, 0, True, [], False, None]



# Deal with data from preexisting connections
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    # received data from the client
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        # if data was received
        if len(recv_data) > 0:
            # if the data was a single player game start packet
            if recv_data == b'0':
                print('non-multi')
                # add to game and send first data packet
                add_client_to_game(sock, False)
                msg_flag = chr(0)
                word_size = Game.game_states[sock.getpeername()][0]
                num_incorrect = Game.game_states[sock.getpeername()][3]
                guesses = Game.game_states[sock.getpeername()][2]
                data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses))).encode('UTF-8')
            # if the data was a multi player game start packet
            elif recv_data == b'2':
                print("multi")
                #add to game
                game = add_client_to_game(sock, True)
                # if connected to another player send data, otherwise tell to wait
                if len(game.clients) < 2:
                    Game.game_states[sock.getpeername()][7] = key
                    data.outb += bytes(chr(27) + 'Waiting for another player!')
                else:
                    for client in game.clients:
                        Game.game_states[sock.getpeername()] = Game.game_states[client.getpeername()]

                    data.outb += bytes(chr(16) + 'Players Matched!')
                    #send data to second player in game to get it started
                    msg_flag = chr(0)
                    word_size = Game.game_states[sock.getpeername()][0]
                    num_incorrect = Game.game_states[sock.getpeername()][3]
                    guesses = Game.game_states[sock.getpeername()][2]
                    data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses))).encode('UTF-8')
                    send_message_to_fellow_socks(sock, "waiting for other player to guess")
            # if packet was not game start it is a data packet
            else:
                #if the socket it is coming from is single player
                if sock not in Server.multigame_clients:
                    #get the guess sent in
                    data_len = int(recv_data[0])
                    in_data = recv_data[1]
                    letters = Game.game_states[sock.getpeername()][1]
                    #check for matched
                    correct = False
                    for i in range(len(letters)):
                        if letters[i] == in_data:
                            Game.game_states[sock.getpeername()][2][i] = letters[i]
                            correct = True
                    # if guess was incorrect
                    if correct == False:
                        Game.game_states[sock.getpeername()][5].append(in_data)
                        Game.game_states[sock.getpeername()][3] += 1
                        # check if too many incorrect guesses
                        if Game.game_states[sock.getpeername()][3] > 6:
                            #game over
                            #send last data packet
                            msg_flag = chr(0)
                            word_size = Game.game_states[sock.getpeername()][0]
                            num_incorrect = Game.game_states[sock.getpeername()][3]
                            guesses = Game.game_states[sock.getpeername()][2]
                            incorrect = str(''.join(Game.game_states[sock.getpeername()][5]))
                            data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect).encode('UTF-8')
                            #send loss and game over messages
                            data.outb += bytes(chr(9) + 'YOU LOSE!')
                            data.outb += bytes( chr(10) + 'GAME OVER!')
                            Game.game_states[sock.getpeername()][4] = False;
                            remove_client_from_game(sock)
                            return
                        #send update to player for next guess
                        msg_flag = chr(0)
                        word_size = Game.game_states[sock.getpeername()][0]
                        num_incorrect = Game.game_states[sock.getpeername()][3]
                        guesses = Game.game_states[sock.getpeername()][2]
                        incorrect = str(''.join(Game.game_states[sock.getpeername()][5]))
                        data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect).encode('UTF-8')
                    # if guess was correct
                    else:
                        # check to see if all letters are now correct
                        all_correct = True
                        for i in range(len(letters)):
                            if Game.game_states[sock.getpeername()][2][i] != letters[i]:
                                all_correct = False
                        #it they are the game is over
                        if all_correct == True:
                            #send last data packet and the game over messages
                            msg_flag = chr(0)
                            word_size = Game.game_states[sock.getpeername()][0]
                            num_incorrect = Game.game_states[sock.getpeername()][3]
                            guesses = Game.game_states[sock.getpeername()][2]
                            incorrect = str(''.join(Game.game_states[sock.getpeername()][5]))
                            data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect).encode('UTF-8')
                            data.outb += bytes(chr(8) + 'YOU WIN!')
                            data.outb += bytes(chr(10) + 'GAME OVER!')
                            Game.game_states[sock.getpeername()][4] = False;
                            remove_client_from_game(sock)
                        #otherwise send an update so they can continue guessing
                        else:
                            msg_flag = chr(0)
                            word_size = Game.game_states[sock.getpeername()][0]
                            num_incorrect = Game.game_states[sock.getpeername()][3]
                            guesses = Game.game_states[sock.getpeername()][2]
                            incorrect = str(''.join(Game.game_states[sock.getpeername()][5]))
                            data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect).encode('UTF-8')
                # multi player client sent in packet
                else:
                    #get data from guess
                    data_len = int(recv_data[0])
                    in_data = recv_data[1]
                    letters = Game.game_states[sock.getpeername()][1]
                    #check whether or not the guess was correct
                    correct = False
                    for i in range(len(letters)):
                        if letters[i] == in_data:
                            Game.game_states[sock.getpeername()][2][i] = letters[i]
                            correct = True
                    # let them know the outcome and tell them to wait
                    data.outb += bytes((chr(8)+"Correct!") if correct else (chr(12) + "Incorrect :("))
                    data.outb += bytes(chr(21) + "Other players turn...")
                    #if it was incorrect
                    if correct == False:
                        #add gues to list of incorrect guesses
                        Game.game_states[sock.getpeername()][5].append(in_data)
                        Game.game_states[sock.getpeername()][3] += 1
                        #check if too many incorrect guesses
                        if Game.game_states[sock.getpeername()][3] > 6:
                            #game over
                            # similar to single player logic but with 2 clients using the
                            #      helper methods for fellow_sock
                            msg_flag = chr(0)
                            word_size = Game.game_states[sock.getpeername()][0]
                            num_incorrect = Game.game_states[sock.getpeername()][3]
                            guesses = Game.game_states[sock.getpeername()][2]
                            incorrect = str(''.join(Game.game_states[sock.getpeername()][5]))
                            data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect).encode('UTF-8')
                            data.outb += bytes(chr(9) + 'YOU LOSE!')
                            data.outb += bytes(chr(10) + 'GAME OVER!')
                            Game.game_states[sock.getpeername()][4] = False;

                            msg_flag = chr(0)
                            word_size = Game.game_states[sock.getpeername()][0]
                            num_incorrect = Game.game_states[sock.getpeername()][3]
                            guesses = Game.game_states[sock.getpeername()][2]
                            incorrect = str(''.join(Game.game_states[sock.getpeername()][5]))
                            send_data_to_fellow_socks(sock, str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect)
                            send_message_to_fellow_socks(sock, 'YOU LOSE!')
                            send_message_to_fellow_socks(sock, 'GAME OVER!')
                            close_matching_sock(sock)
                            remove_client_from_game(sock)
                            return
                        # send update
                        msg_flag = chr(0)
                        word_size = Game.game_states[sock.getpeername()][0]
                        num_incorrect = Game.game_states[sock.getpeername()][3]
                        guesses = Game.game_states[sock.getpeername()][2]
                        incorrect = str(''.join(Game.game_states[sock.getpeername()][5]))
                        send_data_to_fellow_socks(sock, str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect)
                    #if the guess was correct
                    else:
                        # check for end condition
                        all_correct = True
                        for i in range(len(letters)):
                            if Game.game_states[sock.getpeername()][2][i] != letters[i]:
                                all_correct = False
                        # if they completed the word
                        if all_correct == True:
                            #send out update packets and also game over messages
                            msg_flag = chr(0)
                            word_size = Game.game_states[sock.getpeername()][0]
                            num_incorrect = Game.game_states[sock.getpeername()][3]
                            guesses = Game.game_states[sock.getpeername()][2]
                            incorrect = str(''.join(Game.game_states[sock.getpeername()][5]))
                            data.outb += (str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect).encode('UTF-8')
                            data.outb += bytes(chr(8) + 'YOU WIN!')
                            data.outb += bytes(chr(10) + 'GAME OVER!')
                            Game.game_states[sock.getpeername()][4] = False;

                            msg_flag = chr(0)
                            word_size = Game.game_states[sock.getpeername()][0]
                            num_incorrect = Game.game_states[sock.getpeername()][3]
                            guesses = Game.game_states[sock.getpeername()][2]
                            incorrect = str(''.join(Game.game_states[sock.getpeername()][5]))
                            send_data_to_fellow_socks(sock, str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect)
                            send_message_to_fellow_socks(sock, 'YOU WIN!')
                            send_message_to_fellow_socks(sock, 'GAME OVER!')
                            close_matching_sock(sock)
                            remove_client_from_game(sock)
                        # not all correct
                        else:
                            #update message
                            msg_flag = chr(0)
                            word_size = Game.game_states[sock.getpeername()][0]
                            num_incorrect = Game.game_states[sock.getpeername()][3]
                            guesses = Game.game_states[sock.getpeername()][2]
                            incorrect = str(''.join(Game.game_states[sock.getpeername()][5]))
                            send_data_to_fellow_socks(sock, str(msg_flag) + str(word_size) + str(num_incorrect) + str(''.join(guesses)) + incorrect)
        #if data received was empty
        else:
            print('closing connection to', data.addr)
            remove_client_from_game(sock)
            Game.game_states.pop(sock.getpeername())
            sel.unregister(sock)
            sock.close()

    # sending data to the socket from data.outb
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


#main function of the server
#sets up the connection to listen for incoming connection requests
if __name__ == '__main__':
    # IP address of the shuttle3 gatech server
    host = '130.207.114.28'
    port = int(sys.argv[1])        # The port used by the server

    sel = selectors.DefaultSelector()



    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))
    lsock.listen(10)
    print('listening on', (host, port))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)
    # continue to listen and deal with new and old connection communications
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)










