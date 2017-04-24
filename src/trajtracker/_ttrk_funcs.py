
import time

import expyriment as xpy
import trajtracker as ttrk


#-------------------------------------------------
def log_write(msg, print_to_console=False):
    """
    Write a message to the log file
    
    :param msg: Text message 
    :param print_to_console: If true, print the message also to console 
    """

    xpy._internals.active_exp._event_file_log(msg, 1)

    if ttrk.log_to_console or print_to_console:
        t = time.time()
        stime = time.strftime('%H:%m:%S', time.localtime(t)) + "{:.3f}".format(t % 1)[1:]
        print(stime + ": " + msg)
