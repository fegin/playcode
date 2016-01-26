from __future__ import print_function

def cprint(*args, **kwargs):
    if not hasattr(cprint, 'table'):
        cprint.table = {}
        cprint.table['RED'] = '\033[91m'
        cprint.table['GREEN'] = '\033[92m'
        cprint.table['YELLOW'] = '\033[93m'
        cprint.table['BLUE'] = '\033[94m'
        cprint.table['MAGENTA'] = '\033[95m'
        cprint.table['CYAN'] = '\033[96m'
        cprint.table['WHITE'] = '\033[97m'
        cprint.table['ENDC'] = '\033[0m'

    if 'color' in kwargs:
        color = kwargs['color']
        del kwargs['color']
    else:
        color = 'BLUE'
    color = color.upper()
    if color not in cprint.table:
        color = 'BLUE'

    print(cprint.table[color], end='')
    print(*args, **kwargs)
    print(cprint.table['ENDC'], end='')

if __name__ == '__main__':
    cprint('Test', color='RED')
    cprint('Test', color='BLUE')
    cprint('Test', color='GREEN')
    cprint('Test', color='YELLOW')
    cprint('Test', color='MAGENTA')
    cprint('Test', color='CYAN')
    cprint('Test', color='WHITE')
    print('Test')
