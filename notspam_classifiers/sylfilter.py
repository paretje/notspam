from . import *

import subprocess

SYLFILTER_MAX_MESSAGES = 10000

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

        self.msgs = []

    def add(self, msg):
        self.msgs += [msg.get_filename()]
        # FIXME: why are we not catching errors here?

    def sync(self):
        for i in range(0, len(self.msgs), SYLFILTER_MAX_MESSAGES):
            subprocess.call(self.cmd + self.msgs[i:i+SYLFILTER_MAX_MESSAGES],
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
