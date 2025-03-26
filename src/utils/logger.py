# src/utils/logger.py
import logging
import sys

def setup_logger(name, level=logging.DEBUG):
    """
    Create a logger with console and file output
    
    :param name: Name of the logger
    :param level: Logging level
    :return: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create file handler
    file_handler = logging.FileHandler(f'{name}.log')
    file_handler.setLevel(level)
    
    # Create formatters
    console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Set formatters
    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger