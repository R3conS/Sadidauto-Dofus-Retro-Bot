"""Provides logging functionality."""

import datetime
import logging
import os


class Logger:
    """
    Holds methods related to logging.
    
    Methods
    ----------
    setup_logger()
        Create and return logger object.

    """

    # Creating master 'log' folder if it's missing from working 
    # directory.
    current_work_dir = os.getcwd()
    files_and_folders = os.listdir(current_work_dir)
    master_log_folder = "logs"
    if master_log_folder not in files_and_folders:
        os.mkdir(master_log_folder)

    # Logging levels.
    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @classmethod
    def __create_logger(cls, 
                        logger_name: str, 
                        log_level: int, 
                        stream_handler: bool):
        """
        Initialize and return instance of `logging.getLogger()`.

        Parameters
        ----------
        logger_name : str
            Name of logger.
        log_level : int
            Logging level. Available: NOTSET, DEBUG, INFO, WARNING, 
            ERROR, CRITICAL. Example: `log_level`=`Logger.DEBUG`.
        stream_handler : bool
            Print logs to console or not.

        Returns
        ----------
        logger : logging.getLogger()
            An instance of `logging.getLogger()`.

        """
        # Generating log file name.
        now = datetime.datetime.now()
        log_file_name = now.strftime("[%Y-%m-%d] Start - %Hh %Mm %Ss") + ".log"

        # Generating log folder path.
        folder_path = os.path.join(
                cls.current_work_dir,
                cls.master_log_folder,
                logger_name
            )

        # Creating log folder if it's missing.
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        # Creating the logger and configuring options.
        logger = logging.getLogger(logger_name)

        if not logger.hasHandlers():

            logger.setLevel(log_level)
            logger.propagate = False

            formatter_file = logging.Formatter(
                    "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
                )
            formatter_stream = logging.Formatter(
                    "%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s",
                    "%H:%M:%S"
                )
            
            file_handler = logging.FileHandler(
                    os.path.join(folder_path, log_file_name)
                )
            file_handler.setFormatter(formatter_file)
            logger.addHandler(file_handler)

            if stream_handler:
                s_handler = logging.StreamHandler()
                s_handler.setFormatter(formatter_stream)
                logger.addHandler(s_handler)

        return logger

    @classmethod
    def setup_logger(cls,
                     logger_name: str,
                     log_level: int,
                     stream_handler: bool):
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
        it's configurations (log_folder, log_file_name, log_level, 
        formatters, handlers).
        - Else initialize a new logger object using `__create_logger()` 
        with `logger_name` and `log_level` as arguments.

        Parameters
        ----------
        logger_name : str
            Name of logger. Also uses this name to create log folder
            if it's missing.
        log_level : int
            Logging level. Available: NOTSET, DEBUG, INFO, WARNING, 
            ERROR, CRITICAL. Example: `log_level`=`Logger.DEBUG`.
        stream_handler : bool
            Print logs to console or not.

        Returns
        ----------
        logger : logging.getLogger()
            An instance of `logging.getLogger()`.
        
        """
        all_loggers = logging.Logger.manager.loggerDict

        if logger_name in all_loggers:
            logger = logging.getLogger(logger_name)
            return logger
        else:
            logger = cls.__create_logger(logger_name,
                                         log_level,
                                         stream_handler)
            return logger
