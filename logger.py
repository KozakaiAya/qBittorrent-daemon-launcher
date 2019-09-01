import datetime
import os
import sys

import utils

class Logger():
    def __init__(self):
        self.cur_path = sys.path[0]
        utils.safe_mkdir(os.path.join(self.cur_path, 'log/'))

    def log(self, content):
        path = os.path.join(self.cur_path, 'log/', datetime.datetime.now().strftime("%Y%m%d"))
        utils.safe_mkdir(path)
        fn = os.path.join(path, datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.log')
        with open(fn, 'w') as f:
            f.write(str(content))
        

