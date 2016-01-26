import logging

class ColorFormatter(logging.Formatter):
    COLORS = {
        'RED' : '\033[91m',
        'GREEN' : '\033[92m',
        'YELLOW' : '\033[93m',
        'BLUE' : '\033[94m',
        'MAGENTA' : '\033[95m',
        'CYAN' : '\033[96m',
        'WHITE' : '\033[97m',
    }
    END_COLOR = '\033[0m'

    def __init__(self, format, use_color=True):
        logging.Formatter.__init__(self, format)
        self.use_color = use_color
        self.level_color_mapping = {
            'DEBUG' : self.COLORS['YELLOW'],
            'INFO' : self.COLORS['BLUE'],
            'WARNING' : self.COLORS['GREEN'],
            'CRITICAL' : self.COLORS['MAGENTA'],
            'ERROR' : self.COLORS['RED'],
            'EXCEPTION' : self.COLORS['RED'],
        }

    def format(self, record):
        levelname = record.levelname
        msg = logging.Formatter.format(self, record)
        if self.use_color:
            msg = self.level_color_mapping[levelname] + msg + self.END_COLOR
        return msg 


def getLogger(name, format=None):
    if not format:
        format = ('[%(levelname)-8s][%(name)-5s]  %(message)s -- ' +
                  '%(filename)s:%(lineno)d')

    if name not in getLogger.table:
        logger = logging.getLogger(name)
        formatter = ColorFormatter(format)
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)
        getLogger.table[name] = logger

    return getLogger.table[name]

getLogger.table = {}

if __name__ == '__main__':
    logger = getLogger(__name__)
    logger.debug('This is %s test', 'clogger')
    logger.info('This is %s test', 'clogger')
    logger.warning('This is %s test', 'clogger')
    logger.critical('This is %s test', 'clogger')
    logger.error('This is %s test', 'clogger')
    logger.setLevel(logging.DEBUG)
    logger.debug('This is %s test', 'clogger')
    logger.info('This is %s test', 'clogger')
    logger.warning('This is %s test', 'clogger')
    logger.critical('This is %s test', 'clogger')
    logger.error('This is %s test', 'clogger')

