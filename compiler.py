# Seyed MohammadMahdi Sajjadi 99108161
# Amin Hassanzadeh 98105705

import json
import os

from anytree import Node, RenderTree


def get_next_token():
    if tokens[1].__contains__('.'):
        tokens.pop(0)
    result = tokens[0:3]
    tokens.pop(1)
    tokens.pop(1)
    return result


sc = open('scanner.py')
exec(sc.read())

with open('table.json', 'r') as read_file:
    y = json.load(read_file)

parse_table = y['parse_table']
grammar = y['grammar']
follow = y['follow']

f = open('tokens.txt', 'r')
tokens = f.read()
tokens = tokens.split()
action = "Start"
stck = [0]
nodes = []
fl = open('syntax_errors.txt', 'w')
error_found = False
end = False
currToken = get_next_token()
while action != "accept":
    x = stck[len(stck) - 1].__str__()
    if currToken[1].startswith('(ID') or currToken[1].startswith('(NUM') or currToken[1].startswith('(WHITESPACE'):
        s = currToken[1][1:-1]
    else:
        s = currToken[2][:-1]
    key = parse_table[x]
    if key.get(s):
        action = parse_table[x][s]

        if action.startswith("shift"):
            actions = action.split("_")
            stck.append(currToken[1] + ' ' + currToken[2])
            stck.append(actions[1])
            nodes.append(Node(currToken[1] + ' ' + currToken[2]))
            currToken = get_next_token()

        elif action.startswith("reduce"):
            actions = action.split("_")
            numberOfGrammars = actions[1]
            gram = grammar[numberOfGrammars.__str__()]
            if gram[2] != 'epsilon':
                stck = stck[:len(stck) - (2 * (len(gram) - 2))]
            firstOfGrammar = gram[0]
            stck.append(firstOfGrammar)
            stringWithGoto = parse_table[stck[len(stck) - 2].__str__()][stck[len(stck) - 1]]
            splitStringWithGoto = stringWithGoto.split("_")
            stck.append(splitStringWithGoto[1])
            if gram[2] == 'epsilon':
                parent = Node(grammar[numberOfGrammars][0], children=[Node(gram[2])])
            else:
                parent = Node(grammar[numberOfGrammars][0], children=nodes[(len(nodes) - len(gram) + 2):])
                nodes = nodes[:len(nodes) - len(gram) + 2]
            nodes.append(parent)

    else:
        error_found = True
        lineno = '#' + currToken[0].replace('.', ' ')
        if currToken[1].startswith('(NUM') or currToken[1].startswith('(ID'):
            fl.writelines(lineno + ': syntax error , illegal ' + currToken[2][:-1] + '\n')
        else:
            fl.writelines(lineno + ': syntax error , illegal ' + s + '\n')
        currToken = get_next_token()
        if currToken[1].startswith('(ID') or currToken[1].startswith('(NUM') or currToken[1].startswith('(WHITESPACE'):
            s = currToken[1][1:-1]
        else:
            s = currToken[2][:-1]

        found = False
        while len(stck) > 0:
            top = stck[len(stck) - 1].__str__()
            listOfCells = []
            for cell in parse_table[top]:
                if parse_table[top][cell].startswith('goto'):
                    found = True
                    listOfCells.append(cell)
            if found is True:
                break
            stck = stck[:-1]
            nodes.pop()
            fl.writelines('syntax error , discarded ' + stck.pop() + ' from stack' + '\n')
        listOfCells.sort()
        found = False
        while True:
            for key in listOfCells:
                if s in follow[key]:
                    found = True
                    break
            if found is True:
                break
            lineno = '#' + currToken[0].replace('.', ' ')
            if currToken[1].startswith('(NUM') or currToken[1].startswith('(ID'):
                fl.writelines(lineno + ': syntax error , discarded ' + currToken[2][:-1] + ' from input' + '\n')
            else:
                fl.writelines(lineno + ': syntax error , discarded ' + s + ' from input' + '\n')
            currToken = get_next_token()
            lineno = '#' + currToken[0].replace('.', ' ')
            if currToken[1].startswith('(ID') or currToken[1].startswith('(NUM') or currToken[1].startswith(
                    '(WHITESPACE'):
                s = currToken[1][1:-1]
            else:
                s = currToken[2][:-1]
                if s == '$':
                    fl.writelines(lineno + ': syntax error , Unexpected EOF' + '\n')
                    end = True
                    break
        if end is True:
            break
        lineno = '#' + currToken[0].replace('.', ' ')
        fl.writelines(lineno + ': syntax error , missing ' + key + '\n')
        stck.append(key)
        nodes.append(Node(key))
        stck.append(parse_table[top][key].split('_')[1])
if error_found is False:
    fl.writelines('There is no syntax error.' + '\n')
Node('$', parent)
fl.close()
read_file.close()
out = open('parse_tree.txt', 'w', encoding='utf8')
if end is False:
    for pre, fill, node in RenderTree(parent):
        out.writelines("%s%s\n" % (pre, node.name))
        print("%s%s" % (pre, node.name))
