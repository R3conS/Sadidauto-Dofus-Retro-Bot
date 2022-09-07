class Threading_Tools:


    def __init__(self):
        pass


    # Checks status of a specified thread.
    def check_thread_status_alive_OR_dead(self, thread_name):

        if thread_name is None:
            return None
        elif thread_name.is_alive():
            return "ALIVE"
        elif not thread_name.is_alive():
            return "DEAD"


    # Forces program to wait until the thread is started.
    def wait_for_thread_to_start(self, thread_name):

        success = False

        print(f"[INFO] Starting '{thread_name}'!")

        while True:

            if success:
                print(f"[INFO] Started '{thread_name}'!")
                break
            elif self.check_thread_status_alive_OR_dead(thread_name) == "ALIVE":
                success = True
            elif self.check_thread_status_alive_OR_dead(thread_name) == "DEAD":
                continue
            elif self.check_thread_status_alive_OR_dead(thread_name) is None:
                continue


    # Forces program to wait until the thread is stopped.
    def wait_for_thread_to_stop(self, thread_name):

        success = False

        print(f"[INFO] Stopping '{thread_name}'!")

        while True:

            if success:
                print(f"[INFO] Stopped '{thread_name}'!")
                break
            elif self.check_thread_status_alive_OR_dead(thread_name) == "ALIVE":
                continue
            elif self.check_thread_status_alive_OR_dead(thread_name) == "DEAD":
                success = True
            elif self.check_thread_status_alive_OR_dead(thread_name) is None:
                success = True
