# %%
import tensorflow as tf

import game_generator as gg

# %%
# Reward system
REWARD_FOR_BUILDING_SEQUENCE = 5
REWARD_FOR_EXPOSING_HIDDEN_CARD = 10
REWARD_FOR_CREATING_EMPTY_PILE = 15
REWARD_FOR_BUILDING_ON_HIGHER_CARD_OUT_OF_SUIT = 2
REWARD_FOR_MAXIMIZING_CARD_EXPOSURE_BEFORE_NEW_DEAL = 20
REWARD_FOR_NATURAL_BUILD_POST_SUIT_REMOVAL = 10

# Penalties
PENALTY_FOR_REDUNDANT_MOVE = -10

# Game mechanics
MAXIMUM_EMPTY_PILES = 10  # Assuming Spider Solitaire with 10 tableau piles
MAX_CARDS_PER_SUIT = 13  # Number of cards per suit, from Ace to King

# Neural network parameters - These can be adjusted based on the model's performance and complexity
# Placeholder, adjust based on actual game state representation
NN_INPUT_SHAPE = (10, 10)
NN_LEARNING_RATE = 0.001
NN_BATCH_SIZE = 32
NN_EPOCHS = 100

# Other constants
# Adjust this for training with different difficulty levels (1, 2, 3, or 4 suits)
NUMBER_OF_SUITS = 1
SUITS = ["C", "D", "S", "H"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]
CARD_COUNT = 104

# %%


def parse_game_state(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    draw_count = int(lines[0].split(": ")[1])
    card_matrix = [
        line.strip().split(" ") for line in lines[2:]
    ]  # Skip the first two lines

    # Convert the card matrix into a more structured format, if necessary
    # For now, it's just a list of lists containing the card values or placeholders

    return draw_count, card_matrix


# %%
draw_count, card_matrix = parse_game_state("input.txt")
print(draw_count)
print(card_matrix)

# %%
model = tf.keras.Sequential(
    [
        tf.keras.layers.Input(shape=NN_INPUT_SHAPE),  # Explicit Input layer
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dense(1, activation="sigmoid"),
    ]
)

model.compile(optimizer="adam", loss="binary_crossentropy",
              metrics=["accuracy"])

# %%
# Example of generating game states
num_games = 1000  # Number of games to generate for the dataset
game_states = []
for _ in range(num_games):
    # Or adjust for different levels of difficulty
    deck = gg.create_deck(num_suits=NUMBER_OF_SUITS)
    deck = gg.shuffle_deck(deck)
    grid, remaining_deck = gg.deal_deck(deck)
    game_str = gg.output_game_as_str(grid, remaining_deck)
    game_states.append(gg.GameState(grid, remaining_deck, game_str))
    gg.move_natural_build(grid, remaining_deck, (2, 5), (4, 4))
    exit()

# Example preprocessing function (placeholder)


def preprocess_game_state(game_str):
    # Convert the game_str into a numerical format
    # This function is highly dependent on how you decide to represent the game state to the model
    pass


x_train = [preprocess_game_state(game_str) for game_str in game_states]

y_train = []

model.fit(x_train, y_train, epochs=10)

# %%


def make_move(model, game_state):
    # This function should use the model to predict the best move
    # Update the game state accordingly
    # For now, this is a placeholder showing the structure
    pass


game_over = True
# Loop to play the game
while not game_over:
    # Assuming a function game_over() to check if the game has ended
    make_move(model, card_matrix)
    # Wait for user to update input.txt and re-parse it
    draw_count, card_matrix = parse_game_state("input.txt")
