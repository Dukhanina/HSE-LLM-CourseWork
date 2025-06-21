def create_board():
    board = [[None for _ in range(8)] for _ in range(8)]
    for i in range(3):
        for j in range(8):
            if (i + j) % 2 == 1:
                board[i][j] = 'w'
    for i in range(5, 8):
        for j in range(8):
            if (i + j) % 2 == 1:
                board[i][j] = 'b'
    return board

def print_board(board):
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece is None:
                print('.', end=' ')
            elif piece == 'w' or piece == 'b':
                print(piece, end=' ')
            else:
                print(piece.upper(), end=' ')
        print()

def is_valid_position(pos):
    return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

def get_capture_moves(board, player, pos):
    moves = []
    r, c = pos
    piece = board[r][c]
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if piece in ('W', 'B') else [(-1, -1), (-1, 1)] if player == 'w' else [(1, -1), (1, 1)]
    for dr, dc in directions:
        r1, c1 = r + dr, c + dc
        r2, c2 = r + 2 * dr, c + 2 * dc
        if (is_valid_position((r1, c1)) and is_valid_position((r2, c2)) and
            board[r1][c1] in ('b', 'B') if player == 'w' else board[r1][c1] in ('w', 'W') and
            board[r2][c2] is None):
            moves.append((r2, c2))
    return moves

def has_capture_moves(board, player):
    for i in range(8):
        for j in range(8):
            if board[i][j] in (player, player.upper()) and get_capture_moves(board, player, (i, j)):
                return True
    return False

def is_valid_move(board, player, start, end):
    if not (is_valid_position(start) and is_valid_position(end)):
        return False
    piece = board[start[0]][start[1]]
    if piece != player and piece != player.upper():
        return False
    if board[end[0]][end[1]] is not None:
        return False
    if has_capture_moves(board, player):
        return False
    if piece == 'w' and end[0] >= start[0]:
        return False
    if piece == 'b' and end[0] <= start[0]:
        return False
    if abs(start[0] - end[0]) == 1 and abs(start[1] - end[1]) == 1:
        return True
    if piece in ('W', 'B'):
        dr = end[0] - start[0]
        dc = end[1] - start[1]
        if abs(dr) == abs(dc):
            step_r = dr // abs(dr)
            step_c = dc // abs(dc)
            r, c = start[0] + step_r, start[1] + step_c
            while (r, c) != end:
                if board[r][c] is not None:
                    return False
                r += step_r
                c += step_c
            return True
    return False

def is_valid_capture(board, player, start, end):
    if not (is_valid_position(start) and is_valid_position(end)):
        return False
    piece = board[start[0]][start[1]]
    if piece != player and piece != player.upper():
        return False
    if board[end[0]][end[1]] is not None:
        return False
    mid_r = (start[0] + end[0]) // 2
    mid_c = (start[1] + end[1]) // 2
    if not is_valid_position((mid_r, mid_c)):
        return False
    if abs(start[0] - end[0]) == 2 and abs(start[1] - end[1]) == 2:
        if board[mid_r][mid_c] in ('b', 'B') if player == 'w' else board[mid_r][mid_c] in ('w', 'W'):
            return True
    if piece in ('W', 'B'):
        dr = end[0] - start[0]
        dc = end[1] - start[1]
        if abs(dr) == abs(dc) and abs(dr) > 1:
            step_r = dr // abs(dr)
            step_c = dc // abs(dc)
            r, c = start[0] + step_r, start[1] + step_c
            opponent_found = False
            while (r, c) != end:
                if board[r][c] in ('b', 'B') if player == 'w' else board[r][c] in ('w', 'W'):
                    if opponent_found:
                        return False
                    opponent_found = True
                elif board[r][c] is not None:
                    return False
                r += step_r
                c += step_c
            return opponent_found
    return False

def make_move(board, start, end):
    piece = board[start[0]][start[1]]
    board[start[0]][start[1]] = None
    board[end[0]][end[1]] = piece
    if piece == 'w' and end[0] == 0:
        board[end[0]][end[1]] = 'W'
    if piece == 'b' and end[0] == 7:
        board[end[0]][end[1]] = 'B'

def make_capture(board, start, end):
    piece = board[start[0]][start[1]]
    board[start[0]][start[1]] = None
    board[end[0]][end[1]] = piece
    mid_r = (start[0] + end[0]) // 2
    mid_c = (start[1] + end[1]) // 2
    if abs(start[0] - end[0]) == 2 and abs(start[1] - end[1]) == 2:
        board[mid_r][mid_c] = None
    elif piece in ('W', 'B'):
        dr = end[0] - start[0]
        dc = end[1] - start[1]
        step_r = dr // abs(dr)
        step_c = dc // abs(dc)
        r, c = start[0] + step_r, start[1] + step_c
        while (r, c) != end:
            if board[r][c] is not None:
                board[r][c] = None
            r += step_r
            c += step_c
    if piece == 'w' and end[0] == 0:
        board[end[0]][end[1]] = 'W'
    if piece == 'b' and end[0] == 7:
        board[end[0]][end[1]] = 'B'

def check_winner(board):
    white_pieces = sum(row.count('w') + row.count('W') for row in board)
    black_pieces = sum(row.count('b') + row.count('B') for row in board)
    if white_pieces == 0:
        return 'b'
    if black_pieces == 0:
        return 'w'
    return None

def main():
    board = create_board()
    player = 'w'
    while True:
        print_board(board)
        print(f"Player {player}'s turn")
        winner = check_winner(board)
        if winner:
            print(f"Player {winner} wins!")
            break
        if not any(board[i][j] in (player, player.upper()) for i in range(8) for j in range(8)):
            print(f"Player {'b' if player == 'w' else 'w'} wins!")
            break
        start = tuple(map(int, input("Enter start position (row col): ").split()))
        end = tuple(map(int, input("Enter end position (row col): ").split()))
        if has_capture_moves(board, player):
            if is_valid_capture(board, player, start, end):
                make_capture(board, start, end)
                if get_capture_moves(board, player, end):
                    print("You must continue capturing!")
                    continue
                player = 'b' if player == 'w' else 'w'
            else:
                print("Invalid capture move")
        elif is_valid_move(board, player, start, end):
            make_move(board, start, end)
            player = 'b' if player == 'w' else 'w'
        else:
            print("Invalid move")

if __name__ == "__main__":
    main()
