from __future__ import print_function
import select
import socket
import sys
import time


######################## Client.py ########################################
# Contributors: Matt McAuliffe and Kyle Suter                             #
# CS 3251: Networking, Programming Project 2, Fall 2018                   #
###########################################################################

# holds variables needed in the client code
class Message:
    my_message = ""
    playing = False
    incorrect_guesses = []

# creates the connection to the server
def start_connection(host, port):
    server_addr = (host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    return sock

# sends message data to the socket
def send_data_to_server(message, socket):
    message_converted = message.encode('UTF-8')
    message_length = str(len(message)).encode('UTF-8')
    final_message = b''
    # check for edge case starting messages
    if message == chr(0) or message == chr(2):
        final_message = b"".join([message_converted])
    else:
        final_message = b"".join([message_length, message_converted])
    socket.send(final_message)

# receive the data that is from the server
def receive_data_from_server(sock):
    data = ""
    while len(data) == 0:
        try:
            data = sock.recv(1024).decode('UTF-8')
        except socket.error as ex:
            # ignore common errors which cause programs to crash
            if str(ex) == "[Errno 35] Resource temporarily unavailable":
                time.sleep(0)
                continue
            elif str(ex) == "[Errno 11] Resource temporarily unavailable":
                time.sleep(0)
                continue
            raise ex
    # while there is data to parse through
    while len(data) != 0:
        # get the flag to check what kind of packet it is
        msg_flag = int(ord(data[0]))
        # if it is a data packet
        if msg_flag == 0:
            #parse through the data and output the results to the client
            word_length = int(data[1])
            num_incorrect = int(data[2])
            word_itself = str(data[3: word_length + 3])
            incorrect_guesses = data[(word_length + 3): (word_length + num_incorrect + 3)]
            data = data[(word_length + num_incorrect + 3):]
            spacecount = 0
            print("\n")
            for letter in word_itself:
                print(letter, end="")
                print(" ", end = "")
                if letter == "_":
                    spacecount += 1
            print("\n" + "Incorrect Guesses: ", end="")
            incorrect_count = 0
            for letter in incorrect_guesses:
                incorrect_count += 1
                print(letter, end="")
            print("\n")
            spacecount = 0
            for letter in word_itself:
                if letter == "_":
                    spacecount += 1
            #if the game is not over
            if incorrect_count <= 6 and spacecount != 0:
                valid_input = False
                guess = ""
                # get input from the user
                while valid_input == False:
                    guess = raw_input("Letter to guess: ")
                    #check validity of guess
                    if guess == '':
                        print("\n Invalid Input: Please enter a valid letter a-z")
                    # convert upper to lower case
                    elif ord(guess) > 122 or ord(guess) < 97:
                        if ord(guess) <= 90 or ord(guess) >= 65:
                            guess = chr(ord(guess) + 32)
                            valid_input = True
                        else:
                            print("\n Invalid Input: Please enter a valid letter a-z")
                    elif guess in incorrect_guesses or guess in word_itself:
                        print("\n Input already guessed: guess again")
                    else:
                        valid_input = True
                Message.my_message = guess
        # if the data is a message packet
        else:
            #get the message
            server_message = str(data[1: int(msg_flag) + 1])
            data = data[int(msg_flag) + 1:]
            # check for edge case messages
            if server_message == "GAME OVER!":
                print(server_message + "\n")
                sock.close()
                Message.playing = False
            elif server_message == "server-overloaded":
                print(server_message + "\n")
                sock.close()
                Message.playing = False
            else:
                #print the message
                print(server_message + "\n")


if __name__ == "__main__":
    #setup connection
    host = sys.argv[1]
    port = int(sys.argv[2])
    my_socket = start_connection(host, port);
    #ask for type of game
    choice = raw_input("Two Player? (y/n): ")
    if choice == "n":
        Message.playing = True
        Message.my_message = chr(0)
    elif choice == "y":
        Message.playing = True
        Message.my_message = chr(2)
    else:
        my_socket.close()
    #loop while the client is still playing
    while Message.playing:

        if len(Message.my_message) != 0:
            send_data_to_server(Message.my_message, my_socket)
            Message.my_message = ""

        receive_data_from_server(my_socket)




