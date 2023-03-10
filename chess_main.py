
# convention: white start at the top

from chess_module import *
import pygame as p
import sys
from MiniMaxAlgo import find_good_move
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
import random

LENGTH=512 # divides neatly by 8
SQR_SIZE=64
MAX_FPS=20
IMAGES={}

WHITE_AI=True
BLACK_AI=False


def load_images():
    names=['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in names:
        IMAGES[piece]=p.transform.scale(p.image.load("images/" + piece + ".png"), (SQR_SIZE, SQR_SIZE))

def draw_board(screen, valid_moves, selected_start=None):
    colors=[p.Color("white"), p.Color("gray")]
    if selected_start: valid_squares=[[move.end_row, move.end_col] for move in valid_moves if move.start_row==selected_start[0] and move.start_col==selected_start[1]]
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

def draw_endgame_message(screen, gs):
    if gs.checkmate:
        if gs.whites_turn:
            winner="Black"
        else:
            winner="White"
        font1=p.font.Font(None, 50)
        text1=font1.render(winner+" has won the game!", True, (0,0,0))
        text1_rect=text1.get_rect()
        text1_rect.centerx=screen.get_rect().centerx
        text1_rect.centery=screen.get_rect().centery-20
        screen.blit(text1, text1_rect)
        
        font2=p.font.Font(None, 30)
        text2=font2.render("Press ENTER to restart", True, (0,0,0))
        text2_rect=text2.get_rect()
        text2_rect.centerx=screen.get_rect().centerx
        text2_rect.centery=screen.get_rect().centery+20
        screen.blit(text2, text2_rect)
    elif gs.stalemate:
        font1=p.font.Font(None, 50)
        text1=font1.render("Stalemate, its a draw!", True, (0,0,0))
        text1_rect=text1.get_rect()
        text1_rect.centerx=screen.get_rect().centerx
        text1_rect.centery=screen.get_rect().centery-20
        screen.blit(text1, text1_rect)
        
        font2=p.font.Font(None, 30)
        text2=font2.render("Press ENTER to restart", True, (0,0,0))
        text2_rect=text2.get_rect()
        text2_rect.centerx=screen.get_rect().centerx
        text2_rect.centery=screen.get_rect().centery+20
        screen.blit(text2, text2_rect)

def draw_game_state(screen, gs, valid_moves, selected_start):
    draw_board(screen, valid_moves, selected_start)
    
    draw_pieces(screen, gs.get_board())
    
    if len(valid_moves)==0:
        draw_endgame_message(screen, gs)

def main():
    p.init() # maybe initialize before, could lead to problems later
    screen=p.display.set_mode((LENGTH, LENGTH))
    p.display.set_caption("CHESS AI - PROJECT")
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
    
    sys.setrecursionlimit(1200) # 1000 is standard
    
    evaluator=load_model("data/large_models/model_mae_3_layer_tanh_relu_wide_uniform")
    
    while running:
        human_turn=(gs.whites_turn and not WHITE_AI) or ( not gs.whites_turn and not BLACK_AI)
        for e in p.event.get():
            if e.type==p.QUIT: # makes it possible to quit
                running=False
            # mouse actions

            elif e.type==p.MOUSEBUTTONDOWN:
                if human_turn:
                    location=p.mouse.get_pos() # (x, y) location of mouse
                    col=location[0]//SQR_SIZE
                    row=location[1]//SQR_SIZE
                    if sq_selected==(row, col): # double click on same square
                        sq_selected=()
                        player_clicks=[]
                    else:
                        sq_selected=(row, col)
                        player_clicks.append(sq_selected)
                        if len(player_clicks)==1:
                            selected_start=[row, col]
                    if len(player_clicks)==2: # actually perform the move
                        desired_move=move(player_clicks[0], player_clicks[1], gs.get_board())
                        if desired_move in valid_moves:
                            gs.move_piece(desired_move)
                            valid_moves=gs.get_valid_moves() # calc new valid_moves when a move is made
                            player_clicks=[] # reset player clicks
                            sq_selected=() # also clear selected to be sure
                            selected_start=False
                            print(valid_moves)
                        else:
                            print("invalid move")
                            player_clicks=[]
                            sq_selected=()
                            selected_start=False
            elif e.type==p.KEYDOWN:
                if e.key==p.K_z and gs.move_log:
                    gs.undo_move()
                    valid_moves=gs.get_valid_moves()
                if e.key==p.K_RETURN and len(valid_moves)==0:
                    gs.reset_board()
                    gs.whites_turn=True
                    valid_moves=gs.get_valid_moves()
            
        if not human_turn and len(valid_moves)!=0:
            AI_move=find_good_move(gs, valid_moves, evaluator)
            if AI_move: gs.move_piece(AI_move)
            else: gs.move_piece(random.choice(valid_moves))
            valid_moves=gs.get_valid_moves()
        
        draw_game_state(screen, gs, valid_moves, selected_start)
        
        clock.tick(MAX_FPS) # set max update rate
        p.display.flip() # update entire display to reflect changes
    
    p.quit() # good practice to actually close the initialization

if __name__=="__main__":
    main()