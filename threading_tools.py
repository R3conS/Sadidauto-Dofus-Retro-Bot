"""Provides additional threading functionality."""

import threading


class ThreadingTools:
    """
    Holds custom threading methods.

    Methods
    ----------
    check_thread_status()
        Check if thread alive, dead or doesn't exist.
    wait_thread_start()
        Wait until thread starts.
    wait_thread_stop()
        Wait until thread stops.

    """

    def check_thread_status(self, 
                            thread_instance: type[threading.Thread]) \
                            -> str | None:
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

    def wait_thread_start(self, 
                          thread_instance: type[threading.Thread]) \
                          -> None:
        """
        Wait until thread starts.

        Parameters
        ----------
        thread_instance : type[threading.Thread]
            Instance of `threading.Thread` class.

        """
        success = False
        print(f"[INFO] Starting '{thread_instance}'!")
        while True:
            if success:
                print(f"[INFO] Started '{thread_instance}'!")
                break
            elif self.check_thread_status(thread_instance) == "ALIVE":
                success = True
            elif self.check_thread_status(thread_instance) == "DEAD":
                continue
            elif self.check_thread_status(thread_instance) is None:
                continue

    def wait_thread_stop(self, 
                         thread_instance: type[threading.Thread]) \
                         -> None:
        """
        Wait until thread stops.

        Parameters
        ----------
        thread_instance : type[threading.Thread]
            Instance of `threading.Thread` class.

        """
        success = False
        print(f"[INFO] Stopping '{thread_instance}'!")
        while True:
            if success:
                print(f"[INFO] Stopped '{thread_instance}'!")
                break
            elif self.check_thread_status(thread_instance) == "ALIVE":
                continue
            elif self.check_thread_status(thread_instance) == "DEAD":
                success = True
            elif self.check_thread_status(thread_instance) is None:
                success = True
