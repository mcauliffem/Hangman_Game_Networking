import select
import socket
import sys
import time

######################## Client.py ########################################
# Contributors: Matt McAuliffe and Kyle Suter                             #
# CS 3251: Networking, Programming Project 2, Fall 2018                   #
###########################################################################

class Message:
    my_message = ""
    playing = False
    incorrect_guesses = []

def start_connection(host, port):
    server_addr = (host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    return sock

def send_data_to_server(message, socket):
    message_converted = message.encode('UTF-8')
    message_length = str(len(message)).encode('UTF-8')
    final_message = b"".join([message_length, message_converted])
    socket.send(final_message)

def receive_data_from_server(sock):
    data = ""
    while len(data) == 0:
        try:
            data = sock.recv(1024).decode('UTF-8')
        except socket.error as ex:
            if str(ex) == "[Errno 35] Resource temporarily unavailable":
                time.sleep(0)
                continue
            raise ex

    while len(data) != 0:
        msg_flag = int(ord(data[0]))
        if msg_flag == 0:
            word_length = int(data[1])
            num_incorrect = int(data[2])
            word_itself = str(data[3: word_length + 3])
            incorrect_guesses = data[(word_length + 3): (word_length + num_incorrect + 3)]
            data = data[(word_length + num_incorrect + 3):]
            print("\n" + word_itself + "\n" + "Incorrect Guesses: ", end="")
            for letter in incorrect_guesses:
                print(letter, end="")
            print("\n")
            valid_input = False
            guess = ""
            while valid_input == False:
                guess = input("Letter to guess: ")
                if guess == '':
                    print("\n Invalid Input: Please enter a valid letter a-z")
                elif ord(guess) > 122 or ord(guess) < 97:
                    print("\n Invalid Input: Please enter a valid letter a-z")
                elif guess in incorrect_guesses or guess in word_itself:
                    print("\n Input already guessed: guess again")
                else:
                    valid_input = True
            Message.my_message = guess
        else:
            server_message = str(data[1: int(msg_flag) + 1])
            data = data[int(msg_flag) + 1:]
            if server_message == "GAME OVER!":
                print(server_message + "\n")
                sock.close()
                Message.playing = False
            elif server_message == "server-overloaded":
                print(server_message + "\n")
                print("closing connection!\n")
                sock.close()
                Message.playing = False
            else:
                print(server_message + "\n")


if __name__ == "__main__":

    host = sys.argv[1]
    port = int(sys.argv[2])
    my_socket = start_connection(host, port);
    choice = input("Two Player? (y/n): ")
    if choice == "n":
        Message.playing = True
        Message.my_message = "0"
    elif choice == "y":
        Message.playing = True
        Message.my_message = "2"
    else:
        print("closing connection!\n")
        my_socket.close()
        print("connection closed!\n")

    while Message.playing:

        if len(Message.my_message) != 0:
            send_data_to_server(Message.my_message, my_socket)
            Message.my_message = ""

        receive_data_from_server(my_socket)




