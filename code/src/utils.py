import logging
import time

start_time = time.time()


class ElapsedTimeFormatter(logging.Formatter):
    def format(self, record):
        elapsed = int(time.time() - start_time)
        minutes, seconds = divmod(elapsed, 60)
        record.elapsed = f"{minutes:02}:{seconds:02}"
        return super().format(record)


def setup_logging():
    # Basis-Logger konfigurieren (falls mehrfach aufgerufen, keine Duplikate)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Entferne ggf. alte Handler (wichtig bei mehrfachen Konfigurationen)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console Handler – nur INFO
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # File Handler – nur ERROR und höher
    file_handler = logging.FileHandler("error.log", mode="w")
    file_handler.setLevel(logging.ERROR)

    # Einheitliches Format
    formatter = ElapsedTimeFormatter("[%(elapsed)s] %(levelname)s: %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    # Handler hinzufügen
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def time_function(func):
    """
    Decorator to time a function.
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"Function {func.__name__:<40} took {elapsed_time:>8.4f} seconds")
        return result

    return wrapper


def format_dictionary(dictionary: dict, indention=1) -> str:
    """
    Formats the parameters for logging.
    """
    result = ""
    for key, value in dictionary.items():
        if type(value) is dict:
            value = format_dictionary(value, indention + 1)
        result += f"\n{'|' * indention}{key}: {value}"
    return result
