
from collections import Counter

from shape import S


_bottom = [[i, 30] for i in range(10)]  # bottom of the game viewer
_lateral = [[0, i] for i in range(30)]  # left of the game viewer
_lateral.extend([[10 - 1, i] for i in range(30)])

# grid = game boundaries
grid = _bottom + _lateral
#print(grid)

# Map with the rotations of each piece
piece_rotations = {
    "i": [
        [
            [0,0],[1,0],[2,0],[3,0]
        ],
        [
            [0,0],[0,-1],[0,-2],[0,-3]
        ]
    ],
    "o": [
        [[0,0],[1,0],[0,-1],[1,-1]]
    ],
    "s": [
        [
            [0,0],[0,-1],[-1,-1],[-1,-2]
        ],
        [
            [0,0],[1,0],[1,-1],[2,-1]
        ],
    ],
    "z": [
        [
            [0,0],[0,-1],[1,-1],[1,-2]
        ],
        [
            [0,0],[1,0],[1,1],[2,1]
        ],
    ],
    "l": [
        [
            [0,0],[1,0],[0,-1],[0,-2]
        ],
        [
            [0,0],[0,-1],[1,-1],[2,-1]
        ],
        [
            [0,0],[0,-1],[0,-2],[-1,-2]
        ],
        [
            [0,0],[1,0],[2,0],[2,-1]
        ],
    ],
    "j": [
        [                                        
            [0,0],[0,-1],[0,-2],[1,-2]
        ],
        [
            [0,0],[0,-1],[-1,-1],[-2,-1]
        ],                                     
        [
            [0,0],[1,0],[1,-1],[1,-2]
        ],
        [
            [0,0],[1,0],[2,0],[0,-1]            
        ],  
    ],
    "t": [
        [
            [0,0],[0,-1],[0,-2],[1,-1]
        ],
        [
            [0,0],[1,0],[2,0],[1,1]
        ],
        [
            [0,0],[0,-1],[0,-2],[-1,-1]
        ],
        [
            [0,0],[1,0],[2,0],[1,-1]
        ]
    ]
}

# ---------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

# Rank the move based on different criteria
def validate_move(gamestate, piece, high_points):

    lines = 0 # number of lines completed with a given piece placement
    points = 0 # score of a given piece placement

    ### ------ ENCOURAGE COMPLETING LINES ------
    # checking if any lines are complete
    for item, count in Counter(y for _, y in gamestate + piece).most_common():
        if count == 8 and item!= 30:
            lines += 1 # if so, increment "lines"

    # the point score increments exponentially according to the number of lines completed at once by a piece placement
    points += (lines ** 2)

    ### ------ DISCOURAGE HOLES ------
    allBlocks = gamestate + piece # blocks of all already set pieces + blocks of new piece (all blocks in board)
    print("ALL BLOCKS: ", allBlocks)
    Xcoords = []
    for block in piece:
        if block[0] not in Xcoords:
            Xcoords.append(block[0])
    
    for x in Xcoords:
        yCoords = [block[1] for block in allBlocks if block[0]==x ]
        
        yCoords.sort()
        for i in range(len(yCoords)-1):
            if yCoords[i+1] - yCoords[i] > 1: # if there's a hole
                points-= yCoords[i+1] - yCoords[i]

    ### ------ ENCOURAGE FLAT PLAYING STYLE ------
    columnPeaks = [i for i in high_points]
    # see what high_points would look like with new piece placement
    for block in piece:
        columnPeaks[ block[0]-1 ] = block[1] if block[1] < high_points[ block[0]-1 ] else high_points[ block[0]-1 ]
    minVal = 30
    desv = 0
    for column in columnPeaks:
        if minVal - column > desv:
            desv = minVal - column
            minVal = column
    points -= desv

    return points
        

# Check if a piece placement is valid (doesn't overlap with anything)
def valid(placement, gamestate):
    # check if the piece placement doesn't overlap with the game boundaries
    return not any(
        [block in grid for block in placement]
    # check if the piece placement doesn't overlap with any already set pieces
    ) and not any(
        [block in gamestate for block in placement]
    )

# Calculate the possible move at a certain column
def calculate_move(gamestate, piece, column, high_points):

    ### GAMESTATE: list of lists
    ### [ [columnNumber, height], [columnNumber, height], [columnNumber, height], ...  ], for the 8 columns
    ### if column 5 has 3 stacked blocks, all [5,30], [5,29] and [5,28] (the used up blocks) will be in the list of lists
    ### this allows us to see when a full line is formed

    ### PIECE: list of 4 lists (each of the smaller lists is the position of one of the piece's blocks)
    ### the piece is already in one of its positions, see the big map on top with the rotations of each type of piece

    blocksInColumn = [block[1] for block in gamestate if block[0] == column]

    if not blocksInColumn: # column is empty
        pivot = 29 # so we're on the floor
    else: # column already has blocks
        pivot = min(blocksInColumn) # get the highest (y axis goes downwards)
        
    # we're gonna try to find a piece placement now. a piece is 4 blocks tall maximum
    # we try to place it as it is. if it's not possible (because it's overlapping with pieces already in the game), we
    # adjust it one block up (because if it overlaps, it overlaps at the bottom)
    # range(1,5) = [1,2,3,4], four possible adjustments (bc of the max piece height)
    for adjust in range(1,5): 
        # block = block in piece (it's a list with 2 coordinates for that block)
        # block[0]=x, block[1]=y
        #               x + column       y + pivot - n
        # the placement is given in absolute coords in the game viewer
        placement = [ [ block[0]+column, block[1]+pivot-adjust ] for block in piece ]

        if valid(placement,gamestate): # check if the new piece doesn't overlap with already set game pieces for this placement
            # "validate_move" ranks the move based on different criteria
            # so we're returning the tuple (<ranking>,<placement>), so we can later choose the best one
            return validate_move(gamestate,placement,high_points), placement

"""
gs = [[1,28],[2,28],[3,29],[3,28],[4,29],[4,28],[4,27],[5,27],[6,29],[6,28],[7,28],[5,28]]

piece_r = [
    [[0,0],[1,0],[2,0],[2,-1]],
    [[0,0],[0,-1],[0,-2],[-1,-2]],
    [[0,0],[0,-1],[1,-1],[2,-1]],
    [[0,0],[1,0],[0,-1],[0,-2]]
]
a = []"""

def findState(state, game):
    for block in game:
        state[ block[0]-1 ] = block[1]
    return state

def discover_i(piece):
    if piece != None:
        x = piece[0][0]
        y = piece[0][1]
        b = [True,True]
        for coor in piece:
            if coor[0] != x:
                b[0] = False
            if coor[1] != y:
                b[1] = False
        return b  
    return [False,False]

def what_is_this_pokemon(piece):
    """I'm sure this can be improved. Base 3 maybe?"""
    is_i=discover_i(piece)
    if is_i[0] or is_i[1]:
        return "i"
    #print(discover_i(piece))
    piece_code=[(piece[0][0]-piece[1][0], piece[0][1]-piece[1][1]),((piece[2][0]-piece[3][0], piece[2][1]-piece[3][1]))]
    #print("current piece has a code of: "+str(piece_code))
    if piece_code[0]==(-1,0):
        if piece_code[1]==(0,-1):
            return "j"
        if piece_code[1]==(-1,0):
            return "o"
    if piece_code[0]==(0,-1):
        if piece_code[1]==(-1,0):
            return "l"
        if piece_code[1]==(0,-1):
            return "s"
        if piece_code[1]==(1,-1):
            return "t"
    if piece_code[0]==(1,-1):
        return "z"

# get the best possible move of a given piece
def tetris(piece_r, gamestate, high_points):
    ### PIECE_R: piece rotations
    ### in order to assess which is the best move for a new piece, we need to take into account all of the possible
    ### placements of said piece, in all its possible positions (rotations)
    ### if we're trying to place a T piece (for example), piece_r will be the list of lists containing all of T's
    ### possible rotations (this information is taken directly from the big rotations map on top of the code)

    highestScore = None # score of the highest scoring position for this piece
    positionIdx = 0 # index of the position in piece_r (tells us which position we're talking about)
    bestPosition = [] # information about the highest scoring position, format = [<score>,<positionIdx>,<piece placement>]
    for piece in piece_r: # for each rotation of the piece
        for column in range(1,9): # for each column
            piece_score = calculate_move(gamestate, piece, column, high_points) # piece_score = (<score>,<piece placement>)
            # ------ store the information of the highest scoring position in bestPosition ------
            if highestScore is None and piece_score is not None:
                highestScore = piece_score[0]
                bestPosition = [piece_score[1], positionIdx, piece_score[0]]
            elif piece_score is not None and highestScore < piece_score[0]:
                highestScore = piece_score[0]
                bestPosition = [piece_score[1], positionIdx, piece_score[0]]
            # -----------------------------------------------------------------------------------
        positionIdx += 1
    return bestPosition

# ---------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------

import asyncio
import getpass
import json
import os

import websockets

# Next 4 lines are not needed for AI agents, please remove them from your code!
import pygame 

program_icon = pygame.image.load("data/icon2.png")
pygame.display.set_icon(program_icon)


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        # Next 3 lines are not needed for AI agent
        SCREEN = pygame.display.set_mode((299, 123))
        SPRITES = pygame.image.load("data/pad.png").convert_alpha()
        SCREEN.blit(SPRITES, (0, 0))

        n = 0
        high_points = [30 for i in range(8)] # The height of each column
        obj = None
        while 1:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server
                key = ""
                if not state["piece"]:
                    obj = None
                else:
                    if not obj:
                        # get the high_points of the current board
                        if n != 0:
                            n += 1
                            high_points = findState(high_points, state["game"])

                        # find out what the current piece is 
                        piece_type = what_is_this_pokemon(state["piece"])
                        #print("TYPE:",piece_type)
                        # get the rotations of the current piece
                        c_piece = piece_rotations.get(piece_type)
                        # add the floor border to calculate HOLES based on it
                        tmp = state["game"] + [[i,30] for i in range(1,9)] 
                        obj = tetris(c_piece, tmp, high_points)
                        #print("OOOBJ", obj)
                    else:
                        # TODO Make bot generate all the output in one go
                        if obj[1] != 0:
                            #print(obj[1])
                            key = "w" 
                            obj[1] -= 1
                        else:
                            #print("Local: ",state["piece"])
                            left = 0
                            right = 0
                            for p1 in state["piece"]:
                                for p2 in obj[0]:
                                    if p1[0] < p2[0]:
                                        right += 1
                                    elif p1[0] > p2[0]:
                                        left += 1

                            if left > right:
                                key = "a"
                            elif right > left:
                                key = "d"
                            else:
                                key = "s"

                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server - you must implement this send in the AI agent
                
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

            # Next line is not needed for AI agent
            pygame.display.flip()

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
