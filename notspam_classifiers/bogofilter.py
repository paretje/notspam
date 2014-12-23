from . import *

import subprocess

class Trainer(NotspamTrainer):
    def __init__(self, meat):
        self.cmd = ["bogofilter"]
        if meat == 'spam':
            self.cmd += '-s'
        elif meat == 'ham':
            self.cmd += '-n'

    def add(self, msg):
        with open(msg.get_filename(), 'r') as f:
            subprocess.check_call(self.cmd,
                                  stdin=f,
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL,
                              )

class Classifier(NotspamClassifier):
    def classify(self, msg):
        cmd = ["bogofilter",
               "-T",
               ]
        with open(msg.get_filename(), 'r') as f:
            proc = subprocess.Popen(cmd,
                                    stdin=f,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    )
            (stdout, stderr) = proc.communicate()
            ret = proc.wait()
        c, score = stdout.decode().strip().split(' ')
        if ret == 0:
            isspam = True
        elif ret == 1:
            isspam = False
        elif ret == 2:
            isspam = None
        else:
            raise NotspamClassifierFatalError()
        return isspam, score
