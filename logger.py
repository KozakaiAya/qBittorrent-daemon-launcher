import datetime
import os

import utils

class Logger():
    def __init__(self):
        utils.safe_mkdir('./log/')

    def log(self, content):
        path = os.path.join('./log/', datetime.datetime.now().strftime("%Y%m%d"))
        utils.safe_mkdir(path)
        fn = os.path.join(path, datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.log')
        with open(fn, 'w') as f:
            f.write(content)
        

