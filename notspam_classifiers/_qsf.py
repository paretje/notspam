import subprocess

from notspam import NotspamLearner, NotspamClassifier

class Learner(NotspamLearner):
    def __init__(self, meat):
        self.cmd = ["qsf", "-a"]
        if meat == 'spam':
            self.cmd += '--mark-spam'
        elif meat == 'ham':
            self.cmd += '--mark-nonspam'

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
            (stdout, stderr) = proc.communicate()
            ret = proc.wait()
        return
        return isspam, '%s/%s' % (float(score), float(threshold))
