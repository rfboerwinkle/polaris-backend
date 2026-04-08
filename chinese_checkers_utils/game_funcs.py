from constants import  JUMPS as jumps, MOVES as moves
from collections import deque

# return True if the move is valid else False
# see valid_move function for parameter info
# dont export this
def valid_bfs(piece_locations: dict[int, list[int]], start_space: int, end_space:int) -> bool:

    piece_on_spot: dict[int, bool] = { i:False for i in range(121)}
    for id, position_list in piece_locations.items():
        for p in position_list:
            piece_on_spot[p] = True

    visited = set()
    queue = deque([start_space])


    while queue:
        node = queue.popleft()
        if node in visited:
            continue

        if node == end_space:
            return True

        visited.add(node)

        for jump_over, land_space in jumps[node]:
            if piece_on_spot[jump_over] and not piece_on_spot[land_space]:
                queue.append(land_space)

    return False



#TODO: Should we validate the position is legal too (are the multiple pieces on one spot)
# return True if the move is valid else False
# playerID: 0-5
# piece locations: dict - key: player ID, value: 10 ints for piece locations
# start_space: where the piece moved from (0-120)
# end_space: where the piece moved to (0-120)
def valid_move(piece_locations: dict[int, list[int]], 
               playerID: int, start_space: int, end_space:int) -> bool:
    try:
        if start_space > 120 or start_space < 0 or end_space > 120 or end_space < 0:
            return False
        
        if playerID > 5 or playerID < 0:
            return False
        
        if start_space == end_space:
            return False
        
        #check if the player doesn't actually have a piece there
        if start_space not in piece_locations[playerID]:
            return False
        
        #check if the end space is already occupied 
        for id, locations in piece_locations.items():
            if start_space in locations:
                return False
        
        if end_space in moves[start_space]:
            return True
        
        return valid_bfs(piece_locations, start_space, end_space)

    
    except Exception as e:
        return False