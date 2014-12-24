import subprocess

from notspam import NotspamLearner, NotspamClassifier

class Learner(NotspamLearner):
    def __init__(self, meat):
        self.cmd = ["qsf", "-a"]
        if meat == 'spam':
            self.cmd += ['--mark-spam']
        elif meat == 'ham':
            self.cmd += ['--mark-nonspam']

    def add(self, msg):
        with open(msg.get_filename(), 'r') as f:
            proc = subprocess.Popen(self.cmd,
                                    stdin=f,
            )
            (stdout, stderr) = proc.communicate()
            ret = proc.wait()

    ########################################################

class Classifier(NotspamClassifier):

    def classify(self, msg):
        cmd = ["qsf",
               "-a",
               ]
        with open(msg.get_filename(), 'r') as f:
            proc = subprocess.Popen(cmd,
                                    stdin=f,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    )
            for line in proc.stdout:
                line = line.decode().split()
                if line[0] == 'X-Spam:':
                    print(line)
                    c = line[1]
                    break
            proc.communicate()
            ret = proc.wait()
        print(c)
        if c == 'YES':
            isspam = True
        elif c == 'NO':
            isspam = False
        else:
            isspam = None
        return isspam, ''
