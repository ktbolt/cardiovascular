#!/usr/bin/env pytho

import logging

def get_logger_name():
    return 'generate-1d-mesh'

def init_logging():
    import logging
    logger = logging.getLogger(get_logger_name())
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler('generate_1d_mesh.log', mode="w")
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(name)s] %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

