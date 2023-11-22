"""Provides additional threading functionality."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)


class ThreadingTools:
    """
    Holds custom threading methods.

    Methods
    ----------
    wait_thread_start()
        Wait until thread starts.
    wait_thread_stop()
        Wait until thread stops.
    check_thread_status()
        Check if thread alive, dead or doesn't exist.

    """

    @classmethod
    def wait_thread_start(cls, thread_instance):
        """
        Wait until thread starts.

        Parameters
        ----------
        thread_instance : type[threading.Thread]
            Instance of `threading.Thread` class.

        """
        success = False
        log.info(f"Starting '{thread_instance}'!")
        while True:
            if success:
                log.info(f"Started '{thread_instance}'!")
                break
            elif cls.check_thread_status(thread_instance) == "ALIVE":
                success = True
            elif cls.check_thread_status(thread_instance) == "DEAD":
                continue
            elif cls.check_thread_status(thread_instance) is None:
                continue

    @classmethod
    def wait_thread_stop(cls, thread_instance):
        """
        Wait until thread stops.

        Parameters
        ----------
        thread_instance : type[threading.Thread]
            Instance of `threading.Thread` class.

        """
        success = False
        log.info(f"Stopping '{thread_instance}'!")
        while True:
            if success:
                log.info(f"Stopped '{thread_instance}'!")
                break
            elif cls.check_thread_status(thread_instance) == "ALIVE":
                continue
            elif cls.check_thread_status(thread_instance) == "DEAD":
                success = True
            elif cls.check_thread_status(thread_instance) is None:
                success = True

    @staticmethod
    def check_thread_status(thread_instance):
        """
        Check if thread alive, dead or doesn't exist.

        Parameters
        ----------
        thread_instance : type[threading.Thread]
            Instance of `threading.Thread` class.

        Returns
        ----------
        None : NoneType
            If `thread_instance` is `None`.
        "ALIVE" : str
            If `thread_instance.is_alive()` is `True`.
        "DEAD" : str
            If `thread_instance.is_alive()` is `False`.

        """
        if thread_instance.is_alive():
            return "ALIVE"
        elif not thread_instance.is_alive():
            return "DEAD"
        else:
            return None
