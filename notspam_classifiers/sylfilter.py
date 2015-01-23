from . import *

import subprocess

class Trainer(NotspamTrainer):
    def __init__(self, meat, retrain=False):
        self.cmd = ['sylfilter']
        if meat == 'spam':
            if retrain:
                self.cmd += ['-C']
            self.cmd += ['-j']
        elif meat == 'ham':
            if retrain:
                self.cmd += ['-J']
            self.cmd += ['-c']

    def add(self, msg):
        self.cmd += [msg.get_filename()]
        # FIXME: why are we not catching errors here?
        subprocess.call(self.cmd,
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
