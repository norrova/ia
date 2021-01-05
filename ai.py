import numpy as np
import main
import time
import random

def get_cell_ai(height, width):
    return {"x": random.randrange(0, width - 1), "y": random.randrange(0, height - 1)}


def get_variables(game_param):
    variables = []
    for y in reversed(range(0, game_param["height"])):
        for x in range(0, game_param["width"]):
            cell = {"x": x, "y": y}
            if (cell not in game_param["revealed"] 
            and cell not in  game_param["flagged"]):
                    variables.append(cell)
    return variables

def get_matrix_A_B(game_param, variables):
    A = []
    B = []
    for y in reversed(range(0, game_param["height"])):
        for x in range(0, game_param["width"]):
            cell = {"x": x, "y": y}
            if cell in game_param["revealed"]:
                neighbors = main.get_surrounding_cells(game_param["height"], game_param["width"], cell)
                surronding_variables = []
                flag = 0
                for neighbor in neighbors:
                    if neighbor in game_param["flagged"]:
                        flag += 1
                    elif neighbor in variables:
                        surronding_variables.append(neighbor)
                nb_surronding_variables = len(surronding_variables)  
                if (nb_surronding_variables > 0):
                    line = [0] * len(variables)
                    for variable in surronding_variables:
                        index = variables.index(variable)
                        line[index] = 1
                    res = max(0, game_param["map"][cell['y']][cell['x']] - flag)
                    A.append(line)
                    B.append([res])
    if (len(A) > 0):
        A.append([1]*len(variables))
        B.append([ max(0, game_param["nb_bombs"] - len(game_param["flagged"]))])
    return {'A': A, 'B': B}
                
def pinv(A, B):
    A = np.matrix(A)
    pinv = np.linalg.pinv(A)
    return pinv * np.matrix(B)

def roundNumbers(numbers):
    tmp = np.asarray(numbers)
    for index in range(0, len(tmp) - 1):
        tmp[index] = np.around(tmp[index], decimals=1)
    return tmp

def get_cells_actions(game_param, variables, numbers):
    cells_actions = []
    index = 0
    while index < len(variables):
        neighbors = main.get_surrounding_cells(game_param["height"], game_param["width"], variables[index])
        cell_revealed = False
        for neighbor in neighbors:
            if neighbor in game_param["revealed"]:
                cell_revealed = True
                break
        if (cell_revealed):
            number = numbers[index]
            if number >= 0.99:
                cells_actions.append([1, variables[index]])
            elif number <= 0:
                cells_actions.append([0, variables[index]])
        index += 1
    if (len(variables) == 1 and len(cells_actions) == 0):
        cells_actions.append([0, variables[0]])
    return cells_actions

def run_ai(game_param):
    stop = False
    if not main.win(game_param):
        while not stop:
            main.show_map(game_param)
            time.sleep(1)
            variables = get_variables(game_param)
            matrix = get_matrix_A_B(game_param, variables)
            numbers = roundNumbers(pinv(matrix['A'], matrix['B']))
            cells_actions = get_cells_actions(game_param, variables, numbers)
            for cell in cells_actions:
                main.apply_user_action(game_param, cell[0], cell[1])
                if main.win(game_param) or main.lose(game_param, cell[1]):
                    stop = True
                    break
    print("End game !")
