from os import listdir, getcwd, walk
from os.path import isfile, join


def countLinesInPath(path, directory):
    count = 0
    file = open(join(directory, path), encoding='utf8')
    for line in file:
        count += 1
    return count


def countLines(paths, directory):
    count = 0
    for path in paths:
        if path.find('.pyc') == -1 and path.find('__pycache__') == -1:
            count = count + countLinesInPath(path, directory)
    return count


def countIn(directory):
    count = 0
    for root, dirs, files in walk(directory):
        count += countLines(files, root)
    return count

if __name__ == '__main__':
    print('Total project lines length: {}'.format(countIn(getcwd()) - countLinesInPath(__file__, '')))