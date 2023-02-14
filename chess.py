import numpy as np
import ast

# having the pieces in chess_board not directly labeled according to their IMAGE makes the __ini__ functions of the piece classes really messy
# maybe try to change that

# convention: white at the top

BOARD_DIM=8
# since possible castling moves have to be tracked, its convenient to define the following variables globally:
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
        self.white_king_loc=WHITE_KING_START_LOC
        self.black_king_loc=BLACK_KING_START_LOC
        # solution for castling: booleans which track if rooks where moved
        # turned into lists to accommodate for timing when undoing moves
        self.castling_white_king_side=[True]
        self.castling_white_queen_side=[True]
        self.castling_black_king_side=[True]
        self.castling_black_queen_side=[True]
        
        self.checkmate=False
        self.stalemate=False
    
    def place_piece(self, position, piece):
        self.board[position[0],position[1]]=piece
    
    def remove_piece(self, position):
        self.board[position[0],position[1]]=None
    
    def move_piece(self, move):
        # because of timing issues illegal inputs for moves will be handled through the UI
        if self.board[move.start_row,move.start_col]!=None:
            self.reset_en_passant() # resets en-passant rights of all pawns, because if a en-passant move
            # is not immedietly executed, it is not possible in the next move according to chess rules
            # doing this before pawns disappear from the board
            
            # update king pos
            if isinstance(move.piece_moved, king):
                if move.piece_moved.color=='w':
                    self.white_king_loc=[move.end_row, move.end_col]
                else:
                    self.black_king_loc=[move.end_row, move.end_col]
            self.remove_piece([move.start_row, move.start_col])
            self.place_piece([move.end_row, move.end_col], move.piece_moved)
            self.move_log.append(move)
            
            # HANDLING OF CASTLING MOVES:
            # updating castling timelines:
            # check for instance not required since its impossible for a piece to be not king and start on king square
            # white king side
            if self.castling_white_king_side[-1]==False:
                self.castling_white_king_side.append(False)
            elif [move.start_row, move.start_col]==WHITE_KING_START_LOC:
                self.castling_white_king_side.append(False)
            elif [move.start_row, move.start_col]==WHITE_ROOK_KING_START_LOC and isinstance(move.piece_moved, rook):
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
                    if move.end_col==1:
                        self.remove_piece(BLACK_ROOK_KING_START_LOC)
                        self.place_piece([7,2], rook('b'))
                    if move.end_col==5:
                        self.remove_piece(BLACK_ROOK_QUEEN_START_LOC)
                        self.place_piece([7,4], rook('b'))
            
            # HANDLING OF EN-PASSANT MOVES:
            # when making a two step pawn move, check for neighboring opponent pawns and make them
            # elligible for en-passant through setting their corresponding boolean
            
            # performing en-passant move:
            if move.en_passant: # remove other piece
                if move.piece_moved.color=='w':
                    self.remove_piece([move.end_row-1, move.end_col])
                elif move.piece_moved.color=='b':
                    self.remove_piece([move.end_row+1, move.end_col])
            
            if isinstance(move.piece_moved, pawn):
                # after certain moves give corresponding pawns ability to perform en-passant:
                if (0 <= move.end_col+1 < BOARD_DIM and abs(move.start_row-move.end_row)==2
                    and isinstance(self.board[move.end_row, move.end_col+1], pawn)
                    and self.board[move.end_row, move.end_col+1].color!=move.piece_moved.color):
                    self.board[move.end_row, move.end_col+1].en_passant_right[-1]=True
                if (0 <= move.end_col-1 < BOARD_DIM and abs(move.start_row-move.end_row)==2
                    and isinstance(self.board[move.end_row, move.end_col-1], pawn)
                    and self.board[move.end_row, move.end_col-1].color!=move.piece_moved.color):
                    self.board[move.end_row, move.end_col-1].en_passant_left[-1]=True
                
            
            self.whites_turn=(not self.whites_turn)
        else:
            print("cant move None")
    
    def undo_move(self):
        assert len(self.move_log)>=1, "move log is empty"
        last_move=self.move_log[-1]
        # weird logic wise that i have this actions here considering what happens afterwards with en-passant
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
        
        # CASTLING MOVES:
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
                if last_move.end_col==1:
                    self.remove_piece([7,2])
                    self.place_piece(BLACK_ROOK_KING_START_LOC, rook('b'))
                if last_move.end_col==5:
                    self.remove_piece([7,4])
                    self.place_piece(BLACK_ROOK_QUEEN_START_LOC, rook('b'))
        
        # EN-PASSANT MOVES:
        # if en-passant move boolean is True it means the only way a pawn can change columns in the corresponding
        # directions is through an en-passant move, therefore checking if change in col and en-passant boolean is sufficient
        # for identification
        if last_move.en_passant:
            # right side en-passant:
            if last_move.end_col+1==last_move.start_col:
                self.remove_piece([last_move.end_row, last_move.end_col])
                self.place_piece([last_move.start_row, last_move.start_col], last_move.piece_moved) # this ensures that en-passant boolean is kept
                self.place_piece([last_move.start_row, last_move.start_col-1], last_move.piece_captured_right)
            # left side en-passant:
            elif last_move.end_col-1==last_move.start_col:
                self.remove_piece([last_move.end_row, last_move.end_col])
                self.place_piece([last_move.start_row, last_move.start_col], last_move.piece_moved)
                print(type(last_move.piece_captured))
                self.place_piece([last_move.start_row, last_move.start_col+1], last_move.piece_captured_left)
        
        self.undo_en_passant_states()
        
        
        # undoing moves means setting checkmate and stalemate to False is always a valid operation
        self.checkmate=False
        self.stalemate=False
        
        self.whites_turn=not self.whites_turn
        
    def get_possible_moves(self):
        # generate a list of all possible moves
        moves=[]
        for row in range(BOARD_DIM):
            for col in range(BOARD_DIM):
                cur_piece=self.board[row, col]
                if cur_piece==None: continue
                else: moves+=cur_piece.get_moves(self, [row, col])
        
        # if castling is enabled through booleans and squares are available add them to possible moves here
        # additional check for better endgame performance:
        if self.castling_black_king_side[-1] or self.castling_black_queen_side[-1] or self.castling_white_king_side[-1] or self.castling_white_queen_side[-1]:
            if self.whites_turn:
                if self.castling_white_king_side[-1]:
                    if not self.board[0,1] and not self.board[0,2]:
                        moves.append(move(WHITE_KING_START_LOC, [0,1], self.board))
                if self.castling_white_queen_side[-1]:
                    if not self.board[0,4] and not self.board[0,5] and not self.board[0,6]:
                        moves.append(move(WHITE_KING_START_LOC, [0,5], self.board))
            if not self.whites_turn:
                if self.castling_black_king_side[-1]:
                    if not self.board[7,1] and not self.board[7,2]:
                        moves.append(move(BLACK_KING_START_LOC, [7,1], self.board))
                if self.castling_black_queen_side[-1]:
                    if not self.board[7,4] and not self.board[7,5] and not self.board[7,6]:
                        moves.append(move(BLACK_KING_START_LOC, [7,5], self.board))
                
        return moves
    
    def get_valid_moves(self):
        # moves which end in a checkmate are not allowed and get filtered here
        # no need for deep copy since undo_move() can be used instead
        
        moves=self.get_possible_moves()

        print("before evaluating valid moves")
        count=1
        for i in range(np.shape(self.board)[0]):
            for j in range(np.shape(self.board)[1]):
                piece=self.board[i,j]
                if isinstance(piece, pawn):
                    print(count)
                    print(piece.en_passant_right)
                    print(piece.en_passant_left)
                    count+=1
        
        print("getting valid moves now")
        
        for i in range(len(moves)-1, -1, -1):
            # active player makes move
            self.move_piece(moves[i])
            # now check if this move brought me into the checked state
            self.whites_turn=not self.whites_turn
            if self.in_check():
                moves.remove(moves[i])
            self.whites_turn=not self.whites_turn
            self.undo_move()
            
        # update checkmate and stalemate states:
        if len(moves)==0:
            if self.in_check():
                self.checkmate=True
            else:
                self.stalemate=True
        
        count=1
        for i in range(np.shape(self.board)[0]):
            for j in range(np.shape(self.board)[1]):
                piece=self.board[i,j]
                if isinstance(piece, pawn):
                    print(count)
                    print(piece.en_passant_right)
                    print(piece.en_passant_left)
                    count+=1
        
        print("finished getting valid moves")
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
    
    def reset_en_passant(self):
        for i in range(np.shape(self.board)[0]):
            for j in range(np.shape(self.board)[1]):
                piece=self.board[i,j]
                if isinstance(piece, pawn):
                    piece.en_passant_left.append(False)
                    piece.en_passant_right.append(False)
    
    def undo_en_passant_states(self):
        for i in range(np.shape(self.board)[0]):
            for j in range(np.shape(self.board)[1]):
                piece=self.board[i,j]
                if isinstance(piece, pawn):
                    piece.en_passant_left.pop()
                    piece.en_passant_right.pop()
    
    def reset_board(self):
        self.board=np.full((8, 8), None, dtype=object)
        self.move_log=[]
        for i in range(8):
            self.place_piece([1,i], pawn('w'))
            self.place_piece([6,i], pawn('b'))
        
        self.castling_white_king_side=[True]
        self.castling_white_queen_side=[True]
        self.castling_black_king_side=[True]
        self.castling_black_queen_side=[True]
        
        self.checkmate=False
        self.stalemate=False
        
        self.place_piece(WHITE_ROOK_KING_START_LOC, rook('w'))
        self.place_piece(WHITE_ROOK_QUEEN_START_LOC, rook('w'))
        self.place_piece(BLACK_ROOK_KING_START_LOC, rook('b'))
        self.place_piece(BLACK_ROOK_QUEEN_START_LOC, rook('b'))
        self.place_piece([0,1], knight('w'))
        self.place_piece([0,-2], knight('w'))
        self.place_piece([7,1], knight('b'))
        self.place_piece([7,-2], knight('b'))
        self.place_piece([0,2], bishop('w'))
        self.place_piece([7,2], bishop('b'))
        self.place_piece([0,-3], bishop('w'))
        self.place_piece([7,-3], bishop('b'))
        self.place_piece(WHITE_KING_START_LOC, king('w'))
        self.place_piece(BLACK_KING_START_LOC, king('b'))
        self.place_piece([0,4], queen('w'))
        self.place_piece([7,4], queen('b'))

class move: # class for storing moves and analyzing future moves
    def __init__(self, start, end, board, castling_move=False, en_passant=False):
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
        # HANDLING CASTLING MOVES:
        self.castling_move=castling_move
        # if move not in standard king moves make it a castle move (this is needed for creating the instance in the UI, AI does not need this!)
        # castling moves change generally change columns by 2
        if isinstance(self.piece_moved, king) and abs(self.end_col-self.start_col)==2:
            self.castling_move=True
        # HANDLING EN-PASSANT MOVES:
        self.en_passant=en_passant
        # in our logic, initializing a move which ends in None and changes column of a pawn, has to be an en_passant move
        if isinstance(self.piece_moved, pawn) and self.start_col!=self.end_col and self.board[self.end_row, self.end_col]==None:
            self.en_passant=True
            if self.piece_moved.en_passant_right:
                self.piece_captured_right=board[self.start_row, self.start_col-1]
            if self.piece_moved.en_passant_left:
                self.piece_captured_left=board[self.start_row, self.start_col+1]
    
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

class pawn(piece):
    def __init__(self, color, en_passant_left_start=False, en_passant_right_start=False):
        super().__init__(color)
        self.rep='p'
        self.key=color+self.rep
        self.en_passant_left=[en_passant_left_start]
        self.en_passant_right=[en_passant_right_start]
    
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
        
        # converting to move objects
        if len(moves)!=0:
            moves=self.convert_to_move(pos, moves, board)
        
        # ADDING EN-PASSANT MOVES
        if self.en_passant_right[-1]:
            if self.color=='w' and chess_board.whites_turn:
                moves.append(move(pos, [pos[0]+1, pos[1]-1], board))
            if self.color=='b' and not chess_board.whites_turn:
                moves.append(move(pos, [pos[0]-1, pos[1]-1], board))
        
        if self.en_passant_left[-1]:
            if self.color=='w' and chess_board.whites_turn:
                moves.append(move(pos, [pos[0]+1, pos[1]+1], board))
            if self.color=='b' and not chess_board.whites_turn:
                moves.append(move(pos, [pos[0]-1, pos[1]+1], board))
        
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
