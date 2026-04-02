# This file has a class to hold a particular game. Feel free to implement more
# things onto it. It also has a class for a player. I'm not sure what we want
# in it, kind of up to you guys. For right now, it's just some temporary stuff.

# ALSO this code might be really bad, I haven't actually tried it. It's mostly
# just here to start laying out the Game and Player classes. I will need to use
# them in the interface with the engine.

class Player:
    def __init__(self, name:str, is_bot:bool) -> None:
        self.name = name
        self.is_bot = is_bot

class Game:
    # This has been ripped from the engine code.
    default_start_points = (
        (6,7,8,9,0,1,2,3,4,5),
        (19,32,44,55,20,21,22,33,34,45),
        (74,84,95,107,85,96,97,108,109,110),
        (111,112,113,114,115,116,117,118,119,120),
        (65,76,88,101,75,86,87,98,99,100),
        (13,25,36,46,10,11,12,23,24,35),
    )

    # The length of player_list must be equal to 6. For games with fewer
    # players, add in padding players with a name of "". This is so we can know
    # the positions of the players.
    def __init__(self, player_list:list[Player]) -> None:
        self.player_list = player_list
        # Number of players who started off in the game.
        self.original_count = 0
        # List of indexes into player_list of people who have not been eliminated.
        self.cur_players = []
        # List of lists of board positions. When a player is eliminated, their
        # list gets set to an empty list. Indices of players who were never in
        # the game also have empty lists.
        self.pieces = []
        # This corresponds to an index within player_list. It will never be set
        # to a player who has been eliminated.
        self.turn = -1
        for i,player in enumerate(player_list):
            if player.name == "":
                self.pieces.append([])
                continue
            if self.turn == -1:
                self.turn = i
            self.original_count += 1
            self.cur_players.append(i)
            self.pieces.append(list(Game.default_start_points[i]))

    def eliminate_player(self, player_name:str) -> None:
        for i,player in enumerate(self.player_list):
            if player.name == player_name:
                self.cur_players.remove(i)
                self.pieces[i] = []

    # source and dest are board positions. Currently does no checking of anything.
    def make_move(self, source:int, dest:int) -> None:
        for p_set in self.pieces:
            if source in p_set:
                p_set[p_set.index(source)] = dest
        self.turn += 1
        self.turn %= 6
        # To prevent infinite loops.
        for i in range(7):
            if i == 6:
                print("too many loops of turn updating")
                break
            if self.turn in self.cur_players:
                break
            self.turn += 1
            self.turn %= 6
