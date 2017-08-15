from os import listdir, getcwd, walk
from os.path import isfile, join


def countLinesInPath(path, directory):
    line_count = 0
    char_count = 0
    file = open(join(directory, path), encoding='utf8')
    for line in file:
        line_count += 1
        char_count += len(line)
    return line_count, char_count


def countLines(paths, directory):
    line_count = 0
    char_count = 0
    for path in paths:
        if path[len(path)-3:len(path)] == '.py':
            lc, cc = countLinesInPath(path, directory)
            line_count += lc
            char_count += cc
    return line_count, char_count


def countIn(directory):
    line_count = 0
    char_count = 0
    for root, dirs, files in walk(directory):
        lc, cc = countLines(files, root)
        line_count += lc
        char_count += cc
    return line_count, char_count

if __name__ == '__main__':
    line_count_total, char_count_total = countIn(getcwd())
    line_count_this, char_count_this = countLinesInPath(__file__, '')
    line_count_cleaned = line_count_total - line_count_this
    char_count_cleaned = char_count_total - char_count_this

    print('Total project lines length: {}\nTotal project char length: {}'.format(line_count_cleaned,
                                                                                 char_count_cleaned))
