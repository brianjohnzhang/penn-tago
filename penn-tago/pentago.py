import numpy as np


"""
This code provides the backend to a game of Pentago. It provides several functions for Pentago play.
"""


# Create a blank new game
def init_game():
    board_state = np.zeros((3, 6, 6))
    return board_state


# Return a new board state after processing the move
def move(board_state, new_position, rotate_quadrant, rotate_clockwise):
    # Check out the current board state to see if it is possible
    # if is_valid_board_state(board_state):
    #     game_complete_status = game_complete(board_state)
    #     if game_complete_status[0]:
    #         if game_complete_status[1] == 0:
    #             raise ValueError("Black player has already won.")
    #         else:
    #             raise ValueError("White player has already won.")
    # Check that the other variables are valid
    if not (0 <= new_position[0] < 6 and 0 <= new_position[1] < 6):
        raise ValueError("Invalid position, both indices must be between [0, 6).")
    elif not (1 <= rotate_quadrant <= 4):
        raise ValueError("Invalid quadrant: must be integer between [1, 4].")
    elif (rotate_clockwise is not True and rotate_clockwise is not False) and not (0 <= rotate_clockwise <= 1):
        raise TypeError("Rotate quadrant clockwise must be either True, False, 0 or 1.")

    # If there is already something in that spot, reject the move
    if np.any(board_state[0:2, new_position[1], new_position[0]] == 1):
        raise ValueError("That position on the board is already occupied.")
    else:
        board_state[int(board_state[2, 0, 0]), new_position[1], new_position[0]] = 1

    # Turn the appropriate quadrant
    if rotate_quadrant == 1:
        if rotate_clockwise:
            board_state[0:2, 0:3, 0:3] = np.rot90(board_state[0:2, 0:3, 0:3], 1, [1, 2])
        else:
            board_state[0:2, 0:3, 0:3] = np.rot90(board_state[0:2, 0:3, 0:3], 1, [2, 1])
    elif rotate_quadrant == 2:
        if rotate_clockwise:
            board_state[0:2, 3:6, 0:3] = np.rot90(board_state[0:2, 3:6, 0:3], 1, [1, 2])
        else:
            board_state[0:2, 3:6, 0:3] = np.rot90(board_state[0:2, 3:6, 0:3], 1, [2, 1])
    elif rotate_quadrant == 3:
        if rotate_clockwise:
            board_state[0:2, 0:3, 3:6] = np.rot90(board_state[0:2, 0:3, 3:6], 1, [1, 2])
        else:
            board_state[0:2, 0:3, 3:6] = np.rot90(board_state[0:2, 0:3, 3:6], 1, [2, 1])
    elif rotate_quadrant == 4:
        if rotate_clockwise:
            board_state[0:2, 3:6, 3:6] = np.rot90(board_state[0:2, 3:6, 3:6], 1, [1, 2])
        else:
            board_state[0:2, 3:6, 3:6] = np.rot90(board_state[0:2, 3:6, 3:6], 1, [2, 1])

    # Change the color
    board_state[2, :, :] = 1 - board_state[2, :, :]

    # Return completed game with attached int of whether the game is won:
    # -1: incomplete
    # 0: black won
    # 1: white won
    # 2: tied
    game_complete_status = game_complete(board_state)
    if game_complete_status[0]:
        return board_state, game_complete_status[1]
    else:
        return board_state, -1


# Check if the game is over and return who has won:
# 0: black won
# 1: white won
# 2: tied
def game_complete(board_state):
    # Check for 5-in-a-row
    for i in range(0, 2):
        for y in range(0, 6):
            for x in range(0, 6):
                if board_state[i, y, x] == 1:
                    if x <= 1:
                        if np.sum(board_state[i, y, list(range(x, x + 5))]) == 5:
                            return True, i
                    if y <= 1:
                        if np.sum(board_state[i, y, x]) == 5:
                            return True, i
                    if x <= 1 and y <= 1:
                        if np.sum(board_state[i, list(range(y, y + 5)), list(range(x, x + 5))]) == 5:
                            return True, i
    # If there isn't one, see if the board is full for a tie
    if np.sum(board_state[0:2, :, :]) == 36:
        return True, 2
    # Otherwise, the game hasn't ended
    else:
        return False, 0


# Debug use: determines if a board is valid or not.
def is_valid_board_state(board_state):
    black_pieces = np.sum(board_state[0, :, :])
    white_pieces = np.sum(board_state[1, :, :])
    if not np.all(np.logical_or(board_state == 0, board_state == 1)):
        raise ValueError("Board states are not 0 or 1.")
    elif not np.any(board_state[2, 0, 0] == np.array([0, 1])):
        raise ValueError("Turn array is not 1's or 0's.")
    elif not np.all(board_state[2, 0, 0] == board_state[2, :, :]):
        raise ValueError("Turn array is inconsistent.")
    elif np.any(board_state[0, :, :] + board_state[1, :, :] == 2):
        raise ValueError("A black piece and a white piece are in the same spot.")
    elif board_state[2, 0, 0] == 0 and black_pieces > white_pieces:
        raise ValueError("Black has too many pieces to be going.")
    elif board_state[2, 0, 0] == 0 and black_pieces < white_pieces:
        raise ValueError("Black has too few pieces to be going.")
    elif board_state[2, 0, 0] == 1 and black_pieces > white_pieces + 1:
        raise ValueError("White has too few pieces to be going.")
    elif board_state[2, 0, 0] == 1 and black_pieces < white_pieces + 1:
        raise ValueError("White has too many pieces to be going.")
    else:
        return True


def visualize_board(board_state):
    if board_state[2, 0, 0] == 0:
        print("Turn: BLACK")
    else:
        print("Turn: WHITE")

    for y in reversed(range(0, 6)):
        for x in range(0, 6):
            if board_state[0, y, x] == 1:
                print(' B', end='')
            elif board_state[1, y, x] == 1:
                print(' W', end='')
            else:
                print(' O', end='')
        print('')
