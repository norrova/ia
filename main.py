import json
import os
from random import randrange
import ai

# importation json
def get_json(path):
    file = None
    with open(path) as target:
        file = json.load(target)
    return file

# transformation des clés en chaine de caractères
def keys_to_string(dictionnary):
    keys = list(dictionnary.keys())
    response = ""
    for index in range(0, len(keys)):
        response += ((str(index + 1) + "." + str(keys[index])) + " ")
    return response

# récupération d'un choix selon le dictionnaire passé en paramètre
def get_choice(dictionnary):
    message = keys_to_string(dictionnary)
    valid = False
    while not valid:
        try:
            entry = int(input("Enter your choice " + message + ": "))
            if 1 <= entry <= len(dictionnary):
                valid = True
        except ValueError:
            pass
    return (entry - 1)

# Récupération du niveau
def get_level(levels):
    choice = get_choice(levels)
    return levels[list(levels.keys())[choice]]

# génération de grille avec calcule des voisins
def generate_map(height, width, bombs):
    matrix = []
    for y in range(0, height):
        matrix_x = []
        for x in range(0, width):
            cell = {"x" : x, "y": y}
            if cell in bombs:
                matrix_x.append(-1)
            else:
                matrix_x.append(get_bomb_neighbor(height, width, bombs, cell))
        matrix.append(matrix_x)
    return matrix

# Récupérer le nombre de voisins
def get_bomb_neighbor(height, width, bombs, cell):
    cells = get_surronding_cells(height, width, cell)
    bomb_neighbor = 0
    for cell in cells:
        if cell in bombs:
            bomb_neighbor += 1
    return bomb_neighbor

# Récupération des cellules avoisinantes une cellule
def get_surronding_cells(height, width, cell):
    surronding_cells = []
    for y in range(-1, 2):
        res_y = cell["y"] + y
        if res_y >= 0 and res_y < height:
            for x in range(-1, 2):
                res_x = cell["x"] + x
                if  res_x >= 0 and res_x < width:
                    surronding_cells.append({"x": res_x, "y": res_y})
    return surronding_cells

# génération des bombes aléatoire
def generate_bombs(height, width, nb_bomb, excluded_cells = []):
    bombs = []
    for index in range(0, nb_bomb):
        valid = False
        while not valid:
            coordinate = {"x": randrange(0, width), "y": randrange(0, height)}
            if coordinate not in bombs and coordinate not in excluded_cells:
                valid = True
                bombs.append(coordinate)
    return bombs

# Récupération d'une cellule utilisateur
def get_cell(height, width):
    axes = {"x": height, "y": width}
    coordinate = {}
    for axe in axes.keys():
        response = ("Axe " + str(axe) + " between 1 and " + str(axes[axe]) + " : ")
        valid = False
        while not valid:
            try:
                entry = int(input(response))
                if 1 <= entry <= axes[axe]:
                    valid = True
                    coordinate.update({axe: entry - 1})
            except ValueError:
                pass
    return coordinate

# Convertir un nombre en emoji
def number_to_emoji(number):
    if number > 8:
        raise IndexError
    emojis = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣']
    return emojis[number]

# Affichage de la carte
def show_map(game_param):
    os.system("clear")
    for y in reversed(range(0, game_param["height"])):
        for x in range(0, game_param["width"]):
            cell = {"x": x, "y": y}
            emoji = None
            if cell in game_param["revealed"]:
                if cell in game_param["bombs"]:
                    emoji = "💣"
                elif 0 == game_param["map"][y][x]:
                    emoji = "🌿"
                else:
                    emoji = number_to_emoji(game_param["map"][y][x])
            elif cell in game_param["flagged"]:
                emoji = "🚩"
            else:
                emoji = "⬜️"
            print(" " + emoji + " ", end='')
        print("")

# Appliquer le choix utilisateur
def apply_user_action(game_param, choice, cell):
    if choice == game_param["actions"]["Dig"]:
        if 0 == game_param["map"][cell["y"]][cell["x"]]:
            cells_propagation(game_param, [cell])
        elif cell not in game_param["flagged"]:
            game_param["revealed"].append(cell)
    elif (choice == game_param["actions"]["Flag"]
        and cell not in game_param["flagged"]):
        if cell in game_param["bombs"]:
            game_param["nb_bombs"] -= 1
        game_param["flagged"].append(cell)
    elif (choice == game_param["actions"]["Unflag"]
        and cell in game_param["flagged"]):
        game_param["flagged"].remove(cell)

# Algorithme de propagation
def cells_propagation(game_param, to_discover):
    tmp_cells = []
    for cell_discover in to_discover:
        if cell_discover not in game_param["revealed"]:
            game_param["revealed"].append(cell_discover)
        for cell in get_surronding_cells(game_param["height"], game_param["width"], cell_discover):
            if cell not in to_discover and cell not in game_param["revealed"]:
                if 0 == game_param["map"][cell["y"]][cell["x"]]:
                    tmp_cells.append(cell)
                else:
                    game_param["revealed"].append(cell)
    if len(tmp_cells) > 0:
        cells_propagation(game_param, tmp_cells)

def reveal_all_cells(game_param):
    game_param["revealed"].clear()
    for y in reversed(range(0, game_param["height"])):
        for x in range(0, game_param["width"]):
            cell = {"x": x, "y": y}
            game_param["revealed"].append(cell)

# Vérification gagnant
def win(game_param):
    win = False
    if len(game_param["revealed"]) == game_param["nb_total_cells"]:
        reveal_all_cells(game_param)
        show_map(game_param)
        print("Congrats you win !")
        win = True
    return win

# Vérification perdant
def lose(game_param, cell):
    lose = False
    if cell in game_param["bombs"] and cell not in game_param["flagged"] and cell in game_param["revealed"]:
        reveal_all_cells(game_param)
        show_map(game_param)
        print("You lose")
        lose = True
    return lose

# Initialisation
def setup(level, cell):
    game_param = level
    game_param.update(nb_bombs = level["mines"])
    game_param.update(nb_total_cells = ((game_param["height"] * game_param["width"]) - game_param["mines"]))
    excluded_cells = get_surronding_cells(game_param["height"], game_param["width"], cell)
    game_param.update(bombs = generate_bombs(game_param["height"], game_param["width"], game_param["mines"], excluded_cells))
    game_param.update(map = generate_map(game_param["height"], game_param["width"], game_param["bombs"]))
    game_param.update(revealed = [], flagged = [], variables = [])
    game_param.update(actions = {
        "Dig": 0,
        "Flag": 1,
        "Unflag": 2
    })
    cells_propagation(game_param, [cell])
    return game_param
  
# Lancement partie
def run(game_param):
    stop = False
    show_map(game_param)
    if not win(game_param):
        while not stop:
            show_map(game_param)
            choice = get_choice(game_param["actions"])
            cell = get_cell(game_param["height"], game_param["width"])
            if cell not in game_param["revealed"]:
                apply_user_action(game_param, choice, cell)
            if win(game_param) or lose(game_param, cell):
                stop = True
    print("End game !")
            
# Entrypoint
if __name__ == "__main__":
    path_levels = "./levels.json"
    levels = get_json(path_levels)
    level = get_level(levels)
    # cell = get_cell(level["height"], level["width"])
    cell = ai.get_cell(level["height"], level["width"])
    game_param = setup(level, cell)
    ai.runAI(game_param)
    # run(game_param)
