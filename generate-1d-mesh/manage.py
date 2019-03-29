#!/usr/bin/env pytho

import logging

def get_logger_name():
    return 'generate-1d-mesh'

def init_logging():
    import logging
    logger = logging.getLogger(get_logger_name())
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(name)s] %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


