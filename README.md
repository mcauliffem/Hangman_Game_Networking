# CS 3251 Networking: Programming Project 2
Partners: Matt McAuliffe and Kyle Suter

# Hangman_Game_Networking
This client-server code allows the communication of computers with a server hosting a the game hangman, which can be played through the command line.

The game is built upon establishing TCP connections and using the accept() method on the server side to map different clients to different ports.

How to run our code:
    ./server.py <Port>
    ./client.py <ServerIP> <Port>

The client will then ask if the game will be multiplayer
    y will wait for another player and n will start single player mode.
Simply follow the instructions as they are displayed in the client terminal.