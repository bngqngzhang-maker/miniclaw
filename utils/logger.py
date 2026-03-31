"""
日志工具
"""

import logging
import sys


def setup_logger(name: str = "miniclaw") -> logging.Logger:
    """设置日志器"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    ))
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger


default_logger = setup_logger()