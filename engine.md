# Backend Engine

## Installation

Clone the repo:
```bash
git clone https://github.com/bdsriver/Chinese_Checkers_Engine.git
```
Build the engine. You need gcc/gnu 23 or later:
```bash
cd Chinese_Checkers_Engine
make backend-build
```
Now you can run it with ```./engine```. You should be able to pipe standard input/output.

## Interface

The input for the engine is a position. You can also just give it ```quit``` to make it stop.

### Input
The input format is as follows with different parameters separated by spaces:
```
<difficulty/bot type> <original player amount> <Current player amount> <Current player turn> <piece positions as specified below>
```
**Difficulty/Bot Type:** Currently this hasn't been implemented so just put anything here for now but it will be a string.

**Original Player Amount:** How many players the game started with (2,3,4, or 6).

**Current Player Amount:** How many players still have their pieces on the board (1-6). 
Keep in mind a player still has their pieces on the board if they win the game and we do not remove their pieces.

**Current Player Turn:** Whose turn it is to move (0-5). Player 0 always moves first, followed by player 1 and so on.

**Piece Positions:** For each player with pieces on the board, 11 space separated integers. The first integer is their id (0-5). 
The next 10 are the positions of each of their pieces. The piece positions section for player 0 at their start position looks like:
```
0 0 1 2 3 4 5 6 7 8 9
```
The order of what piece positions or player ids are put in does not matter.

**Example**

Here is what the entire input string could look like for the starting position of a 2 player game with "easy" difficulty bot:
```
easy 2 2 0 0 0 1 2 3 4 5 6 7 8 9 1 111 112 113 114 115 116 117 118 119 120
```
This is the exact same and makes no difference to the engine:
```
easy 2 2 0 1 116 112 120 111 115 114 117 118 119 113 0 9 8 7 6 5 4 3 2 1 0
```

### Output
The output is the new position after the bot makes a move in the input position. We can also change this to include the specific move that was made. 

Unless there is an error, the output will be as follows:
```
<winning player>:<piece positions of player 0>:<piece positions of player 1>:...
```
**Winning Player:** This will always be ```-1``` unless a player won (moved all their pieces into the end zone). 
If a player won, it will be their id (0-5).

**Piece Positions:** This is the same as the input. For each player with pieces on the board, 11 space separated integers. The first integer is their id (0-5). 
The next 10 are the positions of each of their pieces. The piece positions section for player 0 at their start position looks like:
```
0 0 1 2 3 4 5 6 7 8 9
```
There will only be one change from the input, that being the piece that moved. Unlike the input, each group of piece positions is separated by colons.
The winning player is also separated by a colon.

**Example**
If the bot determines, given the starting position of 2 players (from input section), that it should move the piece of spot 5 to spot 18, the output will look like this:
```
-1:0 0 1 2 3 4 6 7 8 9 18:1 111 112 113 114 115 116 117 118 119 120
```

**Errors**

If there was an error in the input, the program will not crash. It will output:
```
<error message>
```
For example, it will say if the input had multiple pieces on the same spot or if the amount of players the same started with doesn't make sense.

# Frontend Engine
TBD, it will have defined member functions of the engine wasm object instead of CLI. 
Expect a a similar interface as the backend using arrays instead of separator characters.
