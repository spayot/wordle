import wordle as wd

word = "paper"  # TODO: replace with a random selector from possible answers

game = wd.WordleGame(word)
while not game.is_over:
    guess = input("make a 5-letter guess:")
    guess_outcome = game.record_player_guess(guess)
    print(guess_outcome)
    if game.is_over:
        print("the game is over!")
        if game.solved:
            print(f"you won in {game.number_of_guesses} guesses")
        else:
            print(f"you have used your {game.max_guesses} guesses.")
