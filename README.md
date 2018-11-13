# CS 3251 Networking: Programming Project 2
Partners: Matt McAuliffe and Kyle Suter

# Hangman_Game_Networking
This client-server code allows the communication of computers with a server hosting a the game hangman, which can be played through the command line.

The game is built upon establishing TCP connections and using the accept() method on the server side to map different clients to different ports.

How to run our code:
run server on shuttle server 3 for connections to work, as IP is set to 130.207.114.28 in server.py main function (could change to IP of your preferred server)
    ./server.py <Port>
    ./client.py <130.207.114.28> <Port>

The client will then ask if the game will be multiplayer
    y will wait for another player
    n will start single player mode.
Simply follow the instructions as they are displayed in the client terminal.