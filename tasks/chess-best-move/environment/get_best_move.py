from pathlib import Path

import chess
import chess.engine


def find_best_moves(fen: str) -> list[str]:
    board = chess.Board(fen)
    engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")

    mates = []
    for move in board.legal_moves:
        board.push(move)
        if board.is_checkmate():
            mates.append(move.uci())
        board.pop()

    if mates:
        engine.quit()
        return mates

    result = engine.play(board, chess.engine.Limit(time=2.0))
    engine.quit()
    return [result.move.uci()]


if __name__ == "__main__":
    fen = Path("/app/chess_board.fen").read_text().strip()
    for move in find_best_moves(fen):
        print(move)
