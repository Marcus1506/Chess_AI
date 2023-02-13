import numpy as np
import ast

# having the pieces in chess_board not directly labeled according to their IMAGE makes the __ini__ functions of the piece classes really messy
# maybe try to change that

# convention: white at the top

BOARD_DIM=8
# since possible castling moves has to be tracked, the following piece positions are global variables:
WHITE_KING_START_LOC=[0,3]
WHITE_ROOK_KING_START_LOC=[0,0]
WHITE_ROOK_QUEEN_START_LOC=[0,7]
BLACK_KING_START_LOC=[7,3]
BLACK_ROOK_KING_START_LOC=[7,0]
BLACK_ROOK_QUEEN_START_LOC=[7,7]

class chess_board:
    def __init__(self, id=0, whites_turn=True): # give chess board ids, making use of multiple instances easier if necessary
        self.board=np.full((8, 8), None, dtype=object)
        self.id=id
        self.whites_turn=whites_turn # means white starts
        self.move_log=[]
        self.white_king_loc=[0,3]
        self.black_king_loc=[7,3]
        # solution for castling: booleans which track if rooks where moved
        # turned into lists to accommodate for timing when undoing moves
        self.castling_white_king_side=[True]
        self.castling_white_queen_side=[True]
        self.castling_black_king_side=[True]
        self.castling_black_queen_side=[True]
    
    def place_piece(self, position, piece):
        self.board[position[0],position[1]]=piece
    
    def remove_piece(self, position):
        self.board[position[0],position[1]]=None
    
    def move_piece(self, move):
        # because of timing issues illegal inputs for moves will be handled through the UI
        if self.board[move.start_row,move.start_col]!=None:
            # update king pos
            if isinstance(move.piece_moved, king):
                if move.piece_moved.color=='w':
                    self.white_king_loc=[move.end_row, move.end_col]
                else:
                    self.black_king_loc=[move.end_row, move.end_col]
            self.remove_piece([move.start_row, move.start_col])
            self.place_piece([move.end_row, move.end_col], move.piece_moved)
            self.move_log.append(move)
            
            # if moved piece was rook or king then set booleans:
            # for better performance in late game additional checks in beginning
            
            # if isinstance(move.piece_moved, king) or isinstance(move.piece_moved, rook):
                # if self.whites_turn:
                    # if [move.start_row, move.start_col]==[0,3]:
                        # self.castling_white_king_side.append(False)
                        # self.castling_white_queen_side.append(False)
                    # if [move.start_row, move.start_col]==[0,0]:
                        # self.castling_white_king_side.append(False)
                    # if [move.start_row, move.start_col]==[0,7]:
                        # self.castling_white_queen_side.append(False)
                # if not self.whites_turn:
                    # if [move.start_row, move.start_col]==[7,3]:
                        # self.castling_black_king_side.append(False)
                        # self.castling_black_queen_side.append(False)
                    # if [move.start_row, move.start_col]==[7,0]:
                        # self.castling_black_king_side.append(False)
                    # if [move.start_row, move.start_col]==[7,7]:
                        # self.castling_black_queen_side.append(False)
            
            # somehow this gets really ugly
            # white king side
            if self.castling_white_king_side[-1]==False:
                self.castling_white_king_side.append(False)
            elif [move.start_row, move.start_col]==WHITE_KING_START_LOC:
                self.castling_white_king_side.append(False)
            elif [move.start_row, move.start_col]==WHITE_ROOK_KING_START_LOC:
                self.castling_white_king_side.append(False)
            # white queen side
            if self.castling_white_queen_side[-1]==False:
                self.castling_white_queen_side.append(False)
            elif [move.start_row, move.start_col]==WHITE_KING_START_LOC:
                self.castling_white_queen_side.append(False)
            elif [move.start_row, move.start_col]==WHITE_ROOK_QUEEN_START_LOC:
                self.castling_white_queen_side.append(False)
            # black king side
            if self.castling_black_king_side[-1]==False:
                self.castling_black_king_side.append(False)
            elif [move.start_row, move.start_col]==BLACK_KING_START_LOC:
                self.castling_black_king_side.append(False)
            elif [move.start_row, move.start_col]==BLACK_ROOK_KING_START_LOC:
                self.castling_black_king_side.append(False)
            # black queen side
            if self.castling_black_queen_side[-1]==False:
                self.castling_black_queen_side.append(False)
            elif [move.start_row, move.start_col]==BLACK_KING_START_LOC:
                self.castling_black_queen_side.append(False)
            elif [move.start_row, move.start_col]==BLACK_ROOK_QUEEN_START_LOC:
                self.castling_black_queen_side.append(False)
            
            
            # if move was castle move, additional piece placement required:
            if move.castling_move:
                if self.whites_turn:
                    if move.end_col==1:
                        self.remove_piece(WHITE_ROOK_KING_START_LOC)
                        self.place_piece([0,2], rook('w'))
                    if move.end_col==5:
                        self.remove_piece(WHITE_ROOK_QUEEN_START_LOC)
                        self.place_piece([0,4], rook('w'))
                if not self.whites_turn:
                    pass
            
            self.whites_turn=(not self.whites_turn)
        else:
            print("cant move None")
    
    def undo_move(self):
        assert len(self.move_log)>=1, "move log is empty"
        last_move=self.move_log[-1]
        self.board[last_move.end_row, last_move.end_col]=last_move.piece_captured
        self.board[last_move.start_row, last_move.start_col]=last_move.piece_moved
        self.move_log.pop()
        
        # update king pos
        if last_move.piece_moved.key=='wK':
            self.white_king_loc=[last_move.start_row, last_move.start_col]
            print("new white king location: ", self.white_king_loc)
        elif last_move.piece_moved.key=='bK':
            self.black_king_loc=[last_move.start_row, last_move.start_col]
            print("new black king location: ", self.black_king_loc)
        
        # resetting booleans of possible castling
        # I can pop booleans if last is False
        # this way it tracks castlemoves correctly in a True, False - move timeline
        if self.castling_white_king_side[-1]==False:
            self.castling_white_king_side.pop()
        if self.castling_white_queen_side[-1]==False:
            self.castling_white_queen_side.pop()
        if self.castling_black_king_side[-1]==False:
            self.castling_black_king_side.pop()
        if self.castling_black_queen_side[-1]==False:    
            self.castling_black_queen_side.pop()
        
        # if last move was castling moves, two piece movements have to be undone
        if last_move.castling_move:
            if not self.whites_turn: # undoing while blacks turn means moving white pieces
                if last_move.end_col==1:
                    self.remove_piece([0,2])
                    self.place_piece(WHITE_ROOK_KING_START_LOC, rook('w'))
                if last_move.end_col==5:
                    self.remove_piece([0,4])
                    self.place_piece(WHITE_ROOK_QUEEN_START_LOC, rook('w'))
            if self.whites_turn:
                pass
        
        self.whites_turn=not self.whites_turn
        
    def get_possible_moves(self):
        # generate a list of all possible moves
        moves=[]
        for row in range(BOARD_DIM):
            for col in range(BOARD_DIM):
                cur_obj=self.board[row, col]
                if cur_obj==None: continue
                else: moves+=cur_obj.get_moves(self, [row, col])
        
        # if castling is enabled through booleans and squares are available add them to possible moves here
        # additional check for better endgame performance:
        if self.castling_black_king_side or self.castling_black_queen_side or self.castling_white_king_side or self.castling_white_queen_side:
            if self.whites_turn:
                if self.castling_white_king_side[-1]:
                    if not self.board[0,1] and not self.board[0,2]:
                        moves.append(move([0, 3], [0,1], self.board, castling_move=True))
                if self.castling_white_queen_side[-1]:
                    if not self.board[0,4] and not self.board[0,5] and not self.board[0,6]:
                        moves.append(move([0, 3], [0,5], self.board, castling_move=True))
            if not self.whites_turn:
                if self.castling_black_king_side:
                    pass
                if self.castling_black_queen_side:
                    pass
                    
                
        return moves
    
    def get_valid_moves(self):
        # moves which end in a checkmate are not allowed and get filtered here
        # no need for deep copy since undo_move() can be used instead
        
        moves=self.get_possible_moves()

        for i in range(len(moves)-1, -1, -1):
            # active player makes move
            self.move_piece(moves[i])
            # now check if this move brought me into the checked state
            self.whites_turn=not self.whites_turn
            if self.in_check():
                moves.remove(moves[i])
            self.whites_turn=not self.whites_turn
            self.undo_move()

        return moves
        
    def in_check(self): # if player on the move is in check returns True
        if self.whites_turn:
            return self.square_under_attack(self.white_king_loc[0], self.white_king_loc[1])
        else:
            return self.square_under_attack(self.black_king_loc[0], self.black_king_loc[1])
    
    def square_under_attack(self, row, col): # general function which checks if square is under attack
        # switch to oppenent, get moves and switch back
        self.whites_turn=not self.whites_turn
        opponents_moves=self.get_possible_moves()
        self.whites_turn=not self.whites_turn
        # because of the stored king locations, we dont have to move two times
        for move in opponents_moves:
            if move.end_row==row and move.end_col==col:
                return True
        return False
   
    def get_board(self):
        return self.board
    
    def set_board(self, board):
        self.board=board
    
    def set_move_log(self, move_log):
        self.move_log=move_log
    
    def __str__(self):
        print(self.board)
    
    def __repr__(self):
        # implement a way to print board directly with None representatives
        print(self.board)
    
    def reset_board(self):
        for i in range(8):
            self.place_piece([1,i], pawn('w'))
            self.place_piece([6,i], pawn('b'))
        self.place_piece([0,0], rook('w'))
        self.place_piece([0,7], rook('w'))
        self.place_piece([7,0], rook('b'))
        self.place_piece([7,7], rook('b'))
        self.place_piece([0,1], knight('w'))
        self.place_piece([0,-2], knight('w'))
        self.place_piece([7,1], knight('b'))
        self.place_piece([7,-2], knight('b'))
        self.place_piece([0,2], bishop('w'))
        self.place_piece([7,2], bishop('b'))
        self.place_piece([0,-3], bishop('w'))
        self.place_piece([7,-3], bishop('b'))
        self.place_piece([0,3], king('w'))
        self.place_piece([7,3], king('b'))
        self.place_piece([0,4], queen('w'))
        self.place_piece([7,4], queen('b'))

class move: # class for storing moves and analyzing future moves
    def __init__(self, start, end, board, castling_move=False):
        # store all the important information for a move
        # maybe also add boardstate, could be important for AI later on
        self.start_row=start[0]
        self.start_col=start[1]
        self.end_row=end[0]
        self.end_col=end[1]
        self.board=board # to define equality more smoothly
        self.piece_moved=board[start[0], start[1]]
        # this direct approach for setting the piece captured is very intuitive
        # no peace captured would mean None dtype, and it simplifies some following implementations
        self.piece_captured=board[end[0], end[1]]
        self.castling_move=castling_move
        
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if (self.start_row == other.start_row and
                self.start_col == other.start_col and
                self.end_row == other.end_row and
                self.end_col == other.end_col and
                np.array_equal(self.board, other.board)):
                return True
        
        return False
    
    def __repr__(self):
        return str([self.start_row,self.start_col,self.end_row,self.end_col])

class piece:
    def __init__(self, color):
        assert color=='w' or color=='b', "wrong/no color"
        self.color=color
    
    def add_horizontal_moves(self, board, pos):
        dir_1=[-1, 1]
        
        moves=[]
        
        for dir in dir_1:
            for row in range(1, BOARD_DIM):
                if 0 <= pos[0]+dir*row < BOARD_DIM:
                    if board[pos[0]+dir*row, pos[1]]==None:
                        moves.append([pos[0]+dir*row, pos[1]])
                    elif board[pos[0]+dir*row, pos[1]].color==self.color:
                        break
                    else:
                        moves.append([pos[0]+dir*row, pos[1]])
                        break
            for col in range(1, BOARD_DIM):
                if 0 <= pos[1]+dir*col < BOARD_DIM:
                    if board[pos[0], pos[1]+dir*col]==None:
                        moves.append([pos[0], pos[1]+dir*col])
                    elif board[pos[0], pos[1]+dir*col].color==self.color:
                        break
                    else:
                        moves.append([pos[0], pos[1]+dir*col])
                        break
        
        if len(moves)!=0:
            moves=self.convert_to_move(pos, moves, board)
        
        return moves
    
    def convert_to_move(self, pos, moves, board):
        converted_moves=[]
        for move_ in moves:
            converted_moves.append(move(pos, move_, board))
        return converted_moves
    
    def add_diagonal_moves(self, board, pos):
        moves=[]

        directions_1=[-1,1]
        directions_2=[-1,1]
        
        for dir_1 in directions_1:
            for dir_2 in directions_2:
                for dist in range(1, BOARD_DIM):
                    if 0 <= pos[0]+dir_1*dist < BOARD_DIM and 0 <= pos[1]+dir_2*dist < BOARD_DIM:
                        if board[pos[0]+dir_1*dist, pos[1]+dir_2*dist]==None:
                            moves.append([pos[0]+dir_1*dist, pos[1]+dir_2*dist])
                        elif board[pos[0]+dir_1*dist, pos[1]+dir_2*dist].color==self.color:
                            break
                        else:
                            moves.append([pos[0]+dir_1*dist, pos[1]+dir_2*dist])
                            break
        
        if len(moves)!=0:
            moves=self.convert_to_move(pos, moves, board)
        
        return moves
    
    def check_false_color_and_turn(self, whites_turn):
        if self.color=='b' and whites_turn:
            return True
            
        if self.color=='w' and (not whites_turn):
            return True
        
        else: return False
    
    def get_position(self):
        return self.position

class pawn(piece):
    def __init__(self, color):
        super().__init__(color)
        self.rep='p'
        self.key=color+self.rep
    
    def get_moves(self, chess_board, pos):
        board=chess_board.get_board()
        moves=[]
        
        if self.color=='w' and chess_board.whites_turn:
            # catch the case when the pawn reached end position on the board
            assert pos[0]!=BOARD_DIM, "pawn must me promoted when end of board is reached"
            if  0 <= pos[0]+1 < BOARD_DIM and board[pos[0]+1, pos[1]]==None:
                moves.append([pos[0]+1, pos[1]])
                if 0 <= pos[0]+2 < BOARD_DIM and board[pos[0]+2, pos[1]]==None and pos in [[1,i] for i in range(BOARD_DIM)]:
                    moves.append([pos[0]+2, pos[1]])
            if 0 <= pos[0]+1 < BOARD_DIM and 0 <= pos[1]+1 < BOARD_DIM and board[pos[0]+1, pos[1]+1]!=None and board[pos[0]+1, pos[1]+1].color!=self.color:
                moves.append([pos[0]+1, pos[1]+1])
            if 0 <= pos[0]+1 < BOARD_DIM and 0 <= pos[1]-1 < BOARD_DIM and board[pos[0]+1, pos[1]-1]!=None and board[pos[0]+1, pos[1]-1].color!=self.color:
                moves.append([pos[0]+1, pos[1]-1])
        
        elif self.color=='b' and (not chess_board.whites_turn):
            assert pos[0]!=0, "pawn must me promoted when end of board is reached"
            if 0 <= pos[0]-1 < BOARD_DIM and board[pos[0]-1, pos[1]]==None:
                moves.append([pos[0]-1, pos[1]])
                if 0 <= pos[0]-2 < BOARD_DIM and board[pos[0]-2, pos[1]]==None and pos in [[6,i] for i in range(BOARD_DIM)]:
                    moves.append([pos[0]-2, pos[1]])
            if 0 <= pos[0]-1 < BOARD_DIM and 0 <= pos[1]-1 < BOARD_DIM and board[pos[0]-1, pos[1]-1]!=None and board[pos[0]-1, pos[1]-1].color!=self.color:
                moves.append([pos[0]-1, pos[1]-1])
            if 0 <= pos[0]-1 < BOARD_DIM and 0 <= pos[1]+1 < BOARD_DIM and board[pos[0]-1, pos[1]+1]!=None and board[pos[0]-1, pos[1]+1].color!=self.color:
                moves.append([pos[0]-1, pos[1]+1])
        
        # add beginning position 'pos' for comparing if the move is valid
        if len(moves)!=0:
            moves=self.convert_to_move(pos, moves, board)
        
        return moves
    
    def __str__(self):
        return "P"
    
    def __repr__(self):
        return "P"

class rook(piece):
    def __init__(self, color):
        super().__init__(color)
        self.rep='R'
        self.key=color+self.rep
    
    def get_moves(self, chess_board, pos):
        board=chess_board.get_board()
        
        if self.check_false_color_and_turn(chess_board.whites_turn):
            return []
        
        return self.add_horizontal_moves(board, pos)
    
    
    def __str__(self):
        return "R"
    
    def __repr__(self):
        return "R"

class knight(piece):
    def __init__(self, color):
        super().__init__(color)
        self.rep='N'
        self.key=color+self.rep
    
    def get_moves(self, chess_board, pos):
        moves=[]
        
        if self.check_false_color_and_turn(chess_board.whites_turn):
            return moves
        
        board=chess_board.get_board()
        
        permutations=[[2,1],[1,2]]
        directions_1=[-1,1]
        directions_2=[-1,1]
        
        for dir_1 in directions_1:
            for dir_2 in directions_2:
                for perm in permutations:
                    if 0 <= pos[0]+dir_1*perm[0] < BOARD_DIM and 0 <= pos[1]+dir_2*perm[1] < BOARD_DIM:
                        if board[pos[0]+dir_1*perm[0], pos[1]+dir_2*perm[1]]==None or board[pos[0]+dir_1*perm[0], pos[1]+dir_2*perm[1]].color!=self.color:
                            moves.append([pos[0]+dir_1*perm[0], pos[1]+dir_2*perm[1]])
        
        if len(moves)!=0:
            moves=self.convert_to_move(pos, moves, board)
        
        return moves
    
    def __str__(self):
        return "K"
    
    def __repr__(self):
        return "K"

class bishop(piece):
    def __init__(self, color):
        super().__init__(color)
        self.rep='B'
        self.key=color+self.rep
    
    def get_moves(self, chess_board, pos):
    
        if self.check_false_color_and_turn(chess_board.whites_turn):
            return []
    
        board=chess_board.get_board()
        
        return self.add_diagonal_moves(board, pos)
    
    def __str__(self):
        return "B"
    
    def __repr__(self):
        return "B"

class queen(piece):
    def __init__(self, color):
        super().__init__(color)
        self.rep='Q'
        self.key=color+self.rep
    
    def get_moves(self, chess_board, pos):
        moves=[]
        
        if self.check_false_color_and_turn(chess_board.whites_turn):
            return moves
        
        board=chess_board.get_board()
        
        moves+=self.add_diagonal_moves(board, pos)
        moves+=self.add_horizontal_moves(board, pos)
        
        return moves
    
    def __str__(self):
        return "Q"
    
    def __repr__(self):
        return "Q"

class king(piece):
    def __init__(self, color):
        super().__init__(color)
        self.rep='K'
        self.key=self.color+self.rep
    
    def get_moves(self, chess_board, pos):
        moves=[]
        
        if self.check_false_color_and_turn(chess_board.whites_turn):
            return moves
        
        board=chess_board.get_board()
        
        directions_1=[-1,1]
        directions_2=[-1,1]
        
        for dir_1 in directions_1:
            for dir_2 in directions_2:
                pos_1=[pos[0]+dir_1, pos[1]]
                pos_2=[pos[0], pos[1]+dir_2]
                pos_3=[pos[0]+dir_1, pos[1]+dir_2]
                
                if 0 <= pos_1[0] < BOARD_DIM:
                    if board[pos_1[0], pos_1[1]]==None:
                        moves.append([pos_1[0], pos_1[1]])
                    elif board[pos_1[0], pos_1[1]].color!=self.color:
                        moves.append([pos_1[0], pos_1[1]])
                
                if 0 <= pos_2[1] < BOARD_DIM:
                    if board[pos_2[0], pos_2[1]]==None:
                        moves.append([pos_2[0], pos_2[1]])
                    elif board[pos_2[0], pos_2[1]].color!=self.color:
                        moves.append([pos_2[0], pos_2[1]])
                
                if 0 <= pos_3[0] < BOARD_DIM and 0 <= pos_3[1] < BOARD_DIM:
                    if board[pos_3[0], pos_3[1]]==None:
                        moves.append([pos_3[0], pos_3[1]])
                    elif board[pos_3[0], pos_3[1]].color!=self.color:
                        moves.append([pos_3[0], pos_3[1]])
        
        if len(moves)!=0:
            moves=self.convert_to_move(pos, moves, board)
        
        return moves
    
    def __str__(self):
        return "X"
    
    def __repr__(self):
        return "X"
