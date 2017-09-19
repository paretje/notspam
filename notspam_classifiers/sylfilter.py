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

        self.__proc = subprocess.Popen(['xargs'] + self.cmd,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL,
                                       )

    def add(self, msg):
        # write the message file paths to process stdin
        path = msg.get_filename()
        self.__proc.stdin.write(bytes(path + '\n', 'UTF-8'))

    def sync(self):
        # FIXME: why are we not catching errors here?
        self.__proc.communicate()
        ret = self.__proc.wait()

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
