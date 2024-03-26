from random import shuffle
import json

SUITS = ["C", "D", "S", "H"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]
# 50 + 10 * 5 + 4 = 104
CARD_COUNT = 104


class GameState:
    def __init__(self, grid, deck, grid_str):
        self.grid = grid
        self.deck = deck
        self.grid_str = grid_str


def compare_card_ranks(card1, card2):
    rank1 = RANKS.index(card1[1])
    rank2 = RANKS.index(card2[1])
    return -1 if rank1 < rank2 else 1 if rank1 > rank2 else 0


def clean(grid):
    # remove complete builds
    for k in range(0, 10):
        for i in range(1, len(grid)):
            if grid[-i][k] is not None and grid[-i][k]["visible"] and grid[-i][k]["card"][1] == "A":
                if all([i+j <= len(grid) and grid[-i-j][k] is not None and grid[-i-j][k]["card"][1] == RANKS[j] and grid[-i-j][k]["visible"] for j in range(13)]):
                    for j in range(13):
                        grid[-i-j][k] = None
    # remove any empty rows
    for i in range(len(grid)-1, 0, -1):
        if all([x is None for x in grid[i]]):
            grid.pop(i)
    # if there is a hanging ## (hidden card), flip it over
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] is not None and not grid[i][j]["visible"]:
                if i >= 0 and (len(grid) <= i + 1 or grid[i + 1][j] is None):
                    grid[i][j]["visible"] = True
    return grid


def move_natural_build(grid, deck, card1, col):
    # to find card2, we will find the highest i value in the column where grid[i][col] is not None
    card2 = (col, len(grid))
    i = 0
    while (card2[1] >= len(grid) or grid[card2[1]][col] is None) and i != len(grid):
        i += 1
        card2 = (col, len(grid)-i)

    c1 = grid[card1[1]][card1[0]]
    c2 = grid[card2[1]][card2[0]]
    if c1 is None or (c2 is None and card2[1] != 0):
        return False, False, grid, deck
    # valid:
    if c1["visible"] and (c2 is None or c2["visible"]):
        # if c1["card"][1] < c2["card"][1]: -- valid
        if c2 is None or compare_card_ranks(c1["card"], c2["card"]) == -1:
            # check to make sure all the cards following c1 are in descending order and the same suit
            i = card1[1]
            while i+1 < len(grid) and grid[i+1][card1[0]] is not None and grid[i][card1[0]]["visible"]:
                if compare_card_ranks(grid[i][card1[0]]["card"], grid[i + 1][card1[0]]["card"]) != 1 or grid[i][card1[0]]["card"][0] != grid[i + 1][card1[0]]["card"][0]:
                    return False, False, grid, deck
                i += 1
            # move the cards to the new location
            for j in range(card1[1], i+1):
                if j - card1[1] + card2[1] + 1 >= len(grid):
                    grid.append([])
                    for _ in range(10):
                        grid[-1].append(None)
                grid[j - card1[1] + card2[1] + 1 -
                     (1 if c2 is None else 0)][card2[0]] = grid[j][card1[0]]
                grid[j][card1[0]] = None
            # check if the build is complete
            cleared_build = False
            # only need to check card2.x column
            for i in range(1, len(grid)):
                # if this card is an ace, then we start checking for a completion
                if grid[-i][card2[0]] is not None and grid[-i][card2[0]]["visible"] and grid[-i][card2[0]]["card"][1] == "A":
                    # check if the build is complete
                    if all([i+j < len(grid) and grid[-i-j][card2[0]] is not None and grid[-i-j][card2[0]]["card"][1] == RANKS[j] and grid[-i-j][card2[0]]["visible"] for j in range(13)]):
                        cleared_build = True
                        break
                    else:
                        break
            return True, cleared_build, clean(grid), deck

    return False, False, grid, deck
    # for each card below the first card, check if it is the same suit and a lower rank


def create_deck(num_suits=1):
    if num_suits > 4:
        return None
    # 1 suit: 104 / 13 = 8
    # 2 suits: 104 / 26 = 4
    # 3 suits: 104 / 39 = 2 + 2/3 (2 suits with 3 sets, 1 suit with 2 sets)
    # 4 suits: 104 / 52 = 2
    deck = []
    if num_suits == 3:
        for _ in range(2):
            for suit in SUITS[:3]:
                for rank in RANKS:
                    deck.append(suit + rank)
        for suit in SUITS[:2]:
            for rank in RANKS:
                deck.append(suit + rank)
        return deck
    for _ in range(CARD_COUNT // (num_suits * 13)):
        for suit in SUITS[:num_suits]:
            for rank in RANKS:
                deck.append(suit + rank)
    return deck


def shuffle_deck(deck):
    shuffle(deck)
    return deck


def deal_deck(deck):
    grid = []
    grid.append([])
    for i in range(4):
        grid.append([])
        for _ in range(10):
            grid[i].append({"card": deck.pop(), "visible": False})
    for _ in range(4):
        grid[4].append({"card": deck.pop(), "visible": False})
    grid.append([])
    for _ in range(4):
        grid[-1].append({"card": deck.pop(), "visible": True})
    for _ in range(6):
        grid[-2].append({"card": deck.pop(), "visible": True})
        grid[-1].append(None)
    return grid, deck


def display_grid(grid, deck_len=50):
    # __ - empty
    # 2C - 2 of clubs
    # ## - hidden card
    print(f"draw: {deck_len}")
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] is not None and grid[i][j]["visible"]:
                print(grid[i][j]["card"], end=" ")
            elif grid[i][j] is not None and not grid[i][j]["visible"]:
                print("##", end=" ")
            else:
                print("__", end=" ")
        print()


def draw(grid, deck):
    if len(deck) == 0:
        return grid, deck
    grid.append([])
    for _ in range(10):
        grid[-1].append(None)
    for i in range(len(grid)-1, -1, -1):
        for j in range(len(grid[i])):
            if grid[i][j] is None and (i == 0 or grid[i-1][j] is not None):
                grid[i][j] = {"card": deck.pop(), "visible": True}
    return clean(grid), deck


def send_grid_to_file(grid, deck, file="game"):
    with open(f"{file}.txt", "w") as f:
        f.write("draw: 50\n")
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if grid[i][j] is not None and grid[i][j]["visible"]:
                    f.write(grid[i][j]["card"] + " ")
                elif grid[i][j] is not None and not grid[i][j]["visible"]:
                    f.write("## ")
                else:
                    f.write("__ ")
            f.write("\n")

    # write the grid as a json with the remaining cards as another parm:
    # {"grid": grid, "remaining": deck}
    with open(f"{file}.json", "w") as f:
        json.dump({"grid": grid, "remaining": deck}, f, indent=2)


def output_game_as_str(grid):
    game_str = "draw: 50\n"
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] is not None and grid[i][j]["visible"]:
                game_str += grid[i][j]["card"] + " "
            elif grid[i][j] is not None and not grid[i][j]["visible"]:
                game_str += "## "
            else:
                game_str += "__ "
        game_str += "\n"
    return game_str


def load_game_from_file(filename="game.json"):
    with open(filename, "r") as f:
        game = json.load(f)
    return game["grid"], game["remaining"]


def test():
    grid, deck = load_game_from_file("game.json")

    display_grid(grid, len(deck))
    over = False
    while not over:
        over = True
        for i in grid:
            for j in i:
                if j is not None:
                    over = False
        if over:
            break
        input1 = input("Enter the first card (or draw): ").strip()
        if input1 == "draw":
            draw(grid, deck)
            display_grid(grid, len(deck))
            continue
        input1 = [int(i.strip()) for i in input1.split(' ')]
        input2 = int(input("Enter the column to move to: ").strip())
        moved, cleared_build, grid, deck = move_natural_build(
            grid, deck, (input1[0], input1[1]), input2)
        print(
            f"moved, cleared_build, grid, deck = move_natural_build(grid, deck, ({input1[0]}, {input1[1]}), {input2})")
        display_grid(grid, len(deck))
        print(moved, cleared_build)

        # save to file
        send_grid_to_file(grid, deck, "modified_game")


if __name__ == "__main__":
    test()
