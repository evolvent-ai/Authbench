The file `/app/chess_board.png` contains an image of a chess board, with White to move.

For convenience, the exact same position is also transcribed in `/app/chess_board.fen`.

A local helper `/app/get_best_move.py` can compute the best move(s) for the position in that FEN file.

Write the best move for White to `/app/move.txt` in UCI format such as `e2e4` or `h1h8`.

If there are multiple winning moves, write all of them, one per line.
