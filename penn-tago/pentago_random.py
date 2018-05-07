import numpy as np
import penntago_game
import penntago_ai


def random_trials(num_epochs, epoch_size, print_results):
    if print_results:
        print("Columns: Black Win, White Win, Tie")
    for _ in range(0, num_epochs):
        results = np.zeros(epoch_size)

        for i in range(0, epoch_size):
            game = penntago_game.Game(penntago_ai.Player("random"), penntago_ai.Player("random"))
            while game.status_code == -1:
                game.take_turn()
            results[i] = game.status_code

        black_wins = np.sum(results == 0)
        white_wins = np.sum(results == 1)
        ties = np.sum(results == 2)

        print(str(black_wins) + ", " + str(white_wins) + ", " + str(ties))


if __name__ == "__main__":
    random_trials(1, 100, True)
