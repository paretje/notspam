from . import *

import subprocess

class Trainer(NotspamTrainer):
    def __init__(self, meat):
        self.cmd = ["mailreaver.crm"]
        if meat == 'spam':
            self.cmd += ['--spam']
        elif meat == 'ham':
            self.cmd += ['--good']

    def add(self, msg):
        with open(msg.get_filename(), 'r') as f:
            try:
                subprocess.check_call(self.cmd,
                                      stdin=f,
                                      stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL,
                                  )
            except subprocess.CalledProcessError:
                raise NotspamTrainingError()

class Classifier(NotspamClassifier):
    def classify(self, msg):
        cmd = ["mailreaver.crm"]
        with open(msg.get_filename(), 'r') as f:
            proc = subprocess.Popen(cmd,
                                    stdin=f,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    )
            for line in proc.stdout:
                line = line.decode().split()
                if line[0] == 'X-CRM114-Status:':
                    c = line[1]
                    break
            proc.communicate()
            ret = proc.wait()
        if c == 'SPAM':
            isspam = True
        elif c == 'Good':
            isspam = False
        else:
            isspam = None
        return isspam, ''
