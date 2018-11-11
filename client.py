import select
import socket
import sys

def start_connection(host, port):
    server_addr = (host, port)
    print('starting connection to', server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    return sock

def send_data_to_server(message, socket):
    message_converted = message.encode('UTF-8')
    message_length = str(len(message)).encode('UTF-8')
    final_message = b"".join([message_length, message_converted])
    socket.send(final_message)
    print(final_message)

def receive_data_from_server(socket):
    data = (socket.recv(1024)).decode('UTF-8')
    if len(data) != 0:
        msg_flag = data[0]
        if msg_flag == 0:
            word_length = int(data[1])
            num_incorrect = int(data[2])
            word_itself = data[3: word_length + 3]
            incorrect_guesses = data[(word_length + 3): (word_length + num_incorrect + 3)]
            print("\n" + word_itself + "\n" + "Incorrect Guesses: ")
            for letter in incorrect_guesses:
                print(letter)
            print("\n\n")
            valid_input = False
            guess = ""
            while valid_input == False:
                guess = input("Letter to guess: ")
                if ord(guess) > 122 or ord(guess) < 97:
                    print("\n Invalid Input: Please enter a valid letter a-z")
                else:
                    valid_input = True
            my_message = guess
        else:
            server_message = data[1: msg_flag + 1]
            print(server_message)


if __name__ == "__main__":

    host = sys.argv[1]
    port = int(sys.argv[2])
    my_message = ""
    my_socket = start_connection(host, port);
    playing = False
    choice = input("Ready to start game? (y/n): ")
    if choice == "y":
        playing = True
        my_message = "0"
    else:
        print("closing connection!\n")
        my_socket.close()
        print("connection closed!\n")

    while playing:

        if len(my_message) != 0:
            send_data_to_server(my_message, my_socket)
            my_message = ""

        receive_data_from_server(my_socket)




