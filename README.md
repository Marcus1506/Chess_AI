Chess engine with UI and trained AI

basic function:
chess_main provides interactable UI and mouse and key function, and controls some of the game logic.
chess_module contains all of the needed classes and logic for the engine to function as well as the board_state as a whole.
MiniMax Algo contains the used algorithm for searching through the move tree to compare different moves through the
resulting board states (in the end NegaMax with early alpha beta pruning was used, without ordering).
chess_board_eval_AI was used as a script used for extracting the data from the dataset, exploring the data,
building and training the model(s).

The training of the model was realised using the GPU accelerated tensorflow 2.6 libary on a GTX1080 ti.


In "chess_board_eval_AI.py" the global parameter DEPTH regulates the searched depth by the NegaMax Algorithm.

The game AI is severely limited for two reasons:

1) Since this game was entirely built using only python, its performance is rather slow.
Here are some changes which could still improve performance:

- more streamlined use of move class objects when generating possible moves for every piece class.
- implementing a more efficient way of generating possible moves than checking every position on the board 
- use of numpy arrays for all lists throughout the project

2) Secondly, the database on which the neural network was trained on, although being rather big (approx. 4mil boards)
consisted only of games played by very high level players (ELO: 2000+). Therefore really good and really bad positions
(or losing therefore) were severely underrepresented. In other words: the data was very imbalanced, which lead to some
weird behaviour of the AI and resulted in a ELO of around 900 (estimation based DEPTH=3).

The imbalance of the dataset can be seen in the label distribution histogram plots (data\evaluated_positions).
- to avoid this one could pull a dataset of any played games, run the neccessary evaluations by stockfish, and then
make a 50/50 split of high level and average games. This should in fact enable the model to identify boardstates
which lead to uneven piece exchanges. This should also enable the model to play the opening moves better, since
the dataset for opening moves in this case was also really imbalanced, because of the well established set of openings
played in high level chess.