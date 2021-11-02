
from collections import Counter

from shape import S


_bottom = [[i, 30] for i in range(10)]  # bottom
_lateral = [[0, i] for i in range(30)]  # left
_lateral.extend([[10 - 1, i] for i in range(30)])


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


# Rank the move based on different criteria
def validate_move(gamestate, piece, high_points):
    lines = 0
    points = 0
    for item, count in Counter(y for _, y in gamestate + piece).most_common():
        if count == 8 and item!= 30:
            lines += 1
        

    points += (lines ** 2)
    
    print("FROM LINES", points)
    tmp1 = points
    tmp = gamestate + piece
    x = []
    for i in piece:
        if i[0] not in x:
            x.append(i[0])

    
    #print("X",x)
    for xx in x:
        t = [b[1] for b in tmp if b[0] == xx ]
        
        t.sort()
        #print("t", t)
        for i in range(len(t)-1):
            if t[i+1] - t[i] > 1:
                points-= t[i+1] - t[i]
    print("FROM HOLES", points - tmp1)
    tmp1 = points
    print(high_points)
    tmp2 = [i for i in high_points]
    for p in piece:
        tmp2[ p[0] -1 ] = p[1] if p[1] < high_points[ p[0] -1 ] else high_points[ p[0] -1 ]
    print(tmp2)
    min = 30
    desv = 0
    for column in tmp2:
        if min - column > desv:
            desv = min - column
            min = column
    points -= desv
    print("FROM HEIGHT", points - tmp1)
    return points
        

# Check if a piece can be there
def valid(piece, gamestate):
        return not any(
            [piece_part in grid for piece_part in piece]
        ) and not any(
            [piece_part in gamestate for piece_part in piece]
        )

# Calculate the possible move at a certain column
def calculate_move(gamestate, piece, column, high_points):

    t = [block[1] for block in gamestate if block[0] == column]

    if not t:
        pivot = 29
    else:
        pivot = min(t)
    n = 1
    #print("Pivot", pivot)
    for n in range(1,5):
        tmp = [[p[0] + column,p[1] + pivot - n] for p in piece ]

        if valid(tmp,gamestate):
            #print(tmp)
            #print(gamestate)
            #print(validate_move(gamestate,tmp))
            return validate_move(gamestate,tmp, high_points), tmp




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

    score = None
    n = 0
    a = []
    for piece in piece_r:
        #print("P",piece)
        for i in range(1,9):
            print("I:", i)
            s = calculate_move(gamestate,piece,i, high_points)
            print(s)
            if score is None and s is not None:
                score = s[0]
                a = [s[1], n, s[0]]
            elif s is not None and score < s[0]:
                score = s[0]
                a = [s[1], n, s[0]]
        n += 1
    print(a)
    return a






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
                        print("TYPE:",piece_type)
                        # get the rotations of the current piece
                        c_piece = piece_rotations.get(piece_type)
                        # add the floor border to calculate HOLES based on it
                        tmp = state["game"] + [[i,30] for i in range(1,9)] 
                        obj = tetris(c_piece, tmp, high_points)
                        print("OOOBJ", obj)
                    else:
                        # TODO Make bot generate all the output in one go
                        if obj[1] != 0:
                            print(obj[1])
                            key = "w" 
                            obj[1] -= 1
                        else:
                            print("Local: ",state["piece"])
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
