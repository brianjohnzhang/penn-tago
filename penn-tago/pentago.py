import numpy as np


"""
This code provides the backend to a game of Pentago. It provides several functions for Pentago play.
"""


ALL_ROTATIONS = [(1, False), (2, False), (3, False), (4, False), (1, True), (2, True), (3, True), (4, True)]


# Create and return a fresh game_state, as well as a list of open move positions (all of them)
def init_game():
    return np.zeros((3, 6, 6)), find_valid_moves(np.zeros((3, 6, 6))), -1


# Find all open array vectors
#   Input: game_state, a valid (3, 6, 6) numpy array game state
#   Output: a list of tuples containing open move positions in array coordinates
def find_valid_moves(game_state):
    open_positions = []
    for row in range(0, 6):
        for col in range(0, 6):
            if game_state[0, row, col] == 0 and game_state[1, row, col] == 0:
                open_positions.append((row, col))
    return [[pos, rot[0], rot[1]] for pos in open_positions for rot in ALL_ROTATIONS]


# From an game_state, determine if the game is over
#   Input: game_state, a valid (3, 6, 6) numpy array game state
#   Output: an int, 0: black won, 1: white won, 2: tied
def _check_game_status(game_state):
    pieces = [np.sum(game_state[0, :, :]), np.sum(game_state[1, :, :])]
    # Can't have 5 in a row yet
    if pieces[0] < 5:
        return -1
    # Check for 5-in-a-row, brute-force
    for i in range(0, 2):
        enough_pieces = True
        for row in range(0, 6):
            for col in range(0, 6):
                if game_state[i, row, col] == 1:
                    if row <= 1:
                        if np.sum(game_state[i, list(range(row, row + 5)), col]) == 5:
                            return i
                    if col <= 1:
                        if np.sum(game_state[i, row, list(range(col, col + 5))]) == 5:
                            return i
                    if row <= 1 and col <= 1:
                        if np.sum(game_state[i, list(range(row, row + 5)), list(range(col, col + 5))]) == 5:
                            return i
                    pieces[i] = pieces[i] - 1
                if pieces[i] < 5:
                    enough_pieces = False
                    break
            if not enough_pieces:
                break

    # If there isn't one, see if the board is full for a tie
    if np.sum(game_state[0:2, :, :]) == 36:
        return 2
    # Otherwise, the game hasn't ended
    else:
        return -1


# Checks if an game_state is valid or not
#   Input: game_state, a valid (3, 6, 6) numpy array game state
#   Output: True or an error
def _is_valid_game_state(game_state):
    black_pieces = np.sum(game_state[0, :, :])
    white_pieces = np.sum(game_state[1, :, :])
    if not np.all(np.logical_or(game_state == 0, game_state == 1)):
        raise ValueError("Board states are not 0 or 1.")
    elif not np.any(game_state[2, 0, 0] == np.array([0, 1])):
        raise ValueError("Turn array is not 1's or 0's.")
    elif not np.all(game_state[2, 0, 0] == game_state[2, :, :]):
        raise ValueError("Turn array is inconsistent.")
    elif np.any(game_state[0, :, :] + game_state[1, :, :] == 2):
        raise ValueError("A black piece and a white piece are in the same spot.")
    elif game_state[2, 0, 0] == 0 and black_pieces > white_pieces:
        raise ValueError("Black has too many pieces to be going.")
    elif game_state[2, 0, 0] == 0 and black_pieces < white_pieces:
        raise ValueError("Black has too few pieces to be going.")
    elif game_state[2, 0, 0] == 1 and black_pieces > white_pieces + 1:
        raise ValueError("White has too few pieces to be going.")
    elif game_state[2, 0, 0] == 1 and black_pieces < white_pieces + 1:
        raise ValueError("White has too many pieces to be going.")
    else:
        return True


# Debug issues with game_state and moves, and then move
#   Inputs: same as move()
#   Outputs: same as move()
def move_debug(game_state_old, move):
    # Unpack move into subcomponents
    new_position = move[0]
    rotate_quadrant = move[1]
    rotate_clockwise = move[2]

    # Check out the current array state to see if it is possible
    if _is_valid_game_state(game_state_old):
        status_code = _check_game_status(game_state_old)
        if status_code == 0:
            raise ValueError("Black player has already won.")
        elif status_code == 1:
            raise ValueError("White player has already won.")
        elif status_code == 2:
            raise ValueError("The game is tied.")
        # Check that the other variables are valid
        if not (0 <= new_position[0] < 6 and 0 <= new_position[1] < 6):
            raise ValueError("Invalid position, both indices must be between [0, 6).")
        elif not (1 <= rotate_quadrant <= 4):
            raise ValueError("Invalid quadrant: must be integer between [1, 4].")
        elif (rotate_clockwise is not True and rotate_clockwise is not False) and not (0 <= rotate_clockwise <= 1):
            raise TypeError("Rotate quadrant clockwise must be either True, False, 0 or 1.")

        # If there is already something in that spot, reject the move
        if np.any(game_state_old[0:2, new_position[0], new_position[1]] == 1):
            raise ValueError("That position on the board is already occupied.")

    # Continue with regular move function
    return move(game_state_old, move)


# Process a move on a game state
#   Inputs:
#       game_state_old, a valid (3, 6, 6) numpy array game state
#       move, made of:
#           new_position, (row, col) of game_state to be filled. 0 <= x, y < 6
#           rotate_quadrant, quadrants are x-major, or 1: bottom-left, 2: top-left, 3: bottom-right, 4: top-right
#               pieces are laid out in traditional XY, unlike the numpy array
#           rotate_clockwise, boolean, 0 or 1 to indicate rotation direction
#   Output:
#       (game_state_new, open_positions, status_code)
def move(game_state_old, move):
    # Unpack move into subcomponents
    new_position = move[0]
    rotate_quadrant = move[1]
    rotate_clockwise = move[2]

    # Make it safe so that we don't modify the source
    game_state_new = np.copy(game_state_old)

    # Update the correct index
    game_state_new[int(game_state_new[2, 0, 0]), new_position[0], new_position[1]] = 1

    # Turn the appropriate quadrant
    if rotate_quadrant == 1:
        if rotate_clockwise:
            game_state_new[0:2, 0:3, 0:3] = np.rot90(game_state_new[0:2, 0:3, 0:3], 1, [2, 1])
        else:
            game_state_new[0:2, 0:3, 0:3] = np.rot90(game_state_new[0:2, 0:3, 0:3], 1, [1, 2])
    elif rotate_quadrant == 2:
        if rotate_clockwise:
            game_state_new[0:2, 0:3, 3:6] = np.rot90(game_state_new[0:2, 0:3, 3:6], 1, [2, 1])
        else:
            game_state_new[0:2, 0:3, 3:6] = np.rot90(game_state_new[0:2, 0:3, 3:6], 1, [1, 2])
    elif rotate_quadrant == 3:
        if rotate_clockwise:
            game_state_new[0:2, 3:6, 0:3] = np.rot90(game_state_new[0:2, 3:6, 0:3], 1, [2, 1])
        else:
            game_state_new[0:2, 3:6, 0:3] = np.rot90(game_state_new[0:2, 3:6, 0:3], 1, [1, 2])
    elif rotate_quadrant == 4:
        if rotate_clockwise:
            game_state_new[0:2, 3:6, 3:6] = np.rot90(game_state_new[0:2, 3:6, 3:6], 1, [2, 1])
        else:
            game_state_new[0:2, 3:6, 3:6] = np.rot90(game_state_new[0:2, 3:6, 3:6], 1, [1, 2])

    # Change the color
    game_state_new[2, :, :] = 1 - game_state_new[2, :, :]

    # Return completed game with attached int of whether the game is won:
    return game_state_new, find_valid_moves(game_state_new), _check_game_status(game_state_new)


# Creates a console visualization of the board from an game_state
#   Input: game_state, a valid (3, 6, 6) numpy array game state
def show_board(game_state):
    if game_state[2, 0, 0] == 0:
        print("Turn: BLACK")
    else:
        print("Turn: WHITE")

    for y in reversed(range(0, 6)):
        for x in range(0, 6):
            if game_state[0, x, y] == 1:
                print(' B', end='')
            elif game_state[1, x, y] == 1:
                print(' W', end='')
            else:
                print(' O', end='')
        print('')
