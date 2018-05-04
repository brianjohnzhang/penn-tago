import pentago as p
import numpy as np
import random


def random_trials(num_epochs, epoch_size, print_results):
    if print_results:
        print("Columns: Black Win, White Win, Tie")
    for _ in range(0, num_epochs):
        results = np.zeros(epoch_size)

        for i in range(0, epoch_size):
            status = -1
            game_state, open_positions = p.init_game()
            while status == -1:
                game_state, open_positions, status = p.move_debug(game_state, random.choice(open_positions),
                                                                  random.randint(1, 4), random.randint(0, 1))
            results[i] = status

        black_wins = np.sum(results == 0)
        white_wins = np.sum(results == 1)
        ties = np.sum(results == 2)

        print(str(black_wins) + ", " + str(white_wins) + ", " + str(ties))


if __name__ == "__main__":
    random_trials(100, 100, True)
