import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linear_sum_assignment

def load_responses():
    with open('Tindeur.csv', newline='') as responses_file:
        entries = responses_file.readlines()[1:]

        responses = {}
        users = []

        for row in entries:

            row = row.replace('"','')
            split_row = row.split(',')[1:]

            pseudo = split_row[0].replace('@','')
            split_row = split_row[1:]
            users.append(pseudo)

            n = len(split_row)
            response = ['' for i in range(n)]

            for i in range(n):
                if ';' in split_row[i]:
                    response[i] = split_row[i].split(';')
                else:
                    try:
                        response[i] = int(split_row[i])
                    except Exception:
                        response[i] = split_row[i]

            for i in [1, 2, 18, 19]:
                if type(response[i]) == str:
                    response[i] = [response[i]]
            
            responses[pseudo] = response

        return users, responses


def genre(user1, user2):
    res = 30
    if not('Aucun' in user1[1] or 'Aucun' in user2[1]):
        if user1[0] in user2[1]:
            res = 15
            if user2[0] in user1[1]:
                res = 0
    return res

def rel_type(user1, user2):
    res = 30
    for value in user1[2]:
        if value in user2[2]:
            res -= 15
    return res

def talk(user1, user2):
    d1 = abs(user1[3] - user2[4])
    d2 = abs(user1[4] - user2[3])
    return d1 + d2

def trait(user1, user2):
    res = 0
    for i in [5, 6, 7, 8, 10, 11, 13, 15, 16, 17]:
        d = abs(user1[i] - user2[i])
        res += 2 * d
    return res

def food(user1, user2):
    d1 = abs(user1[12] - user2[14])
    d2 = abs(user1[14] - user2[12])
    return d1 + d2

def fidelity(user1, user2):
    if user1[9] == user2[9]:
        return 0
    elif (user1[9] in ['Oui', 'Non'] and user2[9] not in ['Oui', 'Non']) or (user2[9] in ['Oui', 'Non'] and user1[9] not in ['Oui', 'Non']):
        return 10
    else:
        return 20

def music(user1, user2):
    res = 28
    for value in user1[-4]:
        if value in user2[-4]:
            res -= 4
    return res

def griffor(user1, user2):
    if user1[-2] == 'Non' or user2[-2] == 'Non' or type(user1[-1]) != int or type(user2[-1]) != int:
        return 20
    else:
        return int((abs(user1[-1] - user2[-1])) / 10)


def compatibility(user1, user2):
    res = 0
    res += genre(user1, user2)
    res += rel_type(user1, user2)
    res += talk(user1, user2)
    res += trait(user1, user2)
    res += food(user1, user2)
    res += fidelity(user1, user2)
    res += music(user1, user2)
    res += griffor(user1, user2)
    return res


def compatibility_matrix(users, responses):
    n = len(users)
    comp_matrix = np.zeros((n, n))
    comp_matrix.fill(1000)
    for i in range(n):
        user1 = responses[users[i]]
        for j in range(i+1, n):
            user2 = responses[users[j]]
            comp_matrix[i, j] = compatibility(user1, user2)
            comp_matrix[j, i] = comp_matrix[i, j]
    return np.clip(comp_matrix * 2 - 80, 0, 255)


def show_matrix():
    users, responses = load_responses()
    comp_matrix = (255 - compatibility_matrix(users, responses)) / 255 * 100

    plt.imshow(comp_matrix, cmap='inferno', vmin=0, vmax=100)
    plt.xticks(list(range(len(users))), users, rotation='vertical')
    plt.yticks(list(range(len(users))), users)
    plt.title('Compatibility matrix (%)')
    plt.colorbar()
    plt.show()


def most_compatible():
    users, responses = load_responses()
    comp_matrix = compatibility_matrix(users, responses)
    n = len(users)
    with open('most_compatible.txt', 'w') as file:
        res = ''
        for i in range(n):
            m = float('inf')
            index = -1
            for j in range(n):
                if j != i and comp_matrix[i, j] < m:
                    m = comp_matrix[i, j]
                    index = j
            comp = round((255 - comp_matrix[i, index]) / 255 * 100, 1)
            res += '{} - {} : {}%\n'.format(users[i], users[index], comp)
        file.write(res)


def matches():
    users, responses = load_responses()
    comp_matrix = compatibility_matrix(users, responses)
    row_ind, col_ind = linear_sum_assignment(comp_matrix)
    with open('results.txt', 'w') as file:
        matches_list = []
        for k in range(len(row_ind)):
            i = row_ind[k]
            j = col_ind[k]
            comp = (255 - comp_matrix[i, j]) / 255 * 100
            matches_list.append(((i,j),comp))
        chosen_indexes = []
        res = ''
        for match in matches_list:
            i = match[0][0]
            j = match[0][1]
            comp = round(match[1],1)
            if i not in chosen_indexes and j not in chosen_indexes:
                chosen_indexes += [i, j]
                res += '{} - {} | {} % compatibles\n'.format(users[i], users[j], comp)
        file.write(res)

most_compatible()