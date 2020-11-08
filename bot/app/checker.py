"""Thread function for regular check of glpi server
"""
import time
import config


def run_check():
    """Check for every user if it has updates
    """
    print("Do something")


def my_thread_func():
    """Thread function for regular check of glpi server
    """
    counter = 0
    while not config.WE_ARE_CLOSING:
        counter = (counter + 1) % config.CHECK_PERIOD
        if counter == 0:
            run_check()
        time.sleep(1)
