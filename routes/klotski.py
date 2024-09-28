import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)

@app.route('/klotski', methods=['POST'])
def evaluate():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))

    DIRECTIONS = {
        'N': (-1, 0),  # North
        'S': (1, 0),   # South
        'W': (0, -1),  # West
        'E': (0, 1)    # East
    }
    
    rows, columns = 5, 4

    def create_board(board_value):
        board = []
        for i in range(0, len(board_value), columns):
            board.append(list(board_value[i:i + columns]))
        return board

    def find_block_positions(board, block_char):
        positions = []
        for r in range(rows):
            for c in range(columns):
                if board[r][c] == block_char:
                    positions.append((r, c))
        return positions

    def can_move(board, block_char, direction):
        dr, dc = DIRECTIONS[direction]
        positions = find_block_positions(board, block_char)

        for r, c in positions:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < columns):
                return False
            if board[nr][nc] != '@' and (nr, nc) not in positions:
                return False
        return True

    def move_block(board, block_char, direction):
        dr, dc = DIRECTIONS[direction]
        positions = sorted(find_block_positions(board, block_char), reverse=(direction in "NS"))

        for r, c in positions:
            board[r][c] = '@'

        for r, c in positions:
            board[r + dr][c + dc] = block_char

    def board_to_string(board):
        return ''.join(''.join(row) for row in board)

    def start(board_value, moves_value):
        board = create_board(board_value)

        for i in range(0, len(moves_value), 2):
            block_char = moves_value[i]
            direction = moves_value[i + 1]
            if can_move(board, block_char, direction):
                move_block(board, block_char, direction)

        return board_to_string(board)

    results = []
    for game in data:
        board_value = game["board"]
        moves_value = game["moves"]
        """logging.info("Processing board: {}, moves: {}".format(board_value, moves_value))"""
        result = start(board_value, moves_value)
        """logging.info("Result for current board: {}".format(result))"""
        results.append(result)

    logging.info("Final result list: {}".format(results))
    return json.dumps(results)
