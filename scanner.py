global lex_err_bool
lex_err_bool = True
global lex_err
lex_err = ""
global IDs
IDs = []
keyWords = ['if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return', 'endif']
f = open("input.txt", 'r')
fl = open('lexical_errors.txt', 'w')
fs = open('symbol_table.txt', 'w')
ft = open('tokens.txt', 'w')
ftstr = ""
symbol_num = 1
for keyWord in keyWords:
    fs.writelines(f"{symbol_num}.\t{keyWord}\n")
    symbol_num += 1

lines = f.readlines()

i = 1

def isNumToken(word):
    global lex_err
    global lex_err_bool
    i = 0
    for ch in word:
        if ch.isdigit():
            i += 1
            continue
        elif "+ - * = < / ; : ( ) , { } [ ]".__contains__(ch):
            return f"(NUM, {word[:i]}) ", word[i:]
        elif ch.isalpha():
            lex_err_bool = False
            lex_err += f"({word[:i + 1]}, Invalid number)"
            return "", word[i + 1:]
        else:
            lex_err += f"({word[:i + 1]}, Invalid input) "
            lex_err_bool = False
            return "", word[i + 1:]
    return f"(NUM, {word}) ", None


def isIDToken(word):
    global lex_err
    global lex_err_bool
    global symbol_num
    global IDs
    i = 0
    for ch in word:
        if ch.isalpha() or ch.isdigit():
            i += 1
            continue
        elif "+ - * = < / ; : , ( ) { } [ ]".__contains__(ch):
            if word[:i] in keyWords:
                return f"(KEYWORD, {word[:i]}) ", word[i:]
            if not word[:i] in IDs:
                IDs.append(word[:i])
                fs.writelines(f"{symbol_num}.\t{word[:i]}\n")
                symbol_num += 1
            return f"(ID, {word[:i]}) ", word[i:]
        else:
            lex_err += f"({word[:i + 1]}, Invalid input) "
            lex_err_bool = False
            return "", word[i + 1:]
    if word in keyWords:
        return f"(KEYWORD, {word}) ", None
    if not word in IDs:
        IDs.append(word)
        fs.writelines(f"{symbol_num}.\t{word}\n")
        symbol_num += 1
    return f"(ID, {word}) ", None


def isSymbolToken(word):
    global lex_err
    global lex_err_bool
    if len(word) == 1:
        return f"(SYMBOL, {word[0]}) ", None
    if word[0] in ["[", "]", "(", ")", "{", "}", ";", ":", ",", "<", "+", "-", "*", "/"]:
        return f"(SYMBOL, {word[0]}) ", word[1:]
    # more than just == is here       <= ... are here
    if word[0] == "=" and word[1] == "=":
        return f"(SYMBOL, {word[:2]}) ", word[2:]
    if word[0] in ["<", "=", "+", "-", "*", "/"] and (
            word[1].isalpha() or word[1].isdigit() or word[1] in ["[", "]", "(", ")", "{", "}", ";", ":", ",", "<",
                                                                  "=", "+", "-", "*", "/"]):
        return f"(SYMBOL, {word[0]}) ", word[1:]
    else:
        lex_err += f"({word[:2]}, Invalid input) "
        lex_err_bool = False
        return "", word[2:]


def commentToken(word):
    if word.startswith("//"):
        return "comment//", None
    else:
        return "comment/*", None


def tokenizer(word):
    global lex_err
    global lex_err_bool
    if len(word) == 0:
        return "", None
    if word[0].isdigit():
        return isNumToken(word)
    elif word.startswith("/*") or word.startswith("//"):
        return commentToken(word)
    elif word.startswith("*/"):
        lex_err_bool = False
        lex_err += "(*/, Unmatched comment)"
        return "", word[2:]
    elif word[0] in ["[", "]", "(", ")", "{", "}", ";", ":", "+", "-", "*", "=", "<", ",", "==", "/"]:
        return isSymbolToken(word)
    elif word[0].isalpha():
        return isIDToken(word)
    else:
        lex_err += f"({word[0]}, Invalid input) "
        lex_err_bool = False
        if len(word) == 1:
            return "", None
        return "", word[1:]


comment = 0
comment_start = ""
comment_start_loc = 0
for line in lines:
    lex_err += f"{i}.\t"
    line = line.replace("\n", "")
    line = line.replace("\t", "")
    line = line.replace("\v", "")
    line = line.replace("\f", "")
    line = line.replace("\r", "")
    lineStr = ""
    lex_err = ""
    lineWordsStr = ""
    words = line.split(" ")
    # print(words)
    for word in words:
        other = word
        if comment == 2:
            if word.__contains__("*/"):
                comment = 0
                str, other = tokenizer(word[word.index("*/") + 2:])
            else:
                continue
        while other != None:
            str, other = tokenizer(other)
            if str == "comment//":
                comment = 1
                break
            elif str == "comment/*":
                iii = line.index("/*")
                comment_start = line[iii:iii + 7]
                comment = 2
                comment_start_loc = i
                if word.__contains__("*/"):
                    comment = 0
                    str, other = tokenizer(word[word.index("*/") + 2:])
                else:
                    break

            lineWordsStr += str
        if comment == 1:
            comment = 0
            break
    lineStr += lineWordsStr
    if lineStr != "":
        lineStr = f"{i}.\t" + lineStr
        # ft.writelines(lineStr + "\n")
        ftstr += lineStr + "\n"
        # if str != "panic":
    if i == len(lines) and comment == 2:
        lex_err_bool = False
        lex_err += f"({comment_start}..., Unclosed comment)"
        lex_err = f"{comment_start_loc}.\t" + lex_err
        fl.writelines(lex_err + "\n")

        lex_err = ""
    elif lex_err != "":
        lex_err = f"{i}.\t" + lex_err
        fl.writelines(lex_err + "\n")
    i += 1

if lex_err_bool:
    fl.writelines("There is no lexical error.")

# ftstr = ftstr[:-2]
ftstr += f"{i}. (SYMBOL, $) (SYMBOL, $) \n"
ft.writelines(ftstr + "\n")
# print(ftstr)
fl.close()
fs.close()
ft.close()