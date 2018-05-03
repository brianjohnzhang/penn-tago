import pentago as p
import numpy as np
import random


def random_trials(num_epochs, epoch_size, print_results):
    if print_results:
        print("Columns: Black Win, White Win, Tie")
    for _ in range(0, num_epochs):
        results = np.zeros(epoch_size)

        for i in range(0, epoch_size):
            game_won = False
            board_state = p.init_game()
            while not game_won:
                occupied_tiles = board_state[0] + board_state[1]
                unoccupied = []
                for y in range(0, 6):
                    for x in range(0, 6):
                        if occupied_tiles[y, x] == 0:
                            unoccupied.append([x, y])

                board_state, status_code = p.move(board_state, unoccupied[random.randint(0, len(unoccupied) - 1)], random.randint(1, 4), random.randint(0, 1))
                game_won = status_code > -1
                results[i] = status_code

        black_wins = np.sum(results == 0)
        white_wins = np.sum(results == 1)
        ties = np.sum(results == 2)

        print(str(black_wins) + ", " + str(white_wins) + ", " + str(ties))


if __name__ == "__main__":
    random_trials(100, 1000, True)
