import time
import sys

class performance_tester:

    def __init__(self):
        self.checkin = time.time()

    def checkpoint(self,description):
        length = time.time() - self.checkin
        self.checkin = time.time()
        print('{} took {} seconds.'.format(description,length))
        sys.stdout.flush()
