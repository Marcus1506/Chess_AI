
# convention: white start at the top

from chess import *
import pygame as p
import sys


LENGTH = 512 # divides neatly by 8
SQR_SIZE = 64
MAX_FPS = 20
IMAGES = {}

def load_images():
    names=['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in names:
        IMAGES[piece]=p.transform.scale(p.image.load("images/" + piece + ".png"), (SQR_SIZE, SQR_SIZE))

def draw_board(screen, valid_moves, selected_start=None):
    colors=[p.Color("white"), p.Color("gray")]
    if selected_start: valid_squares=[[elem[1][0], elem[1][1]] for elem in valid_moves if elem[0][0]==selected_start[0] and elem[0][1]==selected_start[1]]
    for row in range(BOARD_DIM):
        for col in range(BOARD_DIM):
            color=colors[(row+col)%2]
            # here I can set color differently afterwards, to highlight certain things
            p.draw.rect(screen, color, p.Rect(col*SQR_SIZE, row*SQR_SIZE, SQR_SIZE, SQR_SIZE))
            
            if selected_start:
                if row==selected_start[0] and col==selected_start[1]:
                    p.draw.rect(screen, p.Color("yellow", alpha=128), p.Rect(col*SQR_SIZE, row*SQR_SIZE, SQR_SIZE, SQR_SIZE))
                    continue
                if [row, col] in valid_squares:
                    p.draw.rect(screen, p.Color("yellow", alpha=128), p.Rect(col*SQR_SIZE, row*SQR_SIZE, SQR_SIZE, SQR_SIZE))
                

def draw_pieces(screen, board):
    for row in range(BOARD_DIM):
        for col in range(BOARD_DIM):
            piece=board[row,col]
            if piece != None:
                screen.blit(IMAGES[piece.key], p.Rect(col*SQR_SIZE, row*SQR_SIZE, SQR_SIZE, SQR_SIZE))

def draw_game_state(screen, gs, valid_moves, selected_start):
    draw_board(screen, valid_moves, selected_start)
    
    draw_pieces(screen, gs.state())


def main():
    p.init() # maybe initialize before, could lead to problems later
    screen=p.display.set_mode((LENGTH, LENGTH))
    clock=p.time.Clock()
    screen.fill(p.Color("white"))
    gs=chess_board() # id for first gamestate is 0
    gs.reset_board()
    load_images() # get images into memory
    running=True
    sq_selected=() # no square selected initially, keep track of last click, tuple: (row, col)
    player_clicks=[] # two tuples for the player clicks
    selected_start=False
    valid_moves=gs.get_valid_moves()
    
    print(sys.getrecursionlimit())
    
    while running:
        for e in p.event.get():
            if e.type==p.QUIT: # makes it possible to quit
                running=False
            # mouse actions
            elif e.type==p.MOUSEBUTTONDOWN:
                location=p.mouse.get_pos() # (x, y) location of mouse
                col=location[0]//SQR_SIZE
                row=location[1]//SQR_SIZE
                if sq_selected==(row, col): # double click on same square
                    sq_selected=()
                    player_clicks=[]
                else:
                    sq_selected= (row, col)
                    player_clicks.append(sq_selected)
                    if len(player_clicks)==1:
                        selected_start=[row, col]
                if len(player_clicks)==2: # actually perform the move
                    gs.move_piece(player_clicks[0], player_clicks[1])
                    valid_moves=gs.get_valid_moves() # calc new valid_moves when a move is made
                    player_clicks=[] # reset player clicks
                    sq_selected=() # also clear selected to be sure
                    selected_start=False
            elif e.type==p.KEYDOWN:
                if e.key==p.K_z:
                    gs.undo_move()
                
        
        draw_game_state(screen, gs, valid_moves, selected_start)
        
        clock.tick(MAX_FPS) # set max update rate
        p.display.flip() # update entire display to reflect changes
    
    
    p.quit() # good practice to actually close the initialization

if __name__=="__main__":
    main()
    
    
    