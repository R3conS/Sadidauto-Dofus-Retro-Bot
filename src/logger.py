from datetime import datetime
import logging
import os


class Logger:
    
    # Creating master 'log' folder if it's missing.
    LOGS_DIR_PATH = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(LOGS_DIR_PATH):
        os.mkdir(LOGS_DIR_PATH)

    # Logging levels.
    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @classmethod
    def setup_logger(
            cls,
            logger_name: str,
            log_level: int,
            log_to_console: bool,
            log_to_file: bool
        ):
        """
        Create and return logger object.

        Also creates a unique log folder using `logger_name` if it
        doesn't exist already. Log files are named using current date
        and time.

        Usage
        ----------
        Make sure the object initialization is at the top of module,
        above all other imports.

        - If logging from one module:
            - Initialize logger object by calling `setup_logger()`.
        - If logging from multiple modules to same log file:
            - Initialize logger objects in wanted modules.
            - Set same `logger_name` across all objects.
        - If logging from multiple modules to separate log files:
            - Initialize logger objects in wanted modules.
            - Set different `logger_name` for each object.
        
        It is possible to log to an unlimited amount of different log 
        files with unique log folders. Just make sure to set a different 
        `logger_name` for each initialized logger object.

        Logic
        ----------
        - If `logger_name` already exists, get the logger with all of 
        it's configurations (log_folder, log_filename, log_level, 
        formatters, handlers).
        - Else initialize a new logger object using `_create_logger()`.

        Parameters
        ----------
        logger_name : str
            Name of logger. Also uses this name to create log folder
            if it's missing.
        log_level : int
            Logging level. Available: NOTSET, DEBUG, INFO, WARNING, 
            ERROR, CRITICAL. Example: `log_level`=`Logger.DEBUG`.
        log_to_console : bool
            Whether to log to the console.
        log_to_file : bool
            Whether to log to a file.

        Returns
        ----------
        logger : logging.getLogger()
            An instance of `logging.getLogger()`.
        
        """
        if logger_name in logging.Logger.manager.loggerDict:
            return logging.getLogger(logger_name)
        else:
            return cls._create_logger(
                logger_name,
                log_level, 
                log_to_console,
                log_to_file
            )

    @classmethod
    def _create_logger(
            cls, 
            logger_name: str, 
            log_level: int, 
            log_to_console: bool,
            log_to_file: bool
        ):
        """
        Initialize and return instance of `logging.getLogger()`.

        Parameters
        ----------
        logger_name : str
            Name of logger.
        log_level : int
            Logging level. Available: NOTSET, DEBUG, INFO, WARNING, 
            ERROR, CRITICAL. Example: `log_level`=`Logger.DEBUG`.
        log_to_console : bool
            Whether to log to the console..
        log_to_file : bool
            Whether to log to a file.

        Returns
        ----------
        logger : logging.getLogger()
            An instance of `logging.getLogger()`.

        """
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        logger.propagate = False
        if log_to_file:
            logger.addHandler(cls._create_file_handler(logger_name))
        if log_to_console:
            logger.addHandler(cls._create_stream_handler())
        return logger

    @classmethod
    def _create_file_handler(cls, logger_name):
        folder_path = os.path.join(cls.LOGS_DIR_PATH, logger_name)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        log_filename = datetime.now().strftime("[%Y-%m-%d] %H-%M-%S") + ".log"
        file_handler = logging.FileHandler(
            filename=os.path.join(folder_path, log_filename)
        )
        file_formatter = logging.Formatter(
            fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        return file_handler
    
    @classmethod
    def _create_stream_handler(cls):
        stream_formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s",
            datefmt="%H:%M:%S"
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(stream_formatter)
        return stream_handler
