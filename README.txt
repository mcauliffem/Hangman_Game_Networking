CS 3251 Networking: Programming Project 2
Partners: Matt McAuliffe and Kyle Suter

Hangman_Game_Networking
__________________________________________________________________________________
This client-server code allows the communication of computers with a server hosting a the game hangman, which can be played through the command line.

The game is built upon establishing TCP connections and using the accept() method on the server side to map different clients to different ports.

Selectors2.py is a file publicly available on the internet as a replacement for the functionality of selectors which is only available in python3. With this code in the same directory as the server and the import selectors2 as selectors statement, we could switch to python 2 with minimal difficulty.

Distribution of work:
    -Single Player
        -Server Side: Matt McAuliffe
        -client Side: Kyle Suter
    -Multi Player
        -Server Side:
            -connection management: Matt McAuliffe
            -Game Class and some logic: Kyle Suter
        -Client side:
            -most code retained from original: Kyle Suter
            -addition of multiplayer and formatting updates: Matt McAuliffe
    -Comments: We both put in a lot of effort and we worked well together

How to run our code:
Run server on shuttle server 3 for connections to work, as IP is set to 130.207.114.28 in server.py main function (could change to IP of your preferred server)
    python server.py <Port>
    python client.py <130.207.114.28> <Port>

The client will then ask if the game will be multiplayer
    y will wait for another player
    n will start single player mode.
Simply follow the instructions as they are displayed in the client terminal.