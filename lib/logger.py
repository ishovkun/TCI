import logging

logger = logging.getLogger()
formatter = logging.Formatter(
        '%(levelname)-8s %(module)-20s %(funcName)-20s  %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler('TCI.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.setLevel(logging.DEBUG)
