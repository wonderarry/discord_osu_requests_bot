import logging
from typing import Optional

def retrieve_logger(provided_name: Optional[str] = None) -> logging.Logger:
    
    logger = logging.getLogger(provided_name)
    
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        debug_handler = logging.FileHandler('../debug_logs.txt')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        logger.addHandler(debug_handler)
        
        
        important_handler = logging.FileHandler('../warning_logs.txt')
        important_handler.setLevel(logging.WARNING)
        important_handler.setFormatter(formatter)
        logger.addHandler(important_handler)
    
    return logger
        