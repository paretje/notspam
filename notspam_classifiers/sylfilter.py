from . import *

import subprocess

class Trainer(NotspamTrainer):
    def __init__(self, meat):
        if meat == 'spam':
            self.cmd = '-j'
        elif meat == 'ham':
            self.cmd = '-c'

    def add(self, msg):
        cmd = ['sylfilter',
               self.cmd,
               msg.get_filename(),
               ]
        subprocess.call(cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        )

class Classifier(NotspamClassifier):

    def classify(self, msg):
        cmd = ['sylfilter',
               '-t',
               msg.get_filename(),
               ]
        ret = subprocess.call(cmd,
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL
                              )
        if ret == 0:
            isspam = True
        elif ret == 1:
            isspam = False
        elif ret == 2:
            isspam = None
        else:
            # FIXME: raise error
            isspam = None
        return isspam, None
