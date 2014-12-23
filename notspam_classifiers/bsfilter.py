from . import *

import subprocess

class Trainer(NotspamTrainer):
    def __init__(self, meat):
        self.cmd = ['bsfilter']
        if meat == 'spam':
            self.cmd += '-s'
        elif meat == 'ham':
            self.cmd += '-c'

    def add(self, msg):
        self.cmd += msg.get_filename()
        subprocess.call(self.cmd, stdout=subprocess.DEVNULL)

    def sync(self):
        cmd = ['bsfilter', '--update']
        subprocess.call(cmd)

class Classifier(NotspamClassifier):
    def classify(self, msg):
        cmd = ['bsfilter',
               msg.get_filename(),
               ]
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                )
        (stdout, stderr) = proc.communicate()
        ret = proc.wait()
        try:
            score = stdout.decode().strip().split(' ')[4]
        except:
            raise NotspamClassificationError('%s' % (stderr.decode()))
        if ret == 0:
            isspam = True
        elif ret == 1:
            isspam = False
        else:
            # FIXME: raise error?
            isspam = None
        return isspam, score
